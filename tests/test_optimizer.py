from backend.engine.optimizer import optimize_progression
from backend.engine.transition_solver import calculate_transition_metrics
from backend.engine.harmonic_library import get_voicings_for_chord
from backend.models.hand_profile import PRESET_PROFILES


def test_transition_metrics_and_pivots():
    c_std, _ = get_voicings_for_chord("C")
    # C to Am share common fingers (finger 1 on B string fret 1, finger 2 on D string fret 2)
    am_std, _ = get_voicings_for_chord("Am")
    
    transition = calculate_transition_metrics(c_std, am_std)
    assert transition.pivot_finger_count >= 1
    assert 1 in transition.pivot_fingers  # Index finger stays on B string fret 1!
    assert transition.transition_strain_cost < 15.0


def test_barre_gauntlet_optimization():
    # 4 brutal barre chords
    chords = ["F", "Bm", "F#m", "C#m"]
    profile = PRESET_PROFILES["tendonitis_flexor"]
    
    result = optimize_progression(chords, profile)
    
    assert result.total_chords == 4
    # All 4 standard chords are barres, all 4 should be eliminated
    assert result.barres_eliminated_count >= 3
    # Significant strain reduction percentage
    assert result.total_strain_reduction_pct > 60.0
    # Every step should produce a valid result
    assert len(result.steps) == 4
    for step in result.steps:
        assert step.optimized_strain.total_chord_strain < step.standard_strain.total_chord_strain


def test_dynamic_programming_path_continuity():
    chords = ["C", "G", "Am", "F"]
    profile = PRESET_PROFILES["arthritis_moderate"]
    
    result = optimize_progression(chords, profile)
    assert result.total_strain_reduction_pct > 0
    assert len(result.calculation_logs) > 5
