from backend.engine.biomechanics import (
    calculate_fret_span,
    calculate_barre_clamping,
    evaluate_chord_biomechanics
)
from backend.engine.harmonic_library import get_voicings_for_chord
from backend.models.hand_profile import PRESET_PROFILES, HandProfile


def test_fret_span_calculation():
    # Open C: [-1, 3, 2, 0, 1, 0] -> Fretted: [3, 2, 1] -> Span = 3 - 1 = 2
    span, min_f, max_f = calculate_fret_span([-1, 3, 2, 0, 1, 0])
    assert span == 2
    assert min_f == 1
    assert max_f == 3
    
    # 4-fret span stretch
    span, min_f, max_f = calculate_fret_span([1, 5, -1, -1, -1, -1])
    assert span == 4


def test_barre_detection_and_torque():
    f_std, f_alts = get_voicings_for_chord("F")
    is_barre, count, torque = calculate_barre_clamping(f_std)
    assert is_barre is True
    assert count == 6
    assert torque >= 10.0
    
    # Check open alternative
    f_maj7 = f_alts[0]
    is_barre_alt, count_alt, torque_alt = calculate_barre_clamping(f_maj7)
    assert is_barre_alt is False
    assert count_alt == 0
    assert torque_alt == 0.0


def test_biomechanical_strain_comparison():
    profile = PRESET_PROFILES["arthritis_moderate"]
    
    f_std, f_alts = get_voicings_for_chord("F")
    std_strain = evaluate_chord_biomechanics(f_std, profile)
    
    # Standard F barre should have huge strain under arthritis profile due to banned barres
    assert std_strain.is_barre_active is True
    assert std_strain.barre_torque_penalty > 50.0
    assert std_strain.total_chord_strain > 80.0
    
    # Alternative Fmaj7 should have low strain
    f_maj7 = f_alts[0]
    alt_strain = evaluate_chord_biomechanics(f_maj7, profile)
    assert alt_strain.is_barre_active is False
    assert alt_strain.barre_torque_penalty == 0.0
    assert alt_strain.total_chord_strain < 10.0
    assert alt_strain.total_chord_strain < std_strain.total_chord_strain


def test_pinky_restriction_penalty():
    dystonia_profile = PRESET_PROFILES["dystonia_pinky"]
    # Chord using pinky heavily
    c7_std, _ = get_voicings_for_chord("C7")
    strain = evaluate_chord_biomechanics(c7_std, dystonia_profile)
    # Pinky restriction is 0.0, so using pinky incurs huge penalty
    assert strain.digit_fatigue_penalty > 50.0
