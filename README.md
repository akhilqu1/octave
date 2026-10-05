# octave — Ergonomic Guitar Fretboard Optimizer

**octave** is a production-grade, human-factors-engineered web application and biomechanical intelligence engine designed to assist lifelong guitarists experiencing physical constraints—such as osteoarthritis, rheumatoid arthritis, flexor/extensor tendonitis, focal hand dystonia, carpal tunnel syndrome, or age-related joint stiffness.

The application mathematically re-voices chord progressions into low-torque, low-strain physical configurations while preserving harmonic identity.

---

## System Architecture

octave uses a decoupled, service-oriented architecture:

```
octave/
├── backend/
│   ├── main.py                  # FastAPI application entry point & static frontend host
│   ├── models/
│   │   ├── chord.py             # ChordVoicing, BarreDetail, ChordRequestItem
│   │   ├── hand_profile.py      # HandProfile, Clinical Presets (Arthritis, Tendonitis, Dystonia)
│   │   └── telemetry.py         # BiomechanicalStrainBreakdown, TransitionMetrics, OptimizationTelemetry
│   ├── engine/
│   │   ├── music_theory.py      # Chromatic pitch math, tuning matrices, interval spellings
│   │   ├── harmonic_library.py  # Standard textbook vs ergonomic voicings across all 12 keys
│   │   ├── biomechanics.py      # Fret span penalty, barre isometric torque, digit-specific strain
│   │   ├── transition_solver.py # Dynamic finger travel distance, pivot anchors, hand center shift
│   │   └── optimizer.py         # Global Dynamic Programming (Viterbi Trellis) voice-leading solver
│   └── api/
│       └── routes.py            # REST API endpoints (/api/optimize, /api/chords, /api/profiles)
├── frontend/
│   ├── index.html               # Semantic, high-contrast, accessible user interface
│   ├── css/
│   │   ├── styles.css           # Glassmorphic dark theme, responsive grid, large tactile hit targets
│   │   └── fretboard.css        # Vector SVG guitar neck styling, string gauges, finger colors
│   └── js/
│       ├── audio_engine.js      # Web Audio API polyphonic physical acoustic string synthesis
│       ├── fretboard_view.js    # Interactive SVG fretboard with finger numbers (1-4), inlays, motion trails
│       ├── telemetry_dashboard.js # Quantitative strain telemetry meters & comparison cards
│       ├── progression_manager.js # Progression sequencer, drag/order, chromatic chord selector modal
│       ├── api_client.js        # Asynchronous backend API communication layer
│       └── app.js               # Application orchestrator and event hub
├── tests/                       # Complete pytest test suite (19 unit & integration tests)
├── requirements.txt             # Frozen dependencies
└── README.md
```

---

## Biomechanical Cost Engine

The computational core calculates physiological strain using multi-factor biomechanical load modeling:

1. **Exponential Fret Span Penalty**:
   $$\text{Span} = \max(\text{frets}) - \min(\text{frets}) \quad (\text{for frets } > 0)$$
   - Spans of 1–2 frets: low strain ($0.15 \times \text{span}$)
   - Spans of 3 frets: moderate penalty ($1.2$)
   - Spans $\ge 4$ frets: exponential penalty ($2.5 \cdot e^{1.2 \cdot (\text{span} - 3)}$)
   - Exceeding user configured `max_fret_span`: critical penalty ($+35.0 \cdot \Delta\text{span}$)

2. **Barre Chord Isometric Torque Penalty**:
   - Clamping the index finger across 4 to 6 strings demands high sustained isometric pinch force from the adductor pollicis and flexor digitorum superficialis.
   - 6-string barres incur heavy base friction penalties ($11.5 \times \text{sensitivity}$).
   - When the user toggles **Ban Barre Chords**, any multi-string clamp receives a prohibitive barrier cost ($+80.0$).

3. **Dynamic Finger Travel Distance & Pivot Anchoring**:
   - When moving between consecutive chords, each finger's 2D displacement along the neck is computed:
     $$d_f = \sqrt{(\Delta \text{string} \cdot 10.5\text{mm})^2 + (\Delta \text{fret} \cdot 22.0\text{mm})^2}$$
   - **Static Pivot Bonus**: Fingers remaining on the exact same string and fret between shapes receive anchor rewards, providing tactile orientation and eliminating repositioning friction.

4. **Digit-Specific Torque Constraints**:
   - Index (1.0), Middle (1.1), Ring (1.5), Pinky (2.6).
   - Pinky reach to low bass strings (Low E, A) causes lateral tendon shear and carpal canal compression; penalized heavily.
   - Per-finger mobility restrictions (e.g. 0% for focal dystonia) eliminate pinky fretting entirely.

5. **Open String Resonant Relief**:
   - Open strings ring with zero finger pressure; each active open string discounts strain ($-0.75$).

---

## Dynamic Programming Trellis Solver

The global progression optimizer constructs a multi-stage trellis graph:
- **Stages $t$**: Each chord in the sequence.
- **Nodes $V_t$**: Standard textbook shape + all harmonic candidate voicings (open drones, compact triads, extensions).
- **Edges**: Transition cost including finger travel, longitudinal hand shifts, and pivot preservation.
- Solves the Viterbi recurrence to find the sequence minimizing:
  $$C_{\text{total}} = \sum_{t=1}^{N} \text{Strain}(V_t) + \lambda \sum_{t=1}^{N-1} \text{Transition}(V_t, V_{t+1})$$

---

## Polyphonic Web Audio Synthesis

- Accurate physical pitch frequencies for standard tuning:
  - Low E ($E_2$ = 82.41 Hz), A ($A_2$ = 110.00 Hz), D ($D_3$ = 146.83 Hz), G ($G_3$ = 196.00 Hz), B ($B_3$ = 246.94 Hz), High e ($E_4$ = 329.63 Hz).
- Harmonic overtones (fundamental + octave + shimmer harmonics) with dynamic low-pass envelope closing (string damping).
- Acoustic guitar wooden body resonance filter (~115 Hz cavity resonance peak).
- Strum simulation: arpeggiated 26ms micro-delays per string with synchronous SVG string vibration animations.

---

## Running the Application

### 1. Launch Server
```powershell
# Activate environment and start server
.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Access the Application
Open your browser to:
```
http://127.0.0.1:8000
```

### 3. Run Automated Tests
```powershell
.venv\Scripts\python.exe -m pytest -v
```
