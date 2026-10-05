/**
 * octave API Client
 * Clean asynchronous HTTP client communicating with FastAPI backend.
 */

const API_BASE = (window.location && window.location.protocol.startsWith("http"))
  ? "" 
  : "http://127.0.0.1:8000";

export class OctaveApiClient {
  static async getHealth() {
    const res = await fetch(`${API_BASE}/api/health`);
    if (!res.ok) throw new Error("Backend health check failed");
    return res.json();
  }

  static async getProfiles() {
    const res = await fetch(`${API_BASE}/api/profiles`);
    if (!res.ok) throw new Error("Failed to load hand profiles");
    return res.json();
  }

  static async getRoots() {
    const res = await fetch(`${API_BASE}/api/chords/roots`);
    if (!res.ok) throw new Error("Failed to load chord roots");
    return res.json();
  }

  static async getQualities() {
    const res = await fetch(`${API_BASE}/api/chords/qualities`);
    if (!res.ok) throw new Error("Failed to load chord qualities");
    return res.json();
  }

  static async getPresets() {
    const res = await fetch(`${API_BASE}/api/chords/presets`);
    if (!res.ok) throw new Error("Failed to load progression presets");
    return res.json();
  }

  static async optimizeProgression(chords, profileId = "arthritis_moderate", customProfile = null) {
    const payload = {
      chords,
      profile_id: profileId,
      custom_profile: customProfile
    };

    const res = await fetch(`${API_BASE}/api/optimize`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || "Optimization calculation failed");
    }

    return res.json();
  }

  static async evaluateChord(chordName, profileId = "arthritis_moderate") {
    const res = await fetch(`${API_BASE}/api/evaluate/chord/${encodeURIComponent(chordName)}?profile_id=${encodeURIComponent(profileId)}`);
    if (!res.ok) throw new Error(`Failed to evaluate chord ${chordName}`);
    return res.json();
  }
}
