import uuid
from typing import Dict, List, Optional, Tuple
from backend.models.chord import ChordVoicing
from backend.models.hand_profile import HandProfile, PRESET_PROFILES
from backend.models.telemetry import (
    BiomechanicalStrainBreakdown,
    TransitionMetrics,
    ChordStepResult,
    OptimizationTelemetry
)
from backend.engine.music_theory import (
    parse_chord_string,
    format_chord_display,
    get_notes_for_chord,
    NOTE_TO_SEMITONE
)
from backend.engine.harmonic_library import get_voicings_for_chord
from backend.engine.biomechanics import evaluate_chord_biomechanics
from backend.engine.transition_solver import calculate_transition_metrics


def calculate_harmonic_fidelity_penalty(raw_chord_name: str, voicing: ChordVoicing) -> float:
    """
    Evaluates harmonic fidelity to guarantee that the Easy shape sounds virtually
    identical to the requested standard chord.
    
    Penalizes:
    - Missing essential chord tones (Root and 3rd)
    - Unauthorized 7ths, 9ths, or 6ths added to pure major/minor triads
    - Missing 7ths when explicitly requested
    - Non-root bass notes
    """
    root, quality = parse_chord_string(raw_chord_name)
    norm_root = root[0].upper() + (root[1:].lower() if len(root) > 1 else "")
    root_pc = NOTE_TO_SEMITONE.get(norm_root, 0)
    
    target_notes = get_notes_for_chord(norm_root, quality)
    target_pcs = set(NOTE_TO_SEMITONE[n] for n in target_notes)
    
    voicing_pcs = set()
    lowest_pc = None
    
    for s_idx, f in enumerate(voicing.frets):
        if f >= 0 and s_idx < len(voicing.notes):
            n = voicing.notes[s_idx]
            if n != "X":
                letter = n[:-1] if len(n) > 1 and n[-1].isdigit() else n
                norm_letter = letter[0].upper() + (letter[1:].lower() if len(letter) > 1 else "")
                pc = NOTE_TO_SEMITONE.get(norm_letter, 0)
                voicing_pcs.add(pc)
                if lowest_pc is None:
                    lowest_pc = pc
                    
    penalty = 0.0
    
    # 1. Missing Root
    if root_pc not in voicing_pcs:
        penalty += 8.0
        
    # 2. Check 3rd for major and minor triads
    third_interval = 4 if quality in ["major", "maj", ""] else (3 if "min" in quality or quality == "m" else None)
    if third_interval is not None:
        target_third_pc = (root_pc + third_interval) % 12
        if target_third_pc not in voicing_pcs:
            penalty += 6.5
            
    # 3. Check 7th if explicitly requested
    is_7th_requested = any(q in quality for q in ["7", "maj7", "min7", "m7"])
    if is_7th_requested:
        seventh_interval = 11 if "maj7" in quality else 10
        target_seventh_pc = (root_pc + seventh_interval) % 12
        if target_seventh_pc not in voicing_pcs:
            penalty += 5.0
    else:
        # Penalize adding unrequested 7ths, 9ths, or 6ths to pure triads
        unrequested_7_dom = (root_pc + 10) % 12
        unrequested_7_maj = (root_pc + 11) % 12
        unrequested_9 = (root_pc + 2) % 12
        unrequested_6 = (root_pc + 9) % 12
        
        if unrequested_7_maj in voicing_pcs:
            penalty += 5.0
        if unrequested_7_dom in voicing_pcs:
            penalty += 5.0
        if unrequested_9 in voicing_pcs and quality not in ["add9", "sus2", "9"]:
            penalty += 4.0
        if unrequested_6 in voicing_pcs and quality != "6":
            penalty += 4.0
            
    # 4. Bass note preference (slight preference for root in the bass)
    if lowest_pc is not None and lowest_pc != root_pc:
        penalty += 1.0
        
    return penalty


def optimize_progression(
    chord_names: List[str],
    profile: Optional[HandProfile] = None
) -> OptimizationTelemetry:
    """
    Core algorithmic engine: performs dynamic programming (Viterbi path search)
    over a multi-stage trellis graph to find the globally minimal strain sequence of voicings.
    
    Trellis Stage t: chord_names[t]
    Nodes in Stage t: [standard_voicing] + [alternative_voicings]
    Edge weight (V_t, V_{t+1}): TransitionCost(V_t, V_{t+1})
    Node weight V_t: StaticStrain(V_t, profile)
    """
    if profile is None:
        profile = PRESET_PROFILES["arthritis_moderate"]
        
    logs: List[str] = []
    logs.append(f"Ergonomic Engine Initialized with Hand Profile: '{profile.name}'")
    logs.append(f"Active Constraints: Max Span: {profile.max_fret_span} frets | Ban Barres: {profile.ban_barres} | Open Drones: {profile.prefer_open_drones}")
    logs.append(f"Parsing chord progression of {len(chord_names)} steps: {' -> '.join(chord_names)}")
    
    # 1. Collect candidates for each step
    stages: List[List[Tuple[ChordVoicing, BiomechanicalStrainBreakdown]]] = []
    baseline_voicings: List[Tuple[ChordVoicing, BiomechanicalStrainBreakdown]] = []
    
    for idx, raw_name in enumerate(chord_names):
        standard, alts = get_voicings_for_chord(raw_name)
        std_strain = evaluate_chord_biomechanics(standard, profile)
        baseline_voicings.append((standard, std_strain))
        
        # Build candidate pool: include standard plus all viable alternatives
        candidate_pool = [standard] + alts
        valid_candidates: List[Tuple[ChordVoicing, BiomechanicalStrainBreakdown]] = []
        
        pruned_count = 0
        for cand in candidate_pool:
            strain = evaluate_chord_biomechanics(cand, profile)
            # Prune candidates that strictly violate hard rules if alternatives exist
            if profile.ban_barres and strain.is_barre_active and len(alts) > 0:
                pruned_count += 1
                continue
            if strain.fret_span > profile.max_fret_span and len(alts) > 0:
                pruned_count += 1
                continue
            valid_candidates.append((cand, strain))
            
        # Fallback if all were pruned
        if not valid_candidates:
            valid_candidates.append((candidate_pool[0], evaluate_chord_biomechanics(candidate_pool[0], profile)))
            
        stages.append(valid_candidates)
        logs.append(f"Step {idx + 1} ({raw_name}): Deconstructed harmonic tension; evaluated {len(candidate_pool)} shapes, pruned {pruned_count} high-torque candidates.")

    # 2. Dynamic Programming Trellis Solver (Viterbi Shortest Path)
    # Viterbi table: dp[stage][cand_idx] = (min_cumulative_cost, prev_cand_idx)
    num_stages = len(stages)
    dp: List[List[Tuple[float, int]]] = []
    
    # Initialize stage 0 with static biomechanical strain + harmonic fidelity penalty
    dp.append([
        (strain.total_chord_strain + calculate_harmonic_fidelity_penalty(chord_names[0], cand), -1)
        for (cand, strain) in stages[0]
    ])
    
    LAMBDA_TRANSITION = 1.35  # Transition weight relative to static chord strain
    
    logs.append("Executing Dynamic Programming Viterbi recurrence over voice-leading trellis...")
    for t in range(1, num_stages):
        stage_dp: List[Tuple[float, int]] = []
        curr_candidates = stages[t]
        prev_candidates = stages[t - 1]
        
        for curr_idx, (curr_v, curr_strain) in enumerate(curr_candidates):
            best_cost = float('inf')
            best_prev_idx = -1
            harmonic_cost = calculate_harmonic_fidelity_penalty(chord_names[t], curr_v)
            
            for prev_idx, (prev_v, _) in enumerate(prev_candidates):
                prev_cumulative = dp[t - 1][prev_idx][0]
                transition = calculate_transition_metrics(prev_v, curr_v)
                
                # Dynamic cost calculation with harmonic fidelity protection
                total_step_cost = (
                    prev_cumulative
                    + curr_strain.total_chord_strain
                    + (transition.transition_strain_cost * LAMBDA_TRANSITION)
                    + harmonic_cost
                )
                
                if total_step_cost < best_cost:
                    best_cost = total_step_cost
                    best_prev_idx = prev_idx
                    
            stage_dp.append((best_cost, best_prev_idx))
        dp.append(stage_dp)
        
    # 3. Backtrack optimal path
    best_last_idx = 0
    min_final_cost = float('inf')
    for idx, (cost, _) in enumerate(dp[-1]):
        if cost < min_final_cost:
            min_final_cost = cost
            best_last_idx = idx
            
    optimal_path_indices = [best_last_idx]
    for t in range(num_stages - 1, 0, -1):
        prev_idx = dp[t][optimal_path_indices[-1]][1]
        optimal_path_indices.append(prev_idx)
    optimal_path_indices.reverse()
    
    logs.append("Viterbi path converged. Reconstructed global minimum-torque trajectory.")
    
    # 4. Assemble Results and Telemetry Comparison
    steps: List[ChordStepResult] = []
    
    baseline_total_strain = sum(std_s.total_chord_strain for (_, std_s) in baseline_voicings)
    optimized_total_strain = 0.0
    
    baseline_total_travel = 0.0
    optimized_total_travel = 0.0
    
    barres_eliminated = 0
    open_strings_gained = 0
    
    total_span_before = 0
    total_span_after = 0
    
    for t in range(num_stages):
        std_v, std_strain = baseline_voicings[t]
        opt_v, opt_strain = stages[t][optimal_path_indices[t]]
        
        optimized_total_strain += opt_strain.total_chord_strain
        
        total_span_before += std_strain.fret_span
        total_span_after += opt_strain.fret_span
        
        if std_strain.is_barre_active and not opt_strain.is_barre_active:
            barres_eliminated += 1
            
        std_open = sum(1 for f in std_v.frets if f == 0)
        opt_open = sum(1 for f in opt_v.frets if f == 0)
        if opt_open > std_open:
            open_strings_gained += (opt_open - std_open)
            
        # Transition metrics
        opt_transition: Optional[TransitionMetrics] = None
        if t > 0:
            prev_opt_v, _ = stages[t - 1][optimal_path_indices[t - 1]]
            opt_transition = calculate_transition_metrics(prev_opt_v, opt_v)
            optimized_total_travel += opt_transition.finger_travel_distance
            
            prev_std_v, _ = baseline_voicings[t - 1]
            std_transition = calculate_transition_metrics(prev_std_v, std_v)
            baseline_total_travel += std_transition.finger_travel_distance
            
        # Strain reduction percentage for this individual chord
        strain_diff = std_strain.total_chord_strain - opt_strain.total_chord_strain
        step_reduction = (strain_diff / std_strain.total_chord_strain * 100.0) if std_strain.total_chord_strain > 0 else 0.0
        step_reduction = round(max(0.0, step_reduction), 1)
        
        steps.append(ChordStepResult(
            step_index=t,
            requested_chord=chord_names[t],
            standard_voicing=std_v,
            standard_strain=std_strain,
            optimized_voicing=opt_v,
            optimized_strain=opt_strain,
            strain_reduction_pct=step_reduction,
            transition_from_prev=opt_transition
        ))
        
    overall_strain_red = 0.0
    if baseline_total_strain > 0:
        overall_strain_red = round(((baseline_total_strain - optimized_total_strain) / baseline_total_strain) * 100.0, 1)
        
    overall_travel_red = 0.0
    if baseline_total_travel > 0:
        overall_travel_red = round(((baseline_total_travel - optimized_total_travel) / baseline_total_travel) * 100.0, 1)
        
    logs.append(f"Global Optimization Complete: {overall_strain_red}% hand strain reduction, {barres_eliminated} barre chords eliminated.")
    
    return OptimizationTelemetry(
        progression_id=str(uuid.uuid4())[:8],
        total_chords=num_stages,
        profile_used=profile.name,
        baseline_total_strain=round(baseline_total_strain, 2),
        optimized_total_strain=round(optimized_total_strain, 2),
        total_strain_reduction_pct=max(0.0, overall_strain_red),
        baseline_total_travel=round(baseline_total_travel, 1),
        optimized_total_travel=round(optimized_total_travel, 1),
        travel_reduction_pct=max(0.0, overall_travel_red),
        barres_eliminated_count=barres_eliminated,
        open_strings_gained_count=open_strings_gained,
        avg_span_before=round(total_span_before / max(1, num_stages), 1),
        avg_span_after=round(total_span_after / max(1, num_stages), 1),
        steps=steps,
        calculation_logs=logs
    )
