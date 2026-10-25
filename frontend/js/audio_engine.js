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

    // Acoustic Guitar Body Cavity Resonance (~105Hz air resonance)
    this.bodyAirFilter = this.audioCtx.createBiquadFilter();
    this.bodyAirFilter.type = "peaking";
    this.bodyAirFilter.frequency.setValueAtTime(105, this.audioCtx.currentTime);
    this.bodyAirFilter.Q.setValueAtTime(2.0, this.audioCtx.currentTime);
    this.bodyAirFilter.gain.setValueAtTime(4.5, this.audioCtx.currentTime);

    // Acoustic Spruce Top Soundboard Resonance (~215Hz plate wood resonance)
    this.bodyPlateFilter = this.audioCtx.createBiquadFilter();
    this.bodyPlateFilter.type = "peaking";
    this.bodyPlateFilter.frequency.setValueAtTime(215, this.audioCtx.currentTime);
    this.bodyPlateFilter.Q.setValueAtTime(1.6, this.audioCtx.currentTime);
    this.bodyPlateFilter.gain.setValueAtTime(3.2, this.audioCtx.currentTime);

    this.bodyAirFilter.connect(this.bodyPlateFilter);
    this.bodyPlateFilter.connect(this.masterGain);
    this.masterGain.connect(this.audioCtx.destination);
  }

  async resume() {
    if (!this.audioCtx) this.init();
    if (this.audioCtx.state === "suspended") {
      await this.audioCtx.resume();
    }
  }

  /**
   * Synthesizes a single plucked guitar string with physical harmonic decay & pick attack.
   */
  pluckString(frequency, startTime, duration = 2.4, isMuted = false, stringIdx = 0) {
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
      gain.connect(this.bodyAirFilter);
      osc.start(now);
      osc.stop(now + 0.07);
      return;
    }

    // 1. Pick Attack Transient Noise Impulse (~3ms plectrum snap)
    try {
      const bufferSize = Math.floor(this.audioCtx.sampleRate * 0.008);
      const noiseBuffer = this.audioCtx.createBuffer(1, bufferSize, this.audioCtx.sampleRate);
      const output = noiseBuffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        output[i] = (Math.random() * 2 - 1) * Math.exp(-i / (bufferSize * 0.25));
      }
      const noiseNode = this.audioCtx.createBufferSource();
      noiseNode.buffer = noiseBuffer;

      const pickFilter = this.audioCtx.createBiquadFilter();
      pickFilter.type = "bandpass";
      pickFilter.frequency.setValueAtTime(Math.min(3500, frequency * 4), now);
      pickFilter.Q.setValueAtTime(3.0, now);

      const pickGain = this.audioCtx.createGain();
      pickGain.gain.setValueAtTime(0.08, now);
      pickGain.gain.exponentialRampToValueAtTime(0.001, now + 0.008);

      noiseNode.connect(pickFilter);
      pickFilter.connect(pickGain);
      pickGain.connect(this.bodyAirFilter);
      noiseNode.start(now);
      noiseNode.stop(now + 0.01);
    } catch (_) {}

    // 2. Physical String Modeling with Harmonic Decay
    const filter = this.audioCtx.createBiquadFilter();
    filter.type = "lowpass";
    const initialCutoff = Math.min(8500, frequency * 7);
    filter.frequency.setValueAtTime(initialCutoff, now);
    filter.frequency.exponentialRampToValueAtTime(frequency * 1.6, now + duration * 0.45);

    const stringGain = this.audioCtx.createGain();
    stringGain.gain.setValueAtTime(0.001, now);
    stringGain.gain.linearRampToValueAtTime(0.36, now + 0.003); // crisp attack
    stringGain.gain.exponentialRampToValueAtTime(0.0001, now + duration);

    // Fundamental (sawtooth for wound bronze string bite)
    const osc1 = this.audioCtx.createOscillator();
    osc1.type = "sawtooth";
    osc1.frequency.setValueAtTime(frequency, now);

    // 2nd Harmonic (Octave acoustic chime)
    const osc2 = this.audioCtx.createOscillator();
    osc2.type = "sine";
    osc2.frequency.setValueAtTime(frequency * 2.008, now); // slight organic chorus detune
    const osc2Gain = this.audioCtx.createGain();
    osc2Gain.gain.setValueAtTime(0.24, now);
    osc2Gain.gain.exponentialRampToValueAtTime(0.001, now + duration * 0.6);

    // 3rd Harmonic (Fifth harmonic sparkle)
    const osc3 = this.audioCtx.createOscillator();
    osc3.type = "sine";
    osc3.frequency.setValueAtTime(frequency * 3.015, now);
    const osc3Gain = this.audioCtx.createGain();
    osc3Gain.gain.setValueAtTime(0.12, now);
    osc3Gain.gain.exponentialRampToValueAtTime(0.001, now + duration * 0.4);

    osc1.connect(filter);
    osc2.connect(osc2Gain);
    osc2Gain.connect(filter);
    osc3.connect(osc3Gain);
    osc3Gain.connect(filter);

    filter.connect(stringGain);
    stringGain.connect(this.bodyAirFilter);

    osc1.start(now);
    osc2.start(now);
    osc3.start(now);
    osc1.stop(now + duration + 0.1);
    osc2.stop(now + duration + 0.1);
    osc3.stop(now + duration + 0.1);
  }

  /**
   * Plays a full chord voicing with realistic arpeggiated strumming and human micro-delays.
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
        continue;
      }

      // Humanized micro-jitter (0-3ms)
      const jitterMs = (Math.random() * 3.5);
      const stringTime = startTime + (delayIndex * (strumSpeedMs / 1000)) + (jitterMs / 1000);
      this.pluckString(freq, stringTime, 2.5, false, strIdx);

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
