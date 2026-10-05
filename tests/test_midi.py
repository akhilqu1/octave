import struct
from backend.engine.midi_parser import parse_midi_bytes, identify_chord_from_pitch_classes
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def create_minimal_midi_bytes() -> bytes:
    """Constructs a valid format 0 MIDI binary file with a C major chord."""
    header = struct.pack(">4sIHHH", b'MThd', 6, 0, 1, 480)
    
    # Track events:
    # delta 0, note on C4 (60), vel 64
    # delta 0, note on E4 (64), vel 64
    # delta 0, note on G4 (67), vel 64
    # delta 480, note off C4
    # delta 0, note off E4
    # delta 0, note off G4
    # delta 0, end of track FF 2F 00
    events = (
        b'\x00\x90\x3c\x40' +
        b'\x00\x90\x40\x40' +
        b'\x00\x90\x43\x40' +
        b'\x83\x60\x80\x3c\x00' +
        b'\x00\x80\x40\x00' +
        b'\x00\x80\x43\x00' +
        b'\x00\xff\x2f\x00'
    )
    track_header = struct.pack(">4sI", b'MTrk', len(events))
    return header + track_header + events


def test_identify_chord():
    assert identify_chord_from_pitch_classes({0, 4, 7}) == "C"
    assert identify_chord_from_pitch_classes({9, 0, 4}) == "Am"
    assert identify_chord_from_pitch_classes({5, 9, 0}) == "F"


def test_parse_midi_bytes():
    midi_data = create_minimal_midi_bytes()
    chords = parse_midi_bytes(midi_data)
    assert len(chords) >= 1
    assert "C" in chords


def test_midi_api_endpoint():
    midi_data = create_minimal_midi_bytes()
    res = client.post("/api/midi/parse", content=midi_data, headers={"content-type": "application/octet-stream"})
    assert res.status_code == 200
    data = res.json()
    assert "chords" in data
    assert len(data["chords"]) >= 1
