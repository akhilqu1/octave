from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class BarreDetail(BaseModel):
    finger: int = 1  # 1=index, 2=middle, etc.
    fret: int
    strings: List[int] = Field(default_factory=list)  # list of string indices (0=Low E, 5=High E)


class ChordVoicing(BaseModel):
    id: str
    chord_name: str
    root: str
    quality: str
    frets: List[int] = Field(
        ...,
        description="Fret number for each string [Low E (str 6), A (str 5), D (str 4), G (str 3), B (str 2), High e (str 1)]. -1 for mute, 0 for open."
    )
    fingers: List[int] = Field(
        ...,
        description="Finger for each string [0=unfretted/open/mute, 1=index, 2=middle, 3=ring, 4=pinky, -1=thumb]."
    )
    barres: List[BarreDetail] = Field(default_factory=list)
    has_barre: bool = False
    barre_string_count: int = 0
    fret_span: int = 0
    notes: List[str] = Field(default_factory=list)
    pitches_hz: List[float] = Field(default_factory=list)
    is_standard: bool = False
    voicing_category: str = "ergonomic"  # "standard", "open_drone", "compact_triad", "harmonic_sub"
    description: str = ""
    formula: str = ""  # e.g., "1 - 3 - 5", "1 - b3 - 5 - b7"


class ChordRequestItem(BaseModel):
    root: str  # e.g. "F", "C", "G#", "Bb"
    quality: str  # e.g. "major", "minor", "7", "maj7", "min7", "sus2", "sus4", "add9"
    display_name: Optional[str] = None
