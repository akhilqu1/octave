from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, File, UploadFile, Request
from backend.models.telemetry import OptimizationTelemetry, ProgressionOptimizeRequest
from backend.models.hand_profile import PRESET_PROFILES, HandProfile
from backend.engine.optimizer import optimize_progression
from backend.engine.harmonic_library import get_voicings_for_chord
from backend.engine.biomechanics import evaluate_chord_biomechanics
from backend.engine.midi_parser import parse_midi_bytes
from backend.engine.music_theory import (
    PITCH_CLASSES_SHARP,
    PITCH_CLASSES_FLAT,
    CHORD_INTERVALS,
    QUALITY_FORMULAS,
    parse_chord_string,
    format_chord_display
)

router = APIRouter(prefix="/api")


@router.post("/midi/parse")
async def parse_midi(request: Request):
    """Parses a MIDI file (.mid) uploaded as multipart form or raw body and extracts chord names."""
    try:
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            form = await request.form()
            file_item = form.get("file")
            if not file_item:
                raise HTTPException(status_code=400, detail="No file uploaded")
            data = await file_item.read()
        else:
            data = await request.body()
            
        if not data:
            raise HTTPException(status_code=400, detail="Empty MIDI file content")
            
        chords = parse_midi_bytes(data)
        return {"chords": chords, "count": len(chords)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse MIDI: {str(e)}")


@router.get("/health")
def get_health() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "octave-engine",
        "version": "1.0.0",
        "architecture": "modular-service-oriented",
        "features": [
            "biomechanical-cost-engine",
            "harmonic-voice-leading",
            "dynamic-programming-viterbi",
            "polyphonic-physical-synthesis"
        ]
    }


@router.get("/profiles")
def get_profiles() -> Dict[str, Any]:
    return {
        "presets": [profile.model_dump() for profile in PRESET_PROFILES.values()],
        "default": "arthritis_moderate"
    }


@router.get("/chords/roots")
def get_roots() -> Dict[str, Any]:
    return {
        "sharp_roots": PITCH_CLASSES_SHARP,
        "flat_roots": PITCH_CLASSES_FLAT,
        "primary": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
    }


@router.get("/chords/qualities")
def get_qualities() -> List[Dict[str, str]]:
    return [
        {"id": "major", "label": "Major", "suffix": "", "formula": "1 - 3 - 5", "desc": "Bright, happy standard chord"},
        {"id": "minor", "label": "Minor", "suffix": "m", "formula": "1 - b3 - 5", "desc": "Mellow, emotional chord"},
        {"id": "7", "label": "Dominant 7th", "suffix": "7", "formula": "1 - 3 - 5 - b7", "desc": "Blues and soul sound"},
        {"id": "maj7", "label": "Major 7th", "suffix": "maj7", "formula": "1 - 3 - 5 - 7", "desc": "Lush, jazzy open sound"},
        {"id": "min7", "label": "Minor 7th", "suffix": "m7", "formula": "1 - b3 - 5 - b7", "desc": "Relaxed, easy open chord"},
        {"id": "sus2", "label": "Suspended 2nd", "suffix": "sus2", "formula": "1 - 2 - 5", "desc": "Open ringing sound, very easy on fingers"},
        {"id": "sus4", "label": "Suspended 4th", "suffix": "sus4", "formula": "1 - 4 - 5", "desc": "Floating, unresolved sound"},
        {"id": "add9", "label": "Add 9", "suffix": "add9", "formula": "1 - 3 - 5 - 9", "desc": "Sparkling acoustic shape"},
        {"id": "6", "label": "Major 6th", "suffix": "6", "formula": "1 - 3 - 5 - 6", "desc": "Warm vintage sound with few fingers"}
    ]


@router.get("/chords/presets")
def get_progression_presets() -> List[Dict[str, Any]]:
    return [
        {
            "id": "barre_gauntlet",
            "name": "Tough Barre Chords (F, Bm, F#m, C#m)",
            "difficulty": "Hard (All Barre Chords)",
            "description": "4 tough barre chords in a row that tire out your hands. Watch Octave replace every single barre with an easy shape!"
        },
        {
            "id": "pop_anthem",
            "name": "Classic Pop (C, G, Am, F)",
            "difficulty": "Moderate (Tough F Barre)",
            "description": "The most famous progression in modern music. Eliminates the painful F major barre chord while sounding smooth and full."
        },
        {
            "id": "jazz_turnaround",
            "name": "Smooth Jazz (Dm7, G7, Cmaj7, A7)",
            "difficulty": "Moderate (Wide Reach)",
            "description": "A classic jazz progression arranged so your fingers barely have to shift across the fretboard."
        },
        {
            "id": "folk_rock",
            "name": "Acoustic Folk (G, D, Em, C)",
            "difficulty": "Easy (Gentle Stretch)",
            "description": "Keeps your anchor fingers planted in place, making chord transitions smooth and effortless."
        },
        {
            "id": "andalusian",
            "name": "Spanish Walkdown (Am, G, F, E)",
            "difficulty": "Moderate (Tough F Transition)",
            "description": "A classic descending chord pattern made comfortable by swapping out the stiff F barre chord."
        },
        {
            "id": "indie_rock",
            "name": "Acoustic Rock (Bm, G, D, A)",
            "difficulty": "Moderate (Tough Bm Barre)",
            "description": "Replaces the stiff Bm barre chord with a comfortable open ringing shape for easy strumming."
        }
    ]


@router.post("/optimize", response_model=OptimizationTelemetry)
def post_optimize(request: ProgressionOptimizeRequest) -> OptimizationTelemetry:
    if not request.chords:
        raise HTTPException(status_code=400, detail="Progression must contain at least one chord.")
    
    # Resolve HandProfile
    profile = PRESET_PROFILES.get(request.profile_id or "arthritis_moderate")
    if request.custom_profile:
        try:
            profile = HandProfile(**request.custom_profile)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid custom hand profile: {str(e)}")
            
    if profile is None:
        profile = PRESET_PROFILES["arthritis_moderate"]
        
    return optimize_progression(request.chords, profile)


@router.get("/evaluate/chord/{chord_name}")
def get_evaluate_chord(chord_name: str, profile_id: str = "arthritis_moderate") -> Dict[str, Any]:
    profile = PRESET_PROFILES.get(profile_id, PRESET_PROFILES["arthritis_moderate"])
    standard, alts = get_voicings_for_chord(chord_name)
    
    std_strain = evaluate_chord_biomechanics(standard, profile)
    alts_with_strain = [
        {
            "voicing": alt,
            "strain": evaluate_chord_biomechanics(alt, profile)
        }
        for alt in alts
    ]
    
    return {
        "chord": chord_name,
        "standard": {
            "voicing": standard,
            "strain": std_strain
        },
        "alternatives": alts_with_strain
    }
