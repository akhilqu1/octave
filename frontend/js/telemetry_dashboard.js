/**
 * octave Biomechanical Telemetry Dashboard
 * Renders quantitative physiological strain readouts, comparison gauges,
 * and transition telemetry for both standard and ergonomic chord voicings.
 */

export class TelemetryDashboard {
  constructor() {
    this.bannerContainer = document.getElementById("telemetry-banner");
    this.specBaselineContainer = document.getElementById("spec-baseline");
    this.specOptimizedContainer = document.getElementById("spec-optimized");
    this.transitionMetricsContainer = document.getElementById("transition-metrics");
  }

  updateGlobalSummary(telemetry) {
    if (!this.bannerContainer) return;

    this.bannerContainer.innerHTML = `
      <div class="telemetry-card highlight">
        <span class="telemetry-label">Strain Reduction</span>
        <span class="telemetry-value positive">-${telemetry.total_strain_reduction_pct}%</span>
        <span class="telemetry-subtext">Biomechanical load relief</span>
      </div>

      <div class="telemetry-card highlight-blue">
        <span class="telemetry-label">Finger Travel Saved</span>
        <span class="telemetry-value blue">-${telemetry.travel_reduction_pct}%</span>
        <span class="telemetry-subtext">${telemetry.optimized_total_travel}mm vs ${telemetry.baseline_total_travel}mm</span>
      </div>

      <div class="telemetry-card">
        <span class="telemetry-label">Barres Eliminated</span>
        <span class="telemetry-value ${telemetry.barres_eliminated_count > 0 ? 'positive' : ''}">${telemetry.barres_eliminated_count}</span>
        <span class="telemetry-subtext">Clamps dropped entirely</span>
      </div>

      <div class="telemetry-card">
        <span class="telemetry-label">Open Resonant Strings</span>
        <span class="telemetry-value positive">+${telemetry.open_strings_gained_count}</span>
        <span class="telemetry-subtext">Zero-effort vibrating notes</span>
      </div>
    `;
  }

  updateStepDetails(stepResult) {
    const std = stepResult.standard_voicing;
    const stdStrain = stepResult.standard_strain;
    const opt = stepResult.optimized_voicing;
    const optStrain = stepResult.optimized_strain;
    const trans = stepResult.transition_from_prev;

    if (this.specBaselineContainer) {
      const stdBarreClass = stdStrain.is_barre_active ? "danger" : "success";
      const stdBarreText = stdStrain.is_barre_active 
        ? `HIGH ISOMETRIC (${stdStrain.barre_strings_count} Strings)` 
        : "RELAXED";

      this.specBaselineContainer.innerHTML = `
        <div class="spec-title">
          <span>Standard Voicing (${std.chord_name})</span>
          <span class="card-badge">Textbook</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Fret Span:</span>
          <span class="spec-val">${stdStrain.fret_span} frets</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Barre Clamping:</span>
          <span class="barre-badge ${stdBarreClass}">${stdBarreText}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Fingering Code:</span>
          <span class="spec-val font-mono">${stdStrain.fingering_notation}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Span Penalty:</span>
          <span class="spec-val">${stdStrain.span_penalty.toFixed(1)}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Barre Torque Cost:</span>
          <span class="spec-val ${stdStrain.barre_torque_penalty > 0 ? 'text-red-400' : ''}">${stdStrain.barre_torque_penalty.toFixed(1)}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Total Biomechanical Load:</span>
          <span class="spec-val font-bold text-amber-400">${stdStrain.total_chord_strain.toFixed(1)} pts</span>
        </div>
      `;
    }

    if (this.specOptimizedContainer) {
      const optBarreClass = optStrain.is_barre_active ? "danger" : "success";
      const optBarreText = optStrain.is_barre_active 
        ? `ISOMETRIC (${optStrain.barre_strings_count} Strings)` 
        : "RELAXED (NO BARRE)";

      this.specOptimizedContainer.innerHTML = `
        <div class="spec-title">
          <span>Optimized Shape (${opt.chord_name})</span>
          <span class="card-badge" style="color:var(--accent-primary); border-color:var(--accent-primary-border); background:var(--accent-primary-subtle); font-weight:700;">-${stepResult.strain_reduction_pct}% Strain</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Fret Span:</span>
          <span class="spec-val font-bold" style="color:var(--accent-primary);">${optStrain.fret_span} frets</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Barre Status:</span>
          <span class="barre-badge ${optBarreClass}">${optBarreText}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Fingering Code:</span>
          <span class="spec-val font-mono" style="color:var(--accent-primary); font-weight:700;">${optStrain.fingering_notation}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Category / Strategy:</span>
          <span class="spec-val">${opt.voicing_category}</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Open String Relief:</span>
          <span class="spec-val" style="color:var(--accent-primary); font-weight:600;">-${optStrain.open_string_bonus.toFixed(1)} pts</span>
        </div>
        <div class="spec-row">
          <span class="spec-key">Total Biomechanical Load:</span>
          <span class="spec-val font-bold" style="color:var(--accent-primary);">${optStrain.total_chord_strain.toFixed(1)} pts</span>
        </div>
      `;
    }

    if (this.transitionMetricsContainer) {
      if (trans) {
        const pivotLabels = trans.pivot_fingers.map(f => `Digit ${f}`).join(", ") || "None";
        this.transitionMetricsContainer.innerHTML = `
          <div style="font-size:0.8rem; color:var(--text-secondary); display:flex; justify-content:space-between; flex-wrap:wrap; gap:0.5rem; align-items:center;">
            <span><strong>Transition Travel:</strong> ${trans.finger_travel_distance}mm</span>
            <span><strong>Hand Neck Shift:</strong> ${trans.hand_shift_frets} frets</span>
            <span><strong>Static Pivot Anchors:</strong> <span style="color:var(--accent-primary); font-weight:700;">${trans.pivot_finger_count} (${pivotLabels})</span></span>
          </div>
        `;
      } else {
        this.transitionMetricsContainer.innerHTML = `
          <div style="font-size:0.8rem; color:var(--text-muted);">Initial progression chord (starting hand position).</div>
        `;
      }
    }
  }
}
