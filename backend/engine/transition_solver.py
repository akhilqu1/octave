import math
from typing import Dict, List, Optional, Tuple
from backend.models.chord import ChordVoicing
from backend.models.telemetry import TransitionMetrics


STRING_SPACING_MM = 10.5  # Typical standard guitar bridge/nut string spacing ~10.5mm
FRET_SPACING_MM = 22.0    # Average fret-to-fret physical distance on guitar neck ~22mm
PIVOT_REWARD_DISCOUNT = 3.5  # Relief granted when a finger does not have to lift or move


def get_finger_locations(voicing: ChordVoicing) -> Dict[int, Tuple[int, int]]:
    """
    Returns mapping {finger_id: (string_idx, fret)} for all fretted notes.
    Fingers are 1 (index), 2 (middle), 3 (ring), 4 (pinky), -1 (thumb).
    """
    locs: Dict[int, Tuple[int, int]] = {}
    for str_idx, (fret, finger) in enumerate(zip(voicing.frets, voicing.fingers)):
        if fret > 0 and finger > 0:
            # If multiple strings are clamped by same finger (barre), store the primary anchor
            if finger not in locs:
                locs[finger] = (str_idx, fret)
    return locs


def calculate_hand_center_fret(voicing: ChordVoicing) -> float:
    """Calculates the center of mass fret position for the fretting hand."""
    fretted = [f for f in voicing.frets if f > 0]
    if not fretted:
        return 0.0
    return sum(fretted) / len(fretted)


def calculate_transition_metrics(chord_a: ChordVoicing, chord_b: ChordVoicing) -> TransitionMetrics:
    """
    Evaluates dynamic physical movement and strain when moving from chord_a to chord_b.
    Calculates:
    - Individual finger 2D travel vectors (string displacement + fret displacement)
    - Identification of static pivot/anchor fingers
    - Hand center longitudinal shift along neck
    - Dynamic transition cost
    """
    locs_a = get_finger_locations(chord_a)
    locs_b = get_finger_locations(chord_b)
    
    total_travel_mm = 0.0
    pivot_fingers: List[int] = []
    
    # Check all 4 standard playing digits (1 to 4)
    all_fingers = {1, 2, 3, 4}
    
    for f in all_fingers:
        pos_a = locs_a.get(f)
        pos_b = locs_b.get(f)
        
        if pos_a is not None and pos_b is not None:
            if pos_a == pos_b:
                # Pivot finger: exact same string and fret!
                pivot_fingers.append(f)
            else:
                str_delta = abs(pos_a[0] - pos_b[0]) * STRING_SPACING_MM
                fret_delta = abs(pos_a[1] - pos_b[1]) * FRET_SPACING_MM
                disp = math.sqrt(str_delta ** 2 + fret_delta ** 2)
                total_travel_mm += disp
        elif pos_a is None and pos_b is not None:
            # Finger placed from hovering
            total_travel_mm += 18.0  # nominal landing displacement
        elif pos_a is not None and pos_b is None:
            # Finger released to hover
            total_travel_mm += 14.0  # nominal release displacement

    # Hand center displacement along neck
    center_a = calculate_hand_center_fret(chord_a)
    center_b = calculate_hand_center_fret(chord_b)
    shift_frets = abs(center_a - center_b)
    shift_cost_mm = shift_frets * FRET_SPACING_MM
    
    # Pivot discount: each anchor finger dramatically reduces re-orienting friction
    pivot_relief = len(pivot_fingers) * PIVOT_REWARD_DISCOUNT
    
    # Dynamic transition strain cost
    raw_cost = (total_travel_mm * 0.04) + (shift_cost_mm * 0.03) - pivot_relief
    transition_cost = max(0.0, round(raw_cost, 2))
    
    return TransitionMetrics(
        finger_travel_distance=round(total_travel_mm, 1),
        pivot_finger_count=len(pivot_fingers),
        pivot_fingers=pivot_fingers,
        hand_shift_frets=round(shift_frets, 2),
        transition_strain_cost=transition_cost
    )
