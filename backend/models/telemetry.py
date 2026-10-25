from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.models.chord import ChordVoicing


class BiomechanicalStrainBreakdown(BaseModel):
    span_penalty: float = Field(..., description="Cost of fret distance between extreme fretted notes")
    barre_torque_penalty: float = Field(..., description="Cost of isometric clamping across multiple strings")
    digit_fatigue_penalty: float = Field(..., description="Cost based on finger mobility constraints")
    pinky_reach_penalty: float = Field(..., description="Cost of demanding bass reach from digit 4")
    open_string_bonus: float = Field(..., description="Ergonomic discount from zero-force open vibrating strings")
    total_chord_strain: float = Field(..., description="Composite static hand strain score")
    is_barre_active: bool = False
    barre_strings_count: int = 0
    fret_span: int = 0
    fingering_notation: str = ""  # e.g., "1-3-3-2-1-1" or "x-x-3-2-1-0"


class TransitionMetrics(BaseModel):
    finger_travel_distance: float = Field(..., description="Normalized hand distance traveled between chords")
    pivot_finger_count: int = Field(0, description="Number of fingers held as static biomechanical anchors")
    pivot_fingers: List[int] = Field(default_factory=list, description="Finger indices that acted as anchors (1-4)")
    hand_shift_frets: float = Field(0.0, description="Displacement of hand center of mass along guitar neck")
    transition_strain_cost: float = Field(0.0, description="Dynamic cost of transitioning between the shapes")


class ChordStepResult(BaseModel):
    step_index: int
    requested_chord: str
    standard_voicing: ChordVoicing
    standard_strain: BiomechanicalStrainBreakdown
    optimized_voicing: ChordVoicing
    optimized_strain: BiomechanicalStrainBreakdown
    strain_reduction_pct: float
    transition_from_prev: Optional[TransitionMetrics] = None


class OptimizationTelemetry(BaseModel):
    progression_id: str
    total_chords: int
    profile_used: str
    baseline_total_strain: float
    optimized_total_strain: float
    total_strain_reduction_pct: float
    baseline_total_travel: float
    optimized_total_travel: float
    travel_reduction_pct: float
    barres_eliminated_count: int
    open_strings_gained_count: int
    avg_span_before: float
    avg_span_after: float
    steps: List[ChordStepResult]
    calculation_logs: List[str] = Field(default_factory=list)
    has_capo_recommendation: bool = False
    recommended_capo_fret: int = 0
    capo_transposed_shapes: List[str] = Field(default_factory=list)
    capo_recommendation_text: Optional[str] = None


class ProgressionOptimizeRequest(BaseModel):
    chords: List[str]  # e.g. ["F", "C", "G", "Am"] or ["Bm", "G", "D", "A"]
    profile_id: Optional[str] = "arthritis_moderate"
    custom_profile: Optional[Dict[str, Any]] = None
    enable_capo: Optional[bool] = False
