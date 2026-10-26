from typing import Dict, List, Optional, Tuple, Any
from backend.engine.music_theory import (
    parse_chord_string,
    NOTE_TO_SEMITONE,
    PITCH_CLASSES_SHARP,
    PITCH_CLASSES_FLAT
)
from backend.engine.harmonic_library import get_voicings_for_chord
from backend.engine.biomechanics import evaluate_chord_biomechanics
from backend.models.hand_profile import HandProfile, PRESET_PROFILES


OPEN_COWBOY_KEYS = {
    "C", "G", "D", "A", "E",
    "Am", "Em", "Dm",
    "A7", "E7", "D7", "G7", "C7", "B7",
    "Cmaj7", "Amaj7", "Dmaj7", "Gmaj7",
    "Am7", "Em7", "Dm7",
    "Asus2", "Dsus2", "Esus2", "Gsus2",
    "Csus4", "Dsus4", "Esus4", "Asus4",
    "Cadd9", "Gadd9", "Dadd9", "Aadd9"
}


def transpose_chord_for_capo(raw_chord: str, capo_fret: int) -> str:
    """
    Transposes a chord DOWN by capo_fret semitones.
    Fretting this shape with a Capo on capo_fret sounds at raw_chord pitch.
    """
    if capo_fret <= 0:
        return raw_chord
        
    root, quality = parse_chord_string(raw_chord)
    norm_root = root[0].upper() + (root[1:].lower() if len(root) > 1 else "")
    semitone = NOTE_TO_SEMITONE.get(norm_root, 0)
    
    transposed_semitone = (semitone - capo_fret) % 12
    # Select accidental preference
    if "b" in root or raw_chord in ["F", "Bb", "Eb", "Ab", "Db"]:
        new_root = PITCH_CLASSES_FLAT[transposed_semitone]
    else:
        new_root = PITCH_CLASSES_SHARP[transposed_semitone]
        
    suffix = "m" if (quality in ["minor", "m"]) else ("" if quality in ["major", "maj", ""] else quality)
    return f"{new_root}{suffix}"


def evaluate_capo_benefit(
    chord_names: List[str],
    profile: Optional[HandProfile] = None,
    max_capo: int = 7
) -> Dict[str, Any]:
    """
    Scans Capo frets 1 to max_capo to detect if a capo allows the musician
    to play the progression using easy open cowboy chords.
    """
    if profile is None:
        profile = PRESET_PROFILES["arthritis_moderate"]
        
    best_fret = 0
    best_open_count = 0
    best_barres_avoided = 0
    best_transposed: List[str] = list(chord_names)
    
    # Baseline: check how many chords are already open cowboy chords at fret 0
    baseline_open_count = sum(1 for c in chord_names if c in OPEN_COWBOY_KEYS)
    baseline_barres = 0
    for c in chord_names:
        std_v, _ = get_voicings_for_chord(c)
        if std_v.has_barre or any(len(b.strings) >= 2 for b in std_v.barres):
            baseline_barres += 1
            
    candidate_results = []
    
    for f in range(1, max_capo + 1):
        transposed_chords = [transpose_chord_for_capo(c, f) for c in chord_names]
        open_count = sum(1 for c in transposed_chords if c in OPEN_COWBOY_KEYS)
        
        barres_count = 0
        for c in transposed_chords:
            std_v, _ = get_voicings_for_chord(c)
            if std_v.has_barre or any(len(b.strings) >= 2 for b in std_v.barres):
                barres_count += 1
                
        barres_avoided = max(0, baseline_barres - barres_count)
        
        score = (open_count * 3.0) + (barres_avoided * 4.0)
        candidate_results.append({
            "capo_fret": f,
            "transposed_chords": transposed_chords,
            "open_count": open_count,
            "barres_count": barres_count,
            "barres_avoided": barres_avoided,
            "score": score
        })
        
    # Sort candidate results by score descending
    candidate_results.sort(key=lambda x: (x["score"], -x["capo_fret"]), reverse=True)
    
    if candidate_results and candidate_results[0]["score"] > (baseline_open_count * 3.0):
        top = candidate_results[0]
        # Only recommend if it improves on baseline
        if top["open_count"] > baseline_open_count or top["barres_avoided"] > 0:
            best_fret = top["capo_fret"]
            best_transposed = top["transposed_chords"]
            best_barres_avoided = top["barres_avoided"]
            best_open_count = top["open_count"]
            
    if best_fret > 0:
        shapes_str = " -> ".join(best_transposed)
        rec_text = f"Put a capo on fret {best_fret} and play {shapes_str} shapes ({best_open_count} of {len(chord_names)} open shapes, {best_barres_avoided} barres avoided)."
        return {
            "has_recommendation": True,
            "recommended_capo_fret": best_fret,
            "transposed_shapes": best_transposed,
            "recommendation_text": rec_text,
            "open_chords_count": best_open_count,
            "barres_avoided_count": best_barres_avoided
        }
    else:
        return {
            "has_recommendation": False,
            "recommended_capo_fret": 0,
            "transposed_shapes": list(chord_names),
            "recommendation_text": "Playing without a capo is already the easiest option for these chords.",
            "open_chords_count": baseline_open_count,
            "barres_avoided_count": 0
        }
