from backend.engine.music_theory import (
    parse_chord_string,
    format_chord_display,
    get_notes_for_chord,
    get_string_fret_pitch,
    midi_to_frequency,
    STANDARD_TUNING_MIDI,
)


def test_parse_chord_string():
    assert parse_chord_string("C") == ("C", "major")
    assert parse_chord_string("F#m") == ("F#", "minor")
    assert parse_chord_string("Bbmaj7") == ("Bb", "maj7")
    assert parse_chord_string("Gsus4") == ("G", "sus4")
    assert parse_chord_string("Dsus2") == ("D", "sus2")
    assert parse_chord_string("Cadd9") == ("C", "add9")
    assert parse_chord_string("E7") == ("E", "7")
    assert parse_chord_string("Am7") == ("A", "min7")


def test_format_chord_display():
    assert format_chord_display("C", "major") == "C"
    assert format_chord_display("A", "minor") == "Am"
    assert format_chord_display("G", "7") == "G7"
    assert format_chord_display("F", "maj7") == "Fmaj7"
    assert format_chord_display("B", "min7") == "Bm7"
    assert format_chord_display("D", "sus2") == "Dsus2"


def test_get_notes_for_chord():
    c_major = get_notes_for_chord("C", "major")
    assert c_major == ["C", "E", "G"]
    
    a_minor = get_notes_for_chord("A", "minor")
    assert a_minor == ["A", "C", "E"]
    
    g_7 = get_notes_for_chord("G", "7")
    assert g_7 == ["G", "B", "D", "F"]


def test_midi_to_frequency():
    assert midi_to_frequency(69) == 440.0  # A4
    assert midi_to_frequency(40) == 82.41  # E2 (Low E string)
    assert midi_to_frequency(64) == 329.63 # E4 (High e string)


def test_get_string_fret_pitch():
    # String 0 (Low E open)
    note, freq, midi = get_string_fret_pitch(0, 0)
    assert note == "E2"
    assert midi == 40
    assert abs(freq - 82.41) < 0.1
    
    # String 0 fret 1 (F)
    note, freq, midi = get_string_fret_pitch(0, 1)
    assert note == "F2"
    assert midi == 41
    
    # String 5 fret 0 (High e open)
    note, freq, midi = get_string_fret_pitch(5, 0)
    assert note == "E4"
    assert midi == 64
    
    # Muted string
    note, freq, midi = get_string_fret_pitch(0, -1)
    assert note == "X"
    assert freq == 0.0
    assert midi is None
