import math
from typing import Dict, List, Optional, Tuple

# Chromatic scale definitions
PITCH_CLASSES_SHARP = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
PITCH_CLASSES_FLAT  = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]

NOTE_TO_SEMITONE: Dict[str, int] = {
    "C": 0, "B#": 0,
    "C#": 1, "Db": 1,
    "D": 2,
    "D#": 3, "Eb": 3,
    "E": 4, "Fb": 4,
    "F": 5, "E#": 5,
    "F#": 6, "Gb": 6,
    "G": 7,
    "G#": 8, "Ab": 8,
    "A": 9,
    "A#": 10, "Bb": 10,
    "B": 11, "Cb": 11,
}

# Standard Guitar Tuning: E2, A2, D3, G3, B3, E4
# String indices: 0 = Low E (str 6), 1 = A (str 5), 2 = D (str 4), 3 = G (str 3), 4 = B (str 2), 5 = High e (str 1)
STANDARD_TUNING_MIDI = [40, 45, 50, 55, 59, 64]
STANDARD_TUNING_NOTES = ["E2", "A2", "D3", "G3", "B3", "E4"]
STANDARD_TUNING_PITCH_CLASSES = [4, 9, 2, 7, 11, 4]  # E, A, D, G, B, E

CHORD_INTERVALS: Dict[str, List[int]] = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "7": [0, 4, 7, 10],
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "add9": [0, 4, 7, 2],
    "6": [0, 4, 7, 9],
}

QUALITY_FORMULAS: Dict[str, str] = {
    "major": "1 - 3 - 5",
    "minor": "1 - b3 - 5",
    "7": "1 - 3 - 5 - b7",
    "maj7": "1 - 3 - 5 - 7",
    "min7": "1 - b3 - 5 - b7",
    "sus2": "1 - 2 - 5",
    "sus4": "1 - 4 - 5",
    "add9": "1 - 3 - 5 - 9",
    "6": "1 - 3 - 5 - 6",
}


def midi_to_frequency(midi: int) -> float:
    """Converts a standard MIDI note number to frequency in Hertz."""
    return round(440.0 * (2.0 ** ((midi - 69) / 12.0)), 2)


def get_string_fret_pitch(string_idx: int, fret: int) -> Tuple[Optional[str], Optional[float], Optional[int]]:
    """
    Returns (note_name_with_octave, frequency_hz, midi_note) for a string and fret.
    fret = -1 means muted string.
    """
    if fret < 0:
        return ("X", 0.0, None)
    
    base_midi = STANDARD_TUNING_MIDI[string_idx]
    midi = base_midi + fret
    freq = midi_to_frequency(midi)
    
    semitone = midi % 12
    octave = (midi // 12) - 1
    note_name = f"{PITCH_CLASSES_SHARP[semitone]}{octave}"
    return (note_name, freq, midi)


def parse_chord_string(chord_str: str) -> Tuple[str, str]:
    """
    Parses a user chord string like 'F#m7', 'Bbmaj7', 'Cadd9', 'Gsus4', 'Bm', 'F'
    into (root, quality).
    """
    s = chord_str.strip()
    if not s:
        return ("C", "major")
    
    # Check two-character roots
    root = ""
    quality_part = ""
    if len(s) >= 2 and (s[1] == '#' or s[1] == 'b'):
        root = s[:2]
        quality_part = s[2:]
    else:
        root = s[:1]
        quality_part = s[1:]
    
    # Capitalize root
    root = root[0].upper() + (root[1] if len(root) > 1 else "")
    
    q_norm = quality_part.strip().lower()
    if q_norm in ["", "maj", "major", "m_maj"]:
        quality = "major"
    elif q_norm in ["m", "min", "minor"]:
        quality = "minor"
    elif q_norm in ["7", "dom7", "dominant7"]:
        quality = "7"
    elif q_norm in ["maj7", "m7+", "^7", "major7", "ma7"]:
        quality = "maj7"
    elif q_norm in ["m7", "min7", "minor7"]:
        quality = "min7"
    elif q_norm in ["sus2", "s2"]:
        quality = "sus2"
    elif q_norm in ["sus4", "sus", "s4"]:
        quality = "sus4"
    elif q_norm in ["add9", "add2", "2", "9"]:
        quality = "add9"
    elif q_norm in ["6", "maj6"]:
        quality = "6"
    else:
        quality = "major"
        
    return (root, quality)


def format_chord_display(root: str, quality: str) -> str:
    """Returns the conventional human-readable display string for a chord."""
    if quality == "major":
        return root
    elif quality == "minor":
        return f"{root}m"
    elif quality == "7":
        return f"{root}7"
    elif quality == "maj7":
        return f"{root}maj7"
    elif quality == "min7":
        return f"{root}m7"
    elif quality == "sus2":
        return f"{root}sus2"
    elif quality == "sus4":
        return f"{root}sus4"
    elif quality == "add9":
        return f"{root}add9"
    elif quality == "6":
        return f"{root}6"
    return f"{root}{quality}"


def get_notes_for_chord(root: str, quality: str) -> List[str]:
    """Returns the pitch class note names comprising the chord."""
    root_val = NOTE_TO_SEMITONE.get(root, 0)
    intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])
    use_flats = "b" in root or root in ["F", "Bb", "Eb", "Ab", "Db"]
    palette = PITCH_CLASSES_FLAT if use_flats else PITCH_CLASSES_SHARP
    return [palette[(root_val + interval) % 12] for interval in intervals]
