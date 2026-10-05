import math
from typing import List, Tuple
from backend.models.chord import ChordVoicing
from backend.models.hand_profile import HandProfile
from backend.models.telemetry import BiomechanicalStrainBreakdown


def calculate_fret_span(frets: List[int]) -> Tuple[int, int, int]:
    """
    Calculates (span, min_fret, max_fret) for all actively fretted strings (fret > 0).
    Returns (0, 0, 0) if no fretted notes (e.g. all open or muted).
    """
    fretted = [f for f in frets if f > 0]
    if not fretted:
        return (0, 0, 0)
    min_f = min(fretted)
    max_f = max(fretted)
    # Span is the difference between max and min plus 1 fret positions,
    # or span = max_f - min_f. In guitar ergonomics, min=1 and max=3 is a 2-fret reach span.
    span = max_f - min_f
    return (span, min_f, max_f)


def calculate_barre_clamping(voicing: ChordVoicing) -> Tuple[bool, int, float]:
    """
    Determines if an index (or other finger) barre is active and computes isometric clamping torque.
    Returns (is_barre, strings_clamped, base_torque).
    """
    if voicing.barres:
        max_clamped = max(len(b.strings) for b in voicing.barres)
        is_barre = max_clamped >= 2
        # Torque increases rapidly with number of clamped strings
        if max_clamped >= 6:
            torque = 11.5
        elif max_clamped == 5:
            torque = 8.5
        elif max_clamped == 4:
            torque = 5.5
        elif max_clamped >= 2:
            torque = 2.5
        else:
            torque = 0.0
        return (is_barre, max_clamped, torque)
    
    # Fallback inspection of fingers: if index finger (1) appears on 3 or more strings at the same fret
    fret_by_f1 = [voicing.frets[i] for i, f in enumerate(voicing.fingers) if f == 1 and voicing.frets[i] > 0]
    if len(fret_by_f1) >= 2 and len(set(fret_by_f1)) == 1:
        count = len(fret_by_f1)
        torque = 11.5 if count >= 6 else (8.5 if count == 5 else (5.5 if count == 4 else 2.5))
        return (True, count, torque)
    
    return (False, 0, 0.0)


def evaluate_chord_biomechanics(voicing: ChordVoicing, profile: HandProfile) -> BiomechanicalStrainBreakdown:
    """
    Evaluates the static physiological load and torque on the human hand for a given chord voicing.
    Incorporates:
    - Fret span exponential penalty
    - Barre chord isometric torque friction
    - Digit-specific strain (pinky bass reach, index clamp sensitivity)
    - Open string relaxation bonus
    - Profile constraints (banned barres, max fret span limits)
    """
    frets = voicing.frets
    fingers = voicing.fingers
    
    span, min_fret, max_fret = calculate_fret_span(frets)
    voicing.fret_span = span
    
    # 1. Fret Span Penalty
    span_penalty = 0.0
    if span <= 1:
        span_penalty = 0.15 * span
    elif span == 2:
        span_penalty = 0.45
    elif span == 3:
        span_penalty = 1.2
    else:  # span >= 4
        span_penalty = 2.5 * math.exp(1.2 * (span - 3))
    
    # Strict profile max span limit penalty
    if span > profile.max_fret_span:
        span_penalty += 35.0 * (span - profile.max_fret_span)
    
    # 2. Barre Chord Isometric Torque Penalty
    is_barre, barre_count, base_torque = calculate_barre_clamping(voicing)
    barre_torque_penalty = base_torque * profile.index_clamp_sensitivity
    
    if profile.ban_barres and is_barre:
        # User strictly banned barres (e.g., severe arthritis or tendonitis)
        barre_torque_penalty += 80.0
        
    # 3. Digit-Specific Torque & Fatigue Constraints
    digit_fatigue_penalty = 0.0
    pinky_reach_penalty = 0.0
    
    for str_idx, (fret, finger) in enumerate(zip(frets, fingers)):
        if fret <= 0 or finger <= 0:
            continue
            
        # Base finger weight
        if finger == 1:
            digit_fatigue_penalty += 0.2
        elif finger == 2:
            digit_fatigue_penalty += 0.3
        elif finger == 3:
            digit_fatigue_penalty += 0.6
        elif finger == 4:
            # Pinky has higher biomechanical strain
            base_pinky = 1.5
            # Factor in user's pinky mobility restriction
            restriction = profile.pinky_restriction
            if restriction <= 0.05:
                # Pinky forbidden
                digit_fatigue_penalty += 60.0
            else:
                digit_fatigue_penalty += base_pinky + (1.0 - restriction) * 6.0
                
            # Pinky on low bass strings (str 0 = Low E, str 1 = A) causes extreme wrist flexion & tendon shear
            if str_idx in [0, 1]:
                shear = 4.0 * profile.wrist_flexion_limit
                pinky_reach_penalty += shear
            elif str_idx == 2 and fret > 3:
                pinky_reach_penalty += 2.0 * profile.wrist_flexion_limit

    # 4. Open Resonant String Bonus
    open_count = sum(1 for f in frets if f == 0)
    open_bonus_per_string = 0.75 if profile.prefer_open_drones else 0.4
    open_string_bonus = open_count * open_bonus_per_string
    
    # 5. Composite Total Score (Lower is better)
    total_strain = span_penalty + barre_torque_penalty + digit_fatigue_penalty + pinky_reach_penalty - open_string_bonus
    total_strain = max(0.1, round(total_strain, 2))
    
    # 6. Formatting fingering notation
    notation_parts = []
    for f, fing in zip(frets, fingers):
        if f < 0:
            notation_parts.append("x")
        elif f == 0:
            notation_parts.append("0")
        else:
            notation_parts.append(str(fing) if fing > 0 else str(f))
    fingering_notation = "-".join(notation_parts)
    
    return BiomechanicalStrainBreakdown(
        span_penalty=round(span_penalty, 2),
        barre_torque_penalty=round(barre_torque_penalty, 2),
        digit_fatigue_penalty=round(digit_fatigue_penalty, 2),
        pinky_reach_penalty=round(pinky_reach_penalty, 2),
        open_string_bonus=round(open_string_bonus, 2),
        total_chord_strain=total_strain,
        is_barre_active=is_barre,
        barre_strings_count=barre_count,
        fret_span=span,
        fingering_notation=fingering_notation
    )
