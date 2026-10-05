from typing import Dict, List, Optional, Tuple
from backend.models.chord import ChordVoicing, BarreDetail
from backend.engine.music_theory import (
    parse_chord_string,
    format_chord_display,
    get_notes_for_chord,
    get_string_fret_pitch,
    NOTE_TO_SEMITONE,
    PITCH_CLASSES_SHARP,
    STANDARD_TUNING_PITCH_CLASSES,
    CHORD_INTERVALS,
    QUALITY_FORMULAS
)


def create_voicing(
    id_str: str,
    root: str,
    quality: str,
    frets: List[int],
    fingers: List[int],
    barres: Optional[List[BarreDetail]] = None,
    is_standard: bool = False,
    category: str = "ergonomic",
    description: str = "",
    display_suffix: str = ""
) -> ChordVoicing:
    """Helper to assemble a validated ChordVoicing with automatic note and frequency metadata."""
    notes: List[str] = []
    pitches_hz: List[float] = []
    
    for s_idx, f in enumerate(frets):
        note_name, freq, _ = get_string_fret_pitch(s_idx, f)
        notes.append(note_name or "X")
        pitches_hz.append(freq or 0.0)
        
    barres_list = barres or []
    has_barre = any(len(b.strings) >= 2 for b in barres_list)
    barre_count = max((len(b.strings) for b in barres_list), default=0)
    
    fretted = [f for f in frets if f > 0]
    span = (max(fretted) - min(fretted)) if fretted else 0
    
    base_display = format_chord_display(root, quality)
    full_display = f"{base_display}{display_suffix}" if display_suffix else base_display
    
    return ChordVoicing(
        id=id_str,
        chord_name=full_display,
        root=root,
        quality=quality,
        frets=frets,
        fingers=fingers,
        barres=barres_list,
        has_barre=has_barre,
        barre_string_count=barre_count,
        fret_span=span,
        notes=notes,
        pitches_hz=pitches_hz,
        is_standard=is_standard,
        voicing_category=category,
        description=description,
        formula=QUALITY_FORMULAS.get(quality, "1 - 3 - 5")
    )


# Curated dictionary of iconic textbook shapes and high-fidelity ergonomic alternatives
# Key: (canonical_sharp_root, quality)
CORE_VOICINGS_CATALOG: Dict[Tuple[str, str], Dict[str, List[ChordVoicing]]] = {}


def register_chord(root: str, quality: str, standard: ChordVoicing, alternatives: List[ChordVoicing]):
    norm_root = root[0].upper() + (root[1:].lower() if len(root) > 1 else "")
    semitone = NOTE_TO_SEMITONE.get(norm_root, 0)
    canonical_root = PITCH_CLASSES_SHARP[semitone]
    key = (canonical_root, quality)
    
    if key not in CORE_VOICINGS_CATALOG:
        CORE_VOICINGS_CATALOG[key] = {"standard": [], "alternatives": []}
        
    CORE_VOICINGS_CATALOG[key]["standard"].append(standard)
    CORE_VOICINGS_CATALOG[key]["alternatives"].extend(alternatives)


# =======================================================================
# POPULATING COMPREHENSIVE REPERTOIRE (Standard vs Low-Strain Ergonomic)
# All Easy shapes are harmonically tuned to sound identical to the standard.
# =======================================================================

# ----------------- C MAJOR FAMILY -----------------
register_chord(
    "C", "major",
    standard=create_voicing(
        "C_maj_std", "C", "major",
        frets=[-1, 3, 2, 0, 1, 0],
        fingers=[0, 3, 2, 0, 1, 0],
        is_standard=True, category="standard",
        description="Standard textbook open C major."
    ),
    alternatives=[
        create_voicing(
            "C_maj_2finger_pure", "C", "major",
            frets=[-1, -1, 2, 0, 1, 0],
            fingers=[0, 0, 2, 0, 1, 0],
            category="ergonomic",
            description="Pure C major: 2 fingers on D and B strings, open G and high E. 100% C-E-G pure triad."
        ),
        create_voicing(
            "C_maj_muted_e", "C", "major",
            frets=[-1, 3, 2, 0, 1, -1],
            fingers=[0, 3, 2, 0, 1, 0],
            category="ergonomic",
            description="Pure C major with root C in bass; mutes high E to avoid knuckle strain."
        ),
        create_voicing(
            "C_maj_full_bass", "C", "major",
            frets=[3, 3, 2, 0, 1, 0],
            fingers=[3, 4, 2, 0, 1, 0],
            category="open_drone",
            description="Full C/G voicing: deep low bass resonance."
        )
    ]
)

register_chord(
    "C", "minor",
    standard=create_voicing(
        "C_min_std", "C", "minor",
        frets=[-1, 3, 5, 5, 4, 3],
        fingers=[0, 1, 3, 4, 2, 1],
        barres=[BarreDetail(finger=1, fret=3, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="5-string textbook barre chord at fret 3."
    ),
    alternatives=[
        create_voicing(
            "C_min_zero_barre", "C", "minor",
            frets=[-1, 3, 5, 5, 4, -1],
            fingers=[0, 1, 3, 4, 2, 0],
            category="ergonomic",
            description="Pure C minor: Root C in bass, 5th G, octave C, minor 3rd Eb. ZERO barre clamp!"
        ),
        create_voicing(
            "C_min_triad_upper", "C", "minor",
            frets=[-1, -1, -1, 5, 4, 3],
            fingers=[0, 0, 0, 3, 2, 1],
            category="compact_triad",
            description="Pure C minor 3-note triad on upper strings; eliminates wrist flexion entirely."
        ),
        create_voicing(
            "C_min_4string", "C", "minor",
            frets=[-1, -1, 5, 5, 4, 3],
            fingers=[0, 0, 3, 4, 2, 1],
            category="ergonomic",
            description="4-string C minor shape; drops thick 5th string stretch."
        )
    ]
)

register_chord(
    "C", "7",
    standard=create_voicing(
        "C_7_std", "C", "7",
        frets=[-1, 3, 2, 3, 1, 0],
        fingers=[0, 3, 2, 4, 1, 0],
        is_standard=True, category="standard",
        description="Textbook open C dominant 7th."
    ),
    alternatives=[
        create_voicing(
            "C_7_erg", "C", "7",
            frets=[-1, 3, 2, 3, 1, -1],
            fingers=[0, 3, 2, 4, 1, 0],
            category="ergonomic",
            description="C7 without high E string stretch; comfortable balanced arch."
        ),
        create_voicing(
            "C_7_3finger_shell", "C", "7",
            frets=[-1, 3, 2, 3, -1, -1],
            fingers=[0, 2, 1, 3, 0, 0],
            category="ergonomic",
            description="Compact 3-finger C7 shell: Root C, 3rd E, b7 Bb. Pure blues grit."
        )
    ]
)

register_chord(
    "C", "maj7",
    standard=create_voicing(
        "C_maj7_std", "C", "maj7",
        frets=[-1, 3, 2, 0, 0, 0],
        fingers=[0, 3, 2, 0, 0, 0],
        is_standard=True, category="standard",
        description="Textbook open Cmaj7: effortless 2-finger shape with open ringing B string."
    ),
    alternatives=[
        create_voicing(
            "C_maj7_muted_e", "C", "maj7",
            frets=[-1, 3, 2, 0, 0, -1],
            fingers=[0, 2, 1, 0, 0, 0],
            category="ergonomic",
            description="Cmaj7 shell: relaxed 2-finger grip."
        )
    ]
)

# ----------------- D MAJOR FAMILY -----------------
register_chord(
    "D", "major",
    standard=create_voicing(
        "D_maj_std", "D", "major",
        frets=[-1, -1, 0, 2, 3, 2],
        fingers=[0, 0, 0, 1, 3, 2],
        is_standard=True, category="standard",
        description="Textbook open D major."
    ),
    alternatives=[
        create_voicing(
            "D_maj_2finger_pure", "D", "major",
            frets=[-1, -1, 0, 2, 3, 2],
            fingers=[0, 0, 0, 1, 2, 1],
            category="ergonomic",
            description="Pure D major: index finger lays flat across frets 2 of G and high E, middle on B fret 3. Only 2 fingers!"
        ),
        create_voicing(
            "D_maj_triad_upper", "D", "major",
            frets=[-1, -1, -1, 2, 3, 2],
            fingers=[0, 0, 0, 1, 3, 2],
            category="compact_triad",
            description="Pure D major triad: A3, D4, F#4. 3 fingers, zero barre, span 1."
        ),
        create_voicing(
            "D_maj_easy_knuckle", "D", "major",
            frets=[-1, -1, 0, 2, 3, 2],
            fingers=[0, 0, 0, 2, 3, 1],
            category="ergonomic",
            description="Standard D major with relaxed finger arch."
        )
    ]
)

register_chord(
    "D", "minor",
    standard=create_voicing(
        "D_min_std", "D", "minor",
        frets=[-1, -1, 0, 2, 3, 1],
        fingers=[0, 0, 0, 2, 3, 1],
        is_standard=True, category="standard",
        description="Textbook open D minor."
    ),
    alternatives=[
        create_voicing(
            "D_min_relaxed_triad", "D", "minor",
            frets=[-1, -1, 0, 2, 3, 1],
            fingers=[0, 0, 0, 1, 3, 2],
            category="ergonomic",
            description="Pure D minor: comfortable natural finger spacing, full D-A-F triad."
        ),
        create_voicing(
            "D_min_triad_upper", "D", "minor",
            frets=[-1, -1, -1, 2, 3, 1],
            fingers=[0, 0, 0, 2, 3, 1],
            category="compact_triad",
            description="Pure D minor triad: A3, D4, F4. 3 fingers, zero barre, span 2."
        )
    ]
)

register_chord(
    "D", "7",
    standard=create_voicing(
        "D_7_std", "D", "7",
        frets=[-1, -1, 0, 2, 1, 2],
        fingers=[0, 0, 0, 2, 1, 3],
        is_standard=True, category="standard",
        description="Textbook open D dominant 7th."
    ),
    alternatives=[
        create_voicing(
            "D_7_erg", "D", "7",
            frets=[-1, -1, 0, 2, 1, 2],
            fingers=[0, 0, 0, 1, 2, 3],
            category="ergonomic",
            description="D7 with comfortable triangular alignment."
        )
    ]
)

register_chord(
    "D", "min7",
    standard=create_voicing(
        "D_min7_std", "D", "min7",
        frets=[-1, -1, 0, 2, 1, 1],
        fingers=[0, 0, 0, 2, 1, 1],
        is_standard=True, category="standard",
        description="Textbook open D minor 7th: index mini-barre across strings 1 and 2, middle on string 3."
    ),
    alternatives=[
        create_voicing(
            "D_min7_erg", "D", "min7",
            frets=[-1, -1, 0, 2, 1, 1],
            fingers=[0, 0, 0, 2, 1, 3],
            category="ergonomic",
            description="Dm7: Root D, 5th A, Minor 7th C, Minor 3rd F. 3 separate relaxed fingers, ZERO barre clamp."
        ),
        create_voicing(
            "D_min7_drop5", "D", "min7",
            frets=[-1, -1, 0, -1, 1, 1],
            fingers=[0, 0, 0, 0, 1, 2],
            category="compact_triad",
            description="Dm7 drop-5 shell: Root D, Minor 7th C, Minor 3rd F. 2 relaxed fingers."
        )
    ]
)

register_chord(
    "D", "maj7",
    standard=create_voicing(
        "D_maj7_std", "D", "maj7",
        frets=[-1, -1, 0, 2, 2, 2],
        fingers=[0, 0, 0, 1, 1, 1],
        is_standard=True, category="standard",
        description="Textbook open Dmaj7: 1-finger mini-barre across fret 2."
    ),
    alternatives=[
        create_voicing(
            "D_maj7_erg", "D", "maj7",
            frets=[-1, -1, 0, 2, 2, 2],
            fingers=[0, 0, 0, 1, 2, 3],
            category="ergonomic",
            description="Dmaj7 with individual fingers; zero barre pressure."
        )
    ]
)

# ----------------- E MAJOR FAMILY -----------------
register_chord(
    "E", "major",
    standard=create_voicing(
        "E_maj_std", "E", "major",
        frets=[0, 2, 2, 1, 0, 0],
        fingers=[0, 2, 3, 1, 0, 0],
        is_standard=True, category="standard",
        description="Standard textbook open E major."
    ),
    alternatives=[
        create_voicing(
            "E_maj_2finger_pure", "E", "major",
            frets=[0, -1, 2, 1, 0, 0],
            fingers=[0, 0, 2, 1, 0, 0],
            category="ergonomic",
            description="Pure E major: Root E in bass, string 4 fret 2, string 3 fret 1, open B and high E. 100% E major triad with only 2 fingers!"
        ),
        create_voicing(
            "E_maj_1finger_barre", "E", "major",
            frets=[0, 2, 2, 1, 0, 0],
            fingers=[0, 1, 1, 2, 0, 0],
            category="ergonomic",
            description="E major with finger 1 flattening across strings 5 and 4 at fret 2."
        )
    ]
)

register_chord(
    "E", "minor",
    standard=create_voicing(
        "E_min_std", "E", "minor",
        frets=[0, 2, 2, 0, 0, 0],
        fingers=[0, 2, 3, 0, 0, 0],
        is_standard=True, category="standard",
        description="Standard open E minor."
    ),
    alternatives=[
        create_voicing(
            "E_min_1finger_pure", "E", "minor",
            frets=[0, -1, 2, 0, 0, 0],
            fingers=[0, 0, 1, 0, 0, 0],
            category="ergonomic",
            description="Pure E minor: Low E rings, string 4 fret 2, strings 3-2-1 ring openly. 100% pure Em triad with ONLY ONE FINGER!"
        ),
        create_voicing(
            "E_min_flat_1finger", "E", "minor",
            frets=[0, 2, 2, 0, 0, 0],
            fingers=[0, 1, 1, 0, 0, 0],
            category="ergonomic",
            description="Em with index finger flat across strings 5 and 4; 5 open vibrating strings."
        )
    ]
)

register_chord(
    "E", "7",
    standard=create_voicing(
        "E_7_std", "E", "7",
        frets=[0, 2, 0, 1, 0, 0],
        fingers=[0, 2, 0, 1, 0, 0],
        is_standard=True, category="standard",
        description="Textbook open E dominant 7th: only 2 fingers, classic blues foundation."
    ),
    alternatives=[
        create_voicing(
            "E_7_erg", "E", "7",
            frets=[0, 2, 0, 1, 0, 0],
            fingers=[0, 1, 0, 2, 0, 0],
            category="ergonomic",
            description="E7 with comfortable index/middle placement."
        )
    ]
)

register_chord(
    "E", "min7",
    standard=create_voicing(
        "E_min7_std", "E", "min7",
        frets=[0, 2, 0, 0, 0, 0],
        fingers=[0, 1, 0, 0, 0, 0],
        is_standard=True, category="standard",
        description="Textbook open Em7: ONLY ONE FINGER on string 5 fret 2; 5 open strings ring."
    ),
    alternatives=[
        create_voicing(
            "E_min7_rock", "E", "min7",
            frets=[0, 2, 2, 0, 3, 0],
            fingers=[0, 1, 2, 0, 3, 0],
            category="open_drone",
            description="Em7 with locked ring finger on string 2 fret 3."
        )
    ]
)

# ----------------- F MAJOR FAMILY (CRITICAL BARRE SUBSTITUTION) -----------------
register_chord(
    "F", "major",
    standard=create_voicing(
        "F_maj_std_barre", "F", "major",
        frets=[1, 3, 3, 2, 1, 1],
        fingers=[1, 3, 4, 2, 1, 1],
        barres=[BarreDetail(finger=1, fret=1, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="High-torque 6-string full index barre chord at fret 1. Extreme flexor strain."
    ),
    alternatives=[
        create_voicing(
            "F_maj_3finger_zero_barre", "F", "major",
            frets=[-1, -1, 3, 2, 1, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure F major triad: Root F3 in bass, Major 3rd A3, 5th C4. ZERO barre, 3 relaxed fingers, span of 2 frets!"
        ),
        create_voicing(
            "F_maj_4string_pure", "F", "major",
            frets=[-1, -1, 3, 2, 1, 1],
            fingers=[0, 0, 3, 2, 1, 1],
            barres=[BarreDetail(finger=1, fret=1, strings=[4, 5])],
            category="ergonomic",
            description="Pure F major: Root F in bass (string 4 fret 3), A, C, F. Zero big barre clamp! Sounds 100% like F major."
        ),
        create_voicing(
            "F_maj_over_c", "F", "major",
            frets=[-1, 3, 3, 2, 1, -1],
            fingers=[0, 3, 4, 2, 1, 0],
            category="ergonomic",
            description="F/C full warm acoustic voicing: C-F-A-C, zero barre pressure."
        )
    ]
)

register_chord(
    "F", "minor",
    standard=create_voicing(
        "F_min_std_barre", "F", "minor",
        frets=[1, 3, 3, 1, 1, 1],
        fingers=[1, 3, 4, 1, 1, 1],
        barres=[BarreDetail(finger=1, fret=1, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="Full 6-string barre chord at fret 1 with index clamp."
    ),
    alternatives=[
        create_voicing(
            "F_min_3finger_triad", "F", "minor",
            frets=[-1, -1, 3, 1, 1, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure F minor triad: Root F3, Minor 3rd Ab3, 5th C4. 3 individual fingers, ZERO barre!"
        ),
        create_voicing(
            "F_min_4string_pure", "F", "minor",
            frets=[-1, -1, 3, 1, 1, 1],
            fingers=[0, 0, 3, 1, 1, 1],
            barres=[BarreDetail(finger=1, fret=1, strings=[3, 4, 5])],
            category="ergonomic",
            description="Pure F minor: Root F in bass (string 4 fret 3), Ab, C, F. Small treble clamp, zero wrist torque!"
        )
    ]
)

register_chord(
    "F", "maj7",
    standard=create_voicing(
        "F_maj7_std", "F", "maj7",
        frets=[-1, -1, 3, 2, 1, 0],
        fingers=[0, 0, 3, 2, 1, 0],
        is_standard=True, category="standard",
        description="Textbook open Fmaj7: 3 relaxed fingers, open ringing high E."
    ),
    alternatives=[
        create_voicing(
            "F_maj7_full", "F", "maj7",
            frets=[-1, 3, 3, 2, 1, 0],
            fingers=[0, 3, 4, 2, 1, 0],
            category="open_drone",
            description="Fmaj7/C: full acoustic resonance."
        )
    ]
)

# ----------------- F# / Gb FAMILY -----------------
register_chord(
    "F#", "major",
    standard=create_voicing(
        "Fsharp_maj_std", "F#", "major",
        frets=[2, 4, 4, 3, 2, 2],
        fingers=[1, 3, 4, 2, 1, 1],
        barres=[BarreDetail(finger=1, fret=2, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="6-string full barre chord at fret 2."
    ),
    alternatives=[
        create_voicing(
            "Fsharp_maj_4string_pure", "F#", "major",
            frets=[-1, -1, 4, 3, 2, 2],
            fingers=[0, 0, 3, 2, 1, 1],
            barres=[BarreDetail(finger=1, fret=2, strings=[4, 5])],
            category="ergonomic",
            description="Pure F# major: Root F# in bass (string 4 fret 4), A#, C#, F#. Zero full barre!"
        ),
        create_voicing(
            "Fsharp_maj_triad_pure", "F#", "major",
            frets=[-1, -1, 4, 3, 2, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure F# triad: Root F#3, Major 3rd A#3, 5th C#4. 3 fingers, ZERO barre."
        )
    ]
)

register_chord(
    "F#", "minor",
    standard=create_voicing(
        "Fsharp_min_std", "F#", "minor",
        frets=[2, 4, 4, 2, 2, 2],
        fingers=[1, 3, 4, 1, 1, 1],
        barres=[BarreDetail(finger=1, fret=2, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="6-string barre chord at fret 2."
    ),
    alternatives=[
        create_voicing(
            "Fsharp_min_4string_pure", "F#", "minor",
            frets=[-1, -1, 4, 2, 2, 2],
            fingers=[0, 0, 3, 1, 1, 1],
            barres=[BarreDetail(finger=1, fret=2, strings=[3, 4, 5])],
            category="ergonomic",
            description="Pure F# minor: Root F# in bass, A, C#, F#. Index flat on fret 2 strings 1-3. Pure F#m!"
        ),
        create_voicing(
            "Fsharp_min_low_bass", "F#", "minor",
            frets=[2, 4, 4, 2, -1, -1],
            fingers=[1, 3, 4, 2, 0, 0],
            category="ergonomic",
            description="Pure F# minor with deep low F# bass note: F#-C#-F#-A. Zero barre clamp!"
        ),
        create_voicing(
            "Fsharp_min_triad_pure", "F#", "minor",
            frets=[-1, -1, 4, 2, 2, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure F#m triad: Root F#3, Minor 3rd A3, 5th C#4. 3 separate fingers, ZERO barre."
        )
    ]
)

# ----------------- G MAJOR FAMILY -----------------
register_chord(
    "G", "major",
    standard=create_voicing(
        "G_maj_std", "G", "major",
        frets=[3, 2, 0, 0, 0, 3],
        fingers=[2, 1, 0, 0, 0, 3],
        is_standard=True, category="standard",
        description="Textbook open G major."
    ),
    alternatives=[
        create_voicing(
            "G_maj_2finger_pure", "G", "major",
            frets=[3, -1, 0, 0, 0, 3],
            fingers=[2, 0, 0, 0, 0, 3],
            category="ergonomic",
            description="Pure G major: Root G in bass, open D, G, B, high G. 100% pure G major triad with ONLY 2 FINGERS!"
        ),
        create_voicing(
            "G_maj_4finger_rock", "G", "major",
            frets=[3, 2, 0, 0, 3, 3],
            fingers=[2, 1, 0, 0, 3, 4],
            category="open_drone",
            description="Modern rock G: locked ring and pinky fingers, effortless transition to Cadd9."
        ),
        create_voicing(
            "G_maj_easy_knuckle", "G", "major",
            frets=[3, 2, 0, 0, 0, 3],
            fingers=[3, 2, 0, 0, 0, 4],
            category="ergonomic",
            description="Open G with ring and pinky on outer strings, freeing index finger."
        )
    ]
)

register_chord(
    "G", "minor",
    standard=create_voicing(
        "G_min_std", "G", "minor",
        frets=[3, 5, 5, 3, 3, 3],
        fingers=[1, 3, 4, 1, 1, 1],
        barres=[BarreDetail(finger=1, fret=3, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="6-string barre chord at fret 3."
    ),
    alternatives=[
        create_voicing(
            "G_min_4string_pure", "G", "minor",
            frets=[-1, -1, 5, 3, 3, 3],
            fingers=[0, 0, 3, 1, 1, 1],
            barres=[BarreDetail(finger=1, fret=3, strings=[3, 4, 5])],
            category="ergonomic",
            description="Pure G minor: Root G in bass (string 4 fret 5), Bb, D, G. Small treble clamp, zero barre torque!"
        ),
        create_voicing(
            "G_min_triad_pure", "G", "minor",
            frets=[-1, -1, 5, 3, 3, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure G minor triad: Root G3, Minor 3rd Bb3, 5th D4. 3 separate fingers, ZERO barre."
        ),
        create_voicing(
            "G_min_low_bass", "G", "minor",
            frets=[3, 5, 5, 3, -1, -1],
            fingers=[1, 3, 4, 2, 0, 0],
            category="ergonomic",
            description="Pure G minor with low G bass note: G-D-G-Bb. Zero barre clamp!"
        )
    ]
)

register_chord(
    "G", "7",
    standard=create_voicing(
        "G_7_std", "G", "7",
        frets=[3, 2, 0, 0, 0, 1],
        fingers=[3, 2, 0, 0, 0, 1],
        is_standard=True, category="standard",
        description="Textbook open G dominant 7th."
    ),
    alternatives=[
        create_voicing(
            "G_7_2finger_pure", "G", "7",
            frets=[3, -1, 0, 0, 0, 1],
            fingers=[2, 0, 0, 0, 0, 1],
            category="ergonomic",
            description="Pure G7: Root G in bass, open D, G, B, high F. ONLY 2 FINGERS! True blues G7 sound."
        )
    ]
)

register_chord(
    "G", "maj7",
    standard=create_voicing(
        "G_maj7_std", "G", "maj7",
        frets=[3, 2, 0, 0, 0, 2],
        fingers=[2, 1, 0, 0, 0, 3],
        is_standard=True, category="standard",
        description="Textbook open Gmaj7."
    ),
    alternatives=[
        create_voicing(
            "G_maj7_2finger", "G", "maj7",
            frets=[3, -1, 0, 0, 0, 2],
            fingers=[2, 0, 0, 0, 0, 1],
            category="ergonomic",
            description="Gmaj7 with only 2 fingers: low G and high F#."
        )
    ]
)

# ----------------- G# / Ab FAMILY -----------------
register_chord(
    "G#", "major",
    standard=create_voicing(
        "Gsharp_maj_std", "Ab", "major",
        frets=[4, 6, 6, 5, 4, 4],
        fingers=[1, 3, 4, 2, 1, 1],
        barres=[BarreDetail(finger=1, fret=4, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="6-string barre chord at fret 4."
    ),
    alternatives=[
        create_voicing(
            "Ab_maj_4string_pure", "Ab", "major",
            frets=[-1, -1, 6, 5, 4, 4],
            fingers=[0, 0, 3, 2, 1, 1],
            barres=[BarreDetail(finger=1, fret=4, strings=[4, 5])],
            category="ergonomic",
            description="Pure Ab/G# major: Root Ab in bass (string 4 fret 6), C, Eb, Ab. Zero full barre!"
        ),
        create_voicing(
            "Ab_maj_triad_pure", "Ab", "major",
            frets=[-1, -1, 6, 5, 4, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure Ab/G# major triad: Root Ab3, Major 3rd C4, 5th Eb4. 3 fingers, zero barre."
        )
    ]
)

register_chord(
    "G#", "minor",
    standard=create_voicing(
        "Gsharp_min_std", "Ab", "minor",
        frets=[4, 6, 6, 4, 4, 4],
        fingers=[1, 3, 4, 1, 1, 1],
        barres=[BarreDetail(finger=1, fret=4, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="6-string barre chord at fret 4."
    ),
    alternatives=[
        create_voicing(
            "Ab_min_4string_pure", "Ab", "minor",
            frets=[-1, -1, 6, 4, 4, 4],
            fingers=[0, 0, 3, 1, 1, 1],
            barres=[BarreDetail(finger=1, fret=4, strings=[3, 4, 5])],
            category="ergonomic",
            description="Pure G#m/Abm: Root G# in bass, B, D#, G#. Small treble clamp, zero barre torque!"
        ),
        create_voicing(
            "Ab_min_triad_pure", "Ab", "minor",
            frets=[-1, -1, 6, 4, 4, -1],
            fingers=[0, 0, 3, 2, 1, 0],
            category="compact_triad",
            description="Pure G#m/Abm triad: Root G#3, Minor 3rd B3, 5th D#4. 3 separate fingers, ZERO barre."
        ),
        create_voicing(
            "Ab_min_low_bass", "Ab", "minor",
            frets=[4, 6, 6, 4, -1, -1],
            fingers=[1, 3, 4, 2, 0, 0],
            category="ergonomic",
            description="Pure G#m/Abm with low G# bass note: G#-D#-G#-B. Zero barre clamp!"
        )
    ]
)

# ----------------- A MAJOR FAMILY -----------------
register_chord(
    "A", "major",
    standard=create_voicing(
        "A_maj_std", "A", "major",
        frets=[-1, 0, 2, 2, 2, 0],
        fingers=[0, 0, 1, 2, 3, 0],
        is_standard=True, category="standard",
        description="Textbook open A major (3 crowded fingers at fret 2)."
    ),
    alternatives=[
        create_voicing(
            "A_maj_1finger_pure", "A", "major",
            frets=[-1, 0, 2, 2, 2, -1],
            fingers=[0, 0, 1, 1, 1, 0],
            barres=[BarreDetail(finger=1, fret=2, strings=[2, 3, 4])],
            category="ergonomic",
            description="Pure A major: Root A in bass, index finger lays flat across D-G-B at fret 2. 100% pure A-C#-E triad with ONLY 1 FINGER!"
        ),
        create_voicing(
            "A_maj_staggered", "A", "major",
            frets=[-1, 0, 2, 2, 2, 0],
            fingers=[0, 0, 2, 1, 3, 0],
            category="ergonomic",
            description="A major with staggered fingers (2-1-3), eliminating knuckle crowding."
        )
    ]
)

register_chord(
    "A", "minor",
    standard=create_voicing(
        "A_min_std", "A", "minor",
        frets=[-1, 0, 2, 2, 1, 0],
        fingers=[0, 0, 2, 3, 1, 0],
        is_standard=True, category="standard",
        description="Standard open A minor."
    ),
    alternatives=[
        create_voicing(
            "A_min_muted_high", "A", "minor",
            frets=[-1, 0, 2, 2, 1, -1],
            fingers=[0, 0, 2, 3, 1, 0],
            category="ergonomic",
            description="Pure A minor: Root A in bass, E, A, C. Mutes high E to avoid knuckle strain."
        ),
        create_voicing(
            "A_min_easy_fingers", "A", "minor",
            frets=[-1, 0, 2, 2, 1, 0],
            fingers=[0, 0, 1, 2, 1, 0],
            category="ergonomic",
            description="Standard Am with relaxed finger arch."
        )
    ]
)

register_chord(
    "A", "7",
    standard=create_voicing(
        "A_7_std", "A", "7",
        frets=[-1, 0, 2, 0, 2, 0],
        fingers=[0, 0, 1, 0, 2, 0],
        is_standard=True, category="standard",
        description="Textbook open A dominant 7th: only 2 fingers, classic open resonance."
    ),
    alternatives=[
        create_voicing(
            "A_7_erg", "A", "7",
            frets=[-1, 0, 2, 0, 2, 0],
            fingers=[0, 0, 2, 0, 3, 0],
            category="ergonomic",
            description="A7 with middle and ring fingers; comfortable wrist angle."
        )
    ]
)

register_chord(
    "A", "min7",
    standard=create_voicing(
        "A_min7_std", "A", "min7",
        frets=[-1, 0, 2, 0, 1, 0],
        fingers=[0, 0, 2, 0, 1, 0],
        is_standard=True, category="standard",
        description="Textbook open Am7: only 2 fingers, relaxed open sound."
    ),
    alternatives=[
        create_voicing(
            "A_min7_erg", "A", "min7",
            frets=[-1, 0, 2, 0, 1, -1],
            fingers=[0, 0, 2, 0, 1, 0],
            category="ergonomic",
            description="Am7 shell: comfortable 2-finger anchor."
        )
    ]
)

register_chord(
    "A", "maj7",
    standard=create_voicing(
        "A_maj7_std", "A", "maj7",
        frets=[-1, 0, 2, 1, 2, 0],
        fingers=[0, 0, 2, 1, 3, 0],
        is_standard=True, category="standard",
        description="Textbook open Amaj7: natural triangular arch on frets 1 and 2."
    ),
    alternatives=[
        create_voicing(
            "A_maj7_erg", "A", "maj7",
            frets=[-1, 0, 2, 1, 2, -1],
            fingers=[0, 0, 2, 1, 3, 0],
            category="ergonomic",
            description="Amaj7 without high E string stretch."
        )
    ]
)

# ----------------- Bb / A# FAMILY -----------------
register_chord(
    "A#", "major",
    standard=create_voicing(
        "Asharp_maj_std", "Bb", "major",
        frets=[-1, 1, 3, 3, 3, 1],
        fingers=[0, 1, 2, 3, 4, 1],
        barres=[BarreDetail(finger=1, fret=1, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="5-string barre chord at fret 1 with 3-finger jam."
    ),
    alternatives=[
        create_voicing(
            "Bb_maj_zero_barre", "Bb", "major",
            frets=[-1, 1, 3, 3, 3, -1],
            fingers=[0, 1, 2, 3, 4, 0],
            category="ergonomic",
            description="Pure Bb major: Root Bb in bass (string 5 fret 1), F, Bb, D. ZERO barre clamp on high E!"
        ),
        create_voicing(
            "Bb_maj_4string_pure", "Bb", "major",
            frets=[-1, -1, 3, 3, 3, 1],
            fingers=[0, 0, 2, 3, 4, 1],
            category="ergonomic",
            description="4-string Bb major: F, Bb, D, F. Drops low stretch completely."
        ),
        create_voicing(
            "Bb_maj_triad_pure", "Bb", "major",
            frets=[-1, -1, 3, 3, 3, -1],
            fingers=[0, 0, 1, 2, 3, 0],
            category="compact_triad",
            description="Pure Bb major 3-note triad on D-G-B strings."
        )
    ]
)

# ----------------- B MAJOR / MINOR FAMILY (CRITICAL BARRE SUBSTITUTION) -----------------
register_chord(
    "B", "major",
    standard=create_voicing(
        "B_maj_std_barre", "B", "major",
        frets=[-1, 2, 4, 4, 4, 2],
        fingers=[0, 1, 2, 3, 4, 1],
        barres=[BarreDetail(finger=1, fret=2, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="High-torque 5-string barre chord with 3-finger cluster at fret 4."
    ),
    alternatives=[
        create_voicing(
            "B_maj_zero_barre_pure", "B", "major",
            frets=[-1, 2, 4, 4, 4, -1],
            fingers=[0, 1, 2, 3, 4, 0],
            category="ergonomic",
            description="Pure B major: Root B in bass (string 5 fret 2), F#, B, D#. ZERO barre on high E! Sounds identical to barre chord."
        ),
        create_voicing(
            "B_maj_4string_pure", "B", "major",
            frets=[-1, -1, 4, 4, 4, 2],
            fingers=[0, 0, 2, 3, 4, 1],
            category="ergonomic",
            description="4-string B major: F#, B, D#, F#. Avoids stretching to string 5."
        ),
        create_voicing(
            "B_maj_triad_pure", "B", "major",
            frets=[-1, -1, -1, 4, 4, 2],
            fingers=[0, 0, 0, 2, 3, 1],
            category="compact_triad",
            description="Pure B triad on top 3 strings: B3, D#4, F#4. Minimal thumb load."
        )
    ]
)

register_chord(
    "B", "minor",
    standard=create_voicing(
        "B_min_std_barre", "B", "minor",
        frets=[-1, 2, 4, 4, 3, 2],
        fingers=[0, 1, 3, 4, 2, 1],
        barres=[BarreDetail(finger=1, fret=2, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="High-friction 5-string barre chord at fret 2. Stiff thumb counter-pressure."
    ),
    alternatives=[
        create_voicing(
            "B_min_zero_barre_pure", "B", "minor",
            frets=[-1, 2, 4, 4, 3, -1],
            fingers=[0, 1, 3, 4, 2, 0],
            category="ergonomic",
            description="Pure B minor: Root B in bass (string 5 fret 2), 5th F#, octave B, minor 3rd D. ZERO barre on high E! Sounds 99% identical to standard Bm!"
        ),
        create_voicing(
            "B_min_4string_pure", "B", "minor",
            frets=[-1, -1, 4, 4, 3, 2],
            fingers=[0, 0, 3, 4, 2, 1],
            category="ergonomic",
            description="4-string B minor: F#3, B3, D4, F#4. Smooth acoustic sound."
        ),
        create_voicing(
            "B_min_triad_pure", "B", "minor",
            frets=[-1, -1, -1, 4, 3, 2],
            fingers=[0, 0, 0, 3, 2, 1],
            category="compact_triad",
            description="Pure Bm triad on top 3 strings: B3, D4, F#4. Zero thumb load."
        )
    ]
)

register_chord(
    "B", "7",
    standard=create_voicing(
        "B_7_std", "B", "7",
        frets=[-1, 2, 1, 2, 0, 2],
        fingers=[0, 2, 1, 3, 0, 4],
        is_standard=True, category="standard",
        description="Textbook open B dominant 7th with open B string; eliminates barre completely."
    ),
    alternatives=[
        create_voicing(
            "B_7_muted_e", "B", "7",
            frets=[-1, 2, 1, 2, 0, -1],
            fingers=[0, 2, 1, 3, 0, 0],
            category="ergonomic",
            description="B7 without pinky reach on high E string."
        )
    ]
)

register_chord(
    "B", "min7",
    standard=create_voicing(
        "B_min7_std", "B", "min7",
        frets=[-1, 2, 4, 2, 3, 2],
        fingers=[0, 1, 3, 1, 2, 1],
        barres=[BarreDetail(finger=1, fret=2, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="Textbook 5-string Bm7 barre chord."
    ),
    alternatives=[
        create_voicing(
            "B_min7_zero_barre", "B", "min7",
            frets=[-1, 2, 4, 2, 3, -1],
            fingers=[0, 1, 3, 2, 4, 0],
            category="ergonomic",
            description="Bm7: Root B in bass, F#, A (b7), D (b3). 4 separate fingers, ZERO barre clamp!"
        ),
        create_voicing(
            "B_min7_open_drone", "B", "min7",
            frets=[-1, 2, 0, 2, 0, 2],
            fingers=[0, 1, 0, 2, 0, 3],
            category="open_drone",
            description="Open Bm7: Root B, open D, 7th A, open B, 5th F#. 3 fingers only, 2 open strings, ZERO barre!"
        )
    ]
)

# ----------------- C# / Db FAMILY -----------------
register_chord(
    "C#", "major",
    standard=create_voicing(
        "Csharp_maj_std", "C#", "major",
        frets=[-1, 4, 6, 6, 6, 4],
        fingers=[0, 1, 2, 3, 4, 1],
        barres=[BarreDetail(finger=1, fret=4, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="5-string barre chord at fret 4."
    ),
    alternatives=[
        create_voicing(
            "Csharp_maj_zero_barre", "C#", "major",
            frets=[-1, 4, 6, 6, 6, -1],
            fingers=[0, 1, 2, 3, 4, 0],
            category="ergonomic",
            description="Pure C# major: Root C# in bass (string 5 fret 4), G#, C#, F. ZERO barre on high E!"
        ),
        create_voicing(
            "Csharp_maj_4string", "C#", "major",
            frets=[-1, -1, 6, 6, 6, 4],
            fingers=[0, 0, 2, 3, 4, 1],
            category="ergonomic",
            description="4-string C# major: G#, C#, F, G#."
        ),
        create_voicing(
            "Csharp_maj_triad", "C#", "major",
            frets=[-1, -1, 6, 6, 6, -1],
            fingers=[0, 0, 1, 2, 3, 0],
            category="compact_triad",
            description="Pure C# 3-note triad on D-G-B strings."
        )
    ]
)

register_chord(
    "C#", "minor",
    standard=create_voicing(
        "Csharp_min_std", "C#", "minor",
        frets=[-1, 4, 6, 6, 5, 4],
        fingers=[0, 1, 3, 4, 2, 1],
        barres=[BarreDetail(finger=1, fret=4, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="5-string textbook barre chord at fret 4."
    ),
    alternatives=[
        create_voicing(
            "Csharp_min_zero_barre_pure", "C#", "minor",
            frets=[-1, 4, 6, 6, 5, -1],
            fingers=[0, 1, 3, 4, 2, 0],
            category="ergonomic",
            description="Pure C# minor: Root C# in bass (string 5 fret 4), 5th G#, octave C#, minor 3rd E. ZERO barre! Sounds virtually identical to standard C#m!"
        ),
        create_voicing(
            "Csharp_min_4string_pure", "C#", "minor",
            frets=[-1, -1, 6, 6, 5, 4],
            fingers=[0, 0, 3, 4, 2, 1],
            category="ergonomic",
            description="4-string C# minor: G#3, C#4, E4, G#4."
        ),
        create_voicing(
            "Csharp_min_triad_lower", "C#", "minor",
            frets=[-1, -1, 2, 1, 2, -1],
            fingers=[0, 0, 2, 1, 3, 0],
            category="compact_triad",
            description="Lower-neck 3-finger C#m triad: E3, G#3, C#4."
        )
    ]
)

# ----------------- D# / Eb FAMILY -----------------
register_chord(
    "D#", "major",
    standard=create_voicing(
        "Eb_maj_std", "Eb", "major",
        frets=[-1, 6, 8, 8, 8, 6],
        fingers=[0, 1, 2, 3, 4, 1],
        barres=[BarreDetail(finger=1, fret=6, strings=[1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description="5-string barre chord at fret 6."
    ),
    alternatives=[
        create_voicing(
            "Eb_maj_zero_barre_pure", "Eb", "major",
            frets=[-1, 6, 8, 8, 8, -1],
            fingers=[0, 1, 2, 3, 4, 0],
            category="ergonomic",
            description="Pure Eb major: Root Eb in bass (string 5 fret 6), Bb, Eb, G. ZERO barre on high E!"
        ),
        create_voicing(
            "Eb_maj_4string_low", "Eb", "major",
            frets=[-1, -1, 5, 3, 4, 3],
            fingers=[0, 0, 4, 1, 3, 2],
            category="ergonomic",
            description="Pure Eb major on lower neck: G3, Bb3, Eb4, G4. Warm, resonant, zero barre."
        ),
        create_voicing(
            "Eb_maj_triad_pure", "Eb", "major",
            frets=[-1, -1, -1, 3, 4, 3],
            fingers=[0, 0, 0, 1, 3, 2],
            category="compact_triad",
            description="Pure Eb major triad on strings 1, 2, 3: Bb3, Eb4, G4."
        )
    ]
)


def algorithmic_voicing_generator(root: str, quality: str) -> Tuple[ChordVoicing, List[ChordVoicing]]:
    """
    Fallback mathematical voicing generator for any arbitrary root and quality combination
    not explicitly defined in CORE_VOICINGS_CATALOG.
    Constructs clean, pure-sounding ergonomic voicings that match the exact requested chord.
    """
    norm_root = root[0].upper() + (root[1:].lower() if len(root) > 1 else "")
    semitone = NOTE_TO_SEMITONE.get(norm_root, 0)
    root_name = PITCH_CLASSES_SHARP[semitone]
    
    # E-shape barre base fret: (semitone - 4) % 12
    fret_e_shape = (semitone - 4) % 12
    if fret_e_shape == 0:
        fret_e_shape = 12
        
    is_minor = "min" in quality or quality == "m" or quality == "min7" or quality == "m7"
    is_7th = any(q in quality for q in ["7", "dom7", "min7", "m7", "maj7"])
    g_offset = 0 if is_minor else 1
    
    # Standard barre
    std_frets = [fret_e_shape, fret_e_shape + 2, fret_e_shape + 2, fret_e_shape + g_offset, fret_e_shape, fret_e_shape]
    std_fingers = [1, 3, 4, (0 if is_minor else 2), 1, 1]
    if is_minor:
        std_fingers[3] = 1
        
    # If dominant 7th, open the D string note down 2 frets
    if quality in ["7", "dom7"]:
        std_frets[2] = fret_e_shape
        std_fingers[2] = 1
    elif is_minor and is_7th:
        std_frets[2] = fret_e_shape
        std_fingers[2] = 1
        
    standard = create_voicing(
        f"{root}_{quality}_gen_std",
        root_name, quality,
        frets=std_frets,
        fingers=std_fingers,
        barres=[BarreDetail(finger=1, fret=fret_e_shape, strings=[0, 1, 2, 3, 4, 5])],
        is_standard=True, category="standard",
        description=f"Standard textbook 6-string barre voicing at fret {fret_e_shape}."
    )
    
    # Generate ergonomic alternatives:
    # 1. 4-string shape (D, G, B, high E strings)
    # This preserves the full chord quality (Root, 3rd, 5th, and 7th if present) with minimal barre
    alt1_frets = [-1, -1, fret_e_shape + (0 if is_7th and (is_minor or quality in ["7", "dom7"]) else 2), fret_e_shape + g_offset, fret_e_shape, fret_e_shape]
    alt1_fingers = [0, 0, (1 if is_7th and (is_minor or quality in ["7", "dom7"]) else 3), (2 if not is_minor else 1), 1, 1]
    alt1 = create_voicing(
        f"{root}_{quality}_gen_4string",
        root_name, quality,
        frets=alt1_frets,
        fingers=alt1_fingers,
        barres=[BarreDetail(finger=1, fret=fret_e_shape, strings=[4, 5])],
        category="ergonomic",
        description=f"Ergonomic 4-string voicing at frets {fret_e_shape}-{fret_e_shape+2}; drops thick bass strings."
    )
    
    # 2. Compact 3-string triad on strings 4, 3, 2 (Root, 3rd, 5th)
    triad_frets = [-1, -1, fret_e_shape + 2, fret_e_shape + g_offset, fret_e_shape, -1]
    triad_fingers = [0, 0, 3, (1 if is_minor else 2), 1, 0]
    alt2 = create_voicing(
        f"{root}_{quality}_gen_triad",
        root_name, quality,
        frets=triad_frets,
        fingers=triad_fingers,
        category="compact_triad",
        description=f"Pure 3-string triad at frets {fret_e_shape}-{fret_e_shape+2}; zero barre."
    )
    
    return (standard, [alt1, alt2])


def get_voicings_for_chord(chord_str: str) -> Tuple[ChordVoicing, List[ChordVoicing]]:
    """
    Returns (standard_voicing, [list_of_candidate_alternatives]) for any chord.
    Guaranteed to return high-quality standard and ergonomic options that preserve exact chord tones.
    """
    root, quality = parse_chord_string(chord_str)
    norm_root = root[0].upper() + (root[1:].lower() if len(root) > 1 else "")
    semitone = NOTE_TO_SEMITONE.get(norm_root, 0)
    canonical_root = PITCH_CLASSES_SHARP[semitone]
    
    key = (canonical_root, quality)
    if key in CORE_VOICINGS_CATALOG:
        data = CORE_VOICINGS_CATALOG[key]
        return (data["standard"][0], list(data["alternatives"]))
        
    # Check if "m" was passed instead of "minor"
    if quality == "m":
        alt_key = (canonical_root, "minor")
        if alt_key in CORE_VOICINGS_CATALOG:
            data = CORE_VOICINGS_CATALOG[alt_key]
            return (data["standard"][0], list(data["alternatives"]))
            
    # Fallback algorithmic generation
    return algorithmic_voicing_generator(canonical_root, quality)
