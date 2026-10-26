from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class FingerConstraint(BaseModel):
    finger_id: int  # 1=index, 2=middle, 3=ring, 4=pinky, -1=thumb
    name: str
    mobility_score: float = Field(1.0, ge=0.0, le=1.0, description="1.0 = full mobility, 0.0 = severe restriction/pain")
    fatigue_threshold: float = Field(1.0, ge=0.1, le=2.0, description="Multiplier on sustained strain")


class HandProfile(BaseModel):
    id: str = "custom"
    name: str = "Custom Profile"
    description: str = "User customized physical constraints"
    max_fret_span: int = Field(3, ge=1, le=5, description="Maximum comfortable span in frets between lowest and highest fretted note")
    ban_barres: bool = Field(False, description="Strictly forbid full or partial barre clamps")
    prefer_open_drones: bool = Field(True, description="Prioritize open resonant strings that require zero finger pressure")
    pinky_restriction: float = Field(1.0, ge=0.0, le=1.0, description="Mobility limit for digit 4 (pinky). 0 = avoid pinky entirely.")
    index_clamp_sensitivity: float = Field(1.0, ge=0.5, le=3.0, description="Sensitivity to index finger isometric clamping torque.")
    wrist_flexion_limit: float = Field(1.0, ge=0.5, le=3.0, description="Sensitivity to bass-string reaching (causes wrist flexion).")
    allow_harmonic_extensions: bool = Field(True, description="Allow harmonically rich, physically simpler substitutes like Maj7, Add9, Sus2, Min7")


# Hand Comfort Presets
PRESET_PROFILES: Dict[str, HandProfile] = {
    "arthritis_moderate": HandProfile(
        id="arthritis_moderate",
        name="Arthritis (Gentle Grip)",
        description="Keeps finger stretches narrow and avoids barre chords.",
        max_fret_span=2,
        ban_barres=True,
        prefer_open_drones=True,
        pinky_restriction=0.4,
        index_clamp_sensitivity=2.5,
        wrist_flexion_limit=1.5,
        allow_harmonic_extensions=True
    ),
    "tendonitis_flexor": HandProfile(
        id="tendonitis_flexor",
        name="Tendonitis (No Barre Chords)",
        description="Removes full and partial barre chords to reduce thumb and wrist pressure.",
        max_fret_span=2,
        ban_barres=True,
        prefer_open_drones=True,
        pinky_restriction=0.6,
        index_clamp_sensitivity=3.0,
        wrist_flexion_limit=1.8,
        allow_harmonic_extensions=True
    ),
    "dystonia_pinky": HandProfile(
        id="dystonia_pinky",
        name="3-Finger Mode (Avoid Pinky)",
        description="Picks chord shapes that use only your index, middle, and ring fingers.",
        max_fret_span=3,
        ban_barres=False,
        prefer_open_drones=True,
        pinky_restriction=0.0,  # Pinky banned or heavily penalized
        index_clamp_sensitivity=1.2,
        wrist_flexion_limit=1.2,
        allow_harmonic_extensions=True
    ),
    "carpal_tunnel": HandProfile(
        id="carpal_tunnel",
        name="Wrist Relief (Less Bass Reach)",
        description="Avoids wide stretches across the low E and A strings so your wrist stays straighter.",
        max_fret_span=2,
        ban_barres=True,
        prefer_open_drones=True,
        pinky_restriction=0.5,
        index_clamp_sensitivity=2.2,
        wrist_flexion_limit=2.5,
        allow_harmonic_extensions=True
    ),
    "healthy_baseline": HandProfile(
        id="healthy_baseline",
        name="Standard Guitar Shapes",
        description="Standard chord chart shapes without hand restrictions.",
        max_fret_span=4,
        ban_barres=False,
        prefer_open_drones=False,
        pinky_restriction=1.0,
        index_clamp_sensitivity=1.0,
        wrist_flexion_limit=1.0,
        allow_harmonic_extensions=True
    )
}
