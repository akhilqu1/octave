import io
import struct
from typing import Dict, List, Set, Tuple
from backend.engine.music_theory import (
    PITCH_CLASSES_SHARP,
    NOTE_TO_SEMITONE,
    CHORD_INTERVALS
)


def read_variable_length(stream: io.BytesIO) -> int:
    """Reads a variable-length quantity from a MIDI stream."""
    value = 0
    while True:
        byte_data = stream.read(1)
        if not byte_data:
            return value
        byte = byte_data[0]
        value = (value << 7) | (byte & 0x7F)
        if not (byte & 0x80):
            break
    return value


def identify_chord_from_pitch_classes(pitch_classes: Set[int]) -> str:
    """
    Given a set of semitones (0-11), detects the most likely chord name.
    e.g. {0, 4, 7} -> 'C', {9, 0, 4} -> 'Am', {5, 9, 0} -> 'F'
    """
    if not pitch_classes:
        return "C"

    # Pass 1: Exact matches (prioritize major and minor triads, then 7ths/extensions)
    quality_order = ["major", "minor", "7", "maj7", "min7", "sus2", "sus4", "add9"]
    for quality in quality_order:
        for root_semitone in range(12):
            root_name = PITCH_CLASSES_SHARP[root_semitone]
            intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])
            chord_pcs = {(root_semitone + iv) % 12 for iv in intervals}
            if chord_pcs == pitch_classes:
                if quality == "major": return root_name
                elif quality == "minor": return f"{root_name}m"
                elif quality == "7": return f"{root_name}7"
                elif quality == "maj7": return f"{root_name}maj7"
                elif quality == "min7": return f"{root_name}m7"
                elif quality == "sus2": return f"{root_name}sus2"
                elif quality == "sus4": return f"{root_name}sus4"
                elif quality == "add9": return f"{root_name}add9"

    # Pass 2: Chord notes are a subset of played notes (e.g. triad contained in larger voicing)
    for quality in quality_order:
        for root_semitone in range(12):
            root_name = PITCH_CLASSES_SHARP[root_semitone]
            intervals = CHORD_INTERVALS.get(quality, [0, 4, 7])
            chord_pcs = {(root_semitone + iv) % 12 for iv in intervals}
            if chord_pcs.issubset(pitch_classes):
                if quality == "major": return root_name
                elif quality == "minor": return f"{root_name}m"
                elif quality == "7": return f"{root_name}7"
                elif quality == "maj7": return f"{root_name}maj7"
                elif quality == "min7": return f"{root_name}m7"
                elif quality == "sus2": return f"{root_name}sus2"
                elif quality == "sus4": return f"{root_name}sus4"
                elif quality == "add9": return f"{root_name}add9"

    # Fallback to the lowest pitch class as root major
    first_pc = sorted(list(pitch_classes))[0]
    return PITCH_CLASSES_SHARP[first_pc]


def parse_midi_bytes(midi_data: bytes) -> List[str]:
    """
    Parses raw bytes of a Standard MIDI File (.mid) and extracts chronological chord progression.
    """
    stream = io.BytesIO(midi_data)

    # 1. Read Header chunk (MThd)
    header_magic = stream.read(4)
    if header_magic != b'MThd':
        # Fallback if raw text or not valid MIDI header
        return ["C", "G", "Am", "F"]

    header_length, format_type, num_tracks, division = struct.unpack(">IHHH", stream.read(10))

    # Notes list: (tick_time, pitch, event_type)
    all_events: List[Tuple[int, int, str]] = []

    # 2. Read Track chunks (MTrk)
    for _ in range(num_tracks):
        track_magic = stream.read(4)
        if track_magic != b'MTrk':
            break
        track_length, = struct.unpack(">I", stream.read(4))
        track_data = io.BytesIO(stream.read(track_length))

        current_tick = 0
        running_status = None

        while True:
            delta = read_variable_length(track_data)
            current_tick += delta

            status_byte = track_data.read(1)
            if not status_byte:
                break

            status = status_byte[0]
            if status < 0x80:
                # Running status
                if running_status is None:
                    break
                data1 = status
                status = running_status
            else:
                data1_byte = track_data.read(1)
                if not data1_byte:
                    break
                data1 = data1_byte[0]
                if status < 0xF0:
                    running_status = status

            # Handle Event Types
            event_type = status & 0xF0
            if event_type in (0x80, 0x90):  # Note Off or Note On
                data2_byte = track_data.read(1)
                if not data2_byte:
                    break
                data2 = data2_byte[0]
                velocity = data2
                pitch = data1

                if event_type == 0x90 and velocity > 0:
                    all_events.append((current_tick, pitch, 'on'))
                else:
                    all_events.append((current_tick, pitch, 'off'))
            elif event_type in (0xA0, 0xB0, 0xE0):
                track_data.read(1)  # 2 data bytes total
            elif event_type in (0xC0, 0xD0):
                pass  # 1 data byte total (already read data1)
            elif status == 0xFF:  # Meta Event
                meta_type = data1
                meta_len = read_variable_length(track_data)
                track_data.read(meta_len)
            elif status in (0xF0, 0xF7):  # Sysex
                sysex_len = read_variable_length(track_data)
                track_data.read(sysex_len)

    if not all_events:
        return ["C", "G", "Am", "F"]

    # 3. Group events into time windows (clusters of notes played closely together)
    all_events.sort(key=lambda x: x[0])
    
    chord_groups: List[Set[int]] = []
    current_chord_notes: Set[int] = set()
    last_tick = -1
    TICK_THRESHOLD = division // 2 if division > 0 else 240

    for tick, pitch, ev_type in all_events:
        if ev_type == 'on':
            pc = pitch % 12
            if last_tick < 0 or (tick - last_tick) <= TICK_THRESHOLD:
                current_chord_notes.add(pc)
                if last_tick < 0:
                    last_tick = tick
            else:
                if len(current_chord_notes) >= 2:
                    chord_groups.append(set(current_chord_notes))
                elif len(current_chord_notes) == 1:
                    chord_groups.append(set(current_chord_notes))
                current_chord_notes = {pc}
                last_tick = tick

    if current_chord_notes:
        chord_groups.append(current_chord_notes)

    # 4. Convert chord note sets to chord names
    result_chords: List[str] = []
    for pcs in chord_groups:
        chord_name = identify_chord_from_pitch_classes(pcs)
        # Avoid immediate duplicate consecutive chords
        if not result_chords or result_chords[-1] != chord_name:
            result_chords.append(chord_name)

    # Fallback to standard progression if too few chords detected
    if not result_chords:
        return ["C", "G", "Am", "F"]

    return result_chords[:12]  # Limit to 12 chords max for smooth progression
