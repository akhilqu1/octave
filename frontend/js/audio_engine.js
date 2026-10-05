/**
 * octave Audio Engine
 * High-fidelity polyphonic Web Audio API string synthesis.
 * Implements physical acoustic guitar pluck simulation with harmonic overtones,
 * string damping, body resonance filtering, and realistic strum micro-delays.
 */

class GuitarAudioEngine {
  constructor() {
    this.audioCtx = null;
    this.masterGain = null;
    this.bodyFilter = null;
    this.isPlayingProgression = false;
    this.progressionTimer = null;
  }

  init() {
    if (this.audioCtx) return;
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    this.audioCtx = new AudioContext();

    // Master volume
    this.masterGain = this.audioCtx.createGain();
    this.masterGain.gain.setValueAtTime(0.75, this.audioCtx.currentTime);

    // Acoustic Guitar Body Resonance Filter (~110Hz body cavity air resonance)
    this.bodyFilter = this.audioCtx.createBiquadFilter();
    this.bodyFilter.type = "peaking";
    this.bodyFilter.frequency.setValueAtTime(115, this.audioCtx.currentTime);
    this.bodyFilter.Q.setValueAtTime(1.8, this.audioCtx.currentTime);
    this.bodyFilter.gain.setValueAtTime(4.0, this.audioCtx.currentTime);

    this.bodyFilter.connect(this.masterGain);
    this.masterGain.connect(this.audioCtx.destination);
  }

  async resume() {
    if (!this.audioCtx) this.init();
    if (this.audioCtx.state === "suspended") {
      await this.audioCtx.resume();
    }
  }

  /**
   * Synthesizes a single plucked guitar string with physical harmonic decay.
   */
  pluckString(frequency, startTime, duration = 2.2, isMuted = false, stringIdx = 0) {
    if (!frequency || frequency <= 0) return;
    this.resume();

    const now = startTime;

    if (isMuted) {
      // Percussive string tap / fret damp thud
      const osc = this.audioCtx.createOscillator();
      const gain = this.audioCtx.createGain();
      osc.type = "triangle";
      osc.frequency.setValueAtTime(80, now);
      osc.frequency.exponentialRampToValueAtTime(30, now + 0.05);

      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.06);

      osc.connect(gain);
      gain.connect(this.bodyFilter);
      osc.start(now);
      osc.stop(now + 0.07);
      return;
    }

    // Polyphonic Physical Modeling:
    // Plucked string consists of fundamental + 2nd harmonic (octave) + 3rd harmonic
    // with a fast dynamic lowpass filter closing down (damping).
    const filter = this.audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    
    // Low strings ring darker, treble strings brighter
    const initialCutoff = Math.min(8000, frequency * 6);
    filter.frequency.setValueAtTime(initialCutoff, now);
    // Damping envelope: brightness decays rapidly
    filter.frequency.exponentialRampToValueAtTime(frequency * 1.5, now + duration * 0.4);

    const stringGain = this.audioCtx.createGain();
    stringGain.gain.setValueAtTime(0.001, now);
    // Quick pluck attack (~3ms)
    stringGain.gain.linearRampToValueAtTime(0.35, now + 0.004);
    // Exponential string decay
    stringGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    // Fundamental oscillator (sawtooth/triangle hybrid for steel string buzz)
    const osc1 = this.audioCtx.createOscillator();
    osc1.type = "sawtooth";
    osc1.frequency.setValueAtTime(frequency, now);

    // 2nd harmonic overtone for acoustic shimmer
    const osc2 = this.audioCtx.createOscillator();
    osc2.type = "sine";
    osc2.frequency.setValueAtTime(frequency * 2.01, now); // slight detune for chorus warmth
    const osc2Gain = this.audioCtx.createGain();
    osc2Gain.gain.setValueAtTime(0.2, now);
    osc2Gain.gain.exponentialRampToValueAtTime(0.001, now + duration * 0.6);

    osc1.connect(filter);
    osc2.connect(osc2Gain);
    osc2Gain.connect(filter);

    filter.connect(stringGain);
    stringGain.connect(this.bodyFilter);

    osc1.start(now);
    osc2.start(now);
    osc1.stop(now + duration + 0.1);
    osc2.stop(now + duration + 0.1);
  }

  /**
   * Plays a full chord voicing with realistic arpeggiated strumming.
   * @param {Object} voicing - ChordVoicing object with frets and pitches_hz
   * @param {number} strumSpeedMs - Micro-delay between strings (default 26ms)
   * @param {Function} onStringPluck - Callback for UI string vibration animation
   */
  async playChord(voicing, strumSpeedMs = 26, onStringPluck = null) {
    await this.resume();
    const startTime = this.audioCtx.currentTime + 0.02;
    const pitches = voicing.pitches_hz || [];
    const frets = voicing.frets || [];

    let delayIndex = 0;
    for (let strIdx = 0; strIdx < 6; strIdx++) {
      const fret = frets[strIdx];
      const freq = pitches[strIdx];

      if (fret === -1) {
        // String is muted
        continue;
      }

      const stringTime = startTime + (delayIndex * (strumSpeedMs / 1000));
      this.pluckString(freq, stringTime, 2.4, false, strIdx);

      if (onStringPluck) {
        const triggerDelayMs = (delayIndex * strumSpeedMs) + 20;
        setTimeout(() => {
          onStringPluck(strIdx, freq);
        }, triggerDelayMs);
      }

      delayIndex++;
    }
  }

  /**
   * Plays A/B comparison: Standard Textbook voicing, pause, then Ergonomic Low-Strain voicing.
   */
  async playABComparison(standardVoicing, optimizedVoicing, onStateChange = null) {
    await this.resume();
    if (onStateChange) onStateChange("standard");
    await this.playChord(standardVoicing);

    setTimeout(async () => {
      if (onStateChange) onStateChange("optimized");
      await this.playChord(optimizedVoicing);
      setTimeout(() => {
        if (onStateChange) onStateChange("idle");
      }, 1800);
    }, 1900);
  }

  stopProgression() {
    this.isPlayingProgression = false;
    if (this.progressionTimer) {
      clearTimeout(this.progressionTimer);
      this.progressionTimer = null;
    }
  }
}

// Export singleton
window.guitarAudio = new GuitarAudioEngine();
