/**
 * octave Progression Manager
 * Handles interactive authoring of chord progressions:
 * - Dropdown selection (Root + Quality)
 * - Quick-add chord chips
 * - HTML5 drag-and-drop reordering
 * - Tactile arrow reordering & deletion
 */

export class ProgressionManager {
  constructor(boardContainerId, onProgressionChanged) {
    this.container = document.getElementById(boardContainerId);
    this.onProgressionChanged = onProgressionChanged;
    this.chords = ["F", "Bm", "F#m", "C#m"]; // Default iconic high-strain gauntlet
    this.draggedIndex = null;

    this.initDropdownInputs();
    this.initQuickChips();
    this.render();
  }

  setProgression(newChords) {
    this.chords = [...newChords];
    this.render();
    if (this.onProgressionChanged) {
      this.onProgressionChanged(this.chords);
    }
  }

  addChord(chordStr) {
    if (!chordStr) return;
    this.chords.push(chordStr);
    this.render();
    if (this.onProgressionChanged) {
      this.onProgressionChanged(this.chords);
    }
  }

  removeChord(index) {
    if (this.chords.length <= 1) {
      alert("Please keep at least 1 chord in your song.");
      return;
    }
    this.chords.splice(index, 1);
    this.render();
    if (this.onProgressionChanged) {
      this.onProgressionChanged(this.chords);
    }
  }

  moveChord(fromIndex, toIndex) {
    if (toIndex < 0 || toIndex >= this.chords.length) return;
    const moved = this.chords.splice(fromIndex, 1)[0];
    this.chords.splice(toIndex, 0, moved);
    this.render();
    if (this.onProgressionChanged) {
      this.onProgressionChanged(this.chords);
    }
  }

  initDropdownInputs() {
    const addBtn = document.getElementById("add-dropdown-chord-btn");
    const rootSelect = document.getElementById("chord-root-select");
    const qualitySelect = document.getElementById("chord-quality-select");

    if (addBtn && rootSelect && qualitySelect) {
      addBtn.onclick = () => {
        const root = rootSelect.value;
        const qual = qualitySelect.value;
        let chordStr = root;
        if (qual === "minor") chordStr += "m";
        else if (qual === "7") chordStr += "7";
        else if (qual === "maj7") chordStr += "maj7";
        else if (qual === "min7") chordStr += "m7";
        else if (qual === "sus2") chordStr += "sus2";
        else if (qual === "sus4") chordStr += "sus4";
        else if (qual === "add9") chordStr += "add9";
        else if (qual === "6") chordStr += "6";

        this.addChord(chordStr);
      };
    }
  }

  initQuickChips() {
    const chips = document.querySelectorAll(".quick-chip");
    chips.forEach(chip => {
      chip.onclick = () => {
        const chord = chip.dataset.chord;
        if (chord) this.addChord(chord);
      };
    });
  }

  render() {
    if (!this.container) return;

    this.container.innerHTML = "";

    if (this.chords.length === 0) {
      this.container.innerHTML = `<span style="color:var(--text-muted); font-size:0.9rem;">No chords added yet. Click chords above or upload a MIDI file to get started.</span>`;
      return;
    }

    this.chords.forEach((chord, idx) => {
      const card = document.createElement("div");
      card.className = "chord-drag-card";
      card.draggable = true;
      card.dataset.index = idx;

      card.innerHTML = `
        <span class="drag-grip-handle" title="Drag to change order">⋮⋮</span>
        <div style="display:flex; align-items:baseline; gap:0.35rem;">
          <span style="font-size:0.75rem; color:var(--text-muted); font-weight:700;">#${idx + 1}</span>
          <span class="drag-chord-name">${chord}</span>
        </div>
        <div style="display:flex; align-items:center; gap:0.25rem; margin-left:0.5rem;">
          <button class="icon-btn" title="Move left" ${idx === 0 ? 'disabled style="opacity:0.2;"' : ''} data-action="left" style="min-height:26px; height:26px; width:26px; font-size:0.75rem;">◀</button>
          <button class="icon-btn" title="Move right" ${idx === this.chords.length - 1 ? 'disabled style="opacity:0.2;"' : ''} data-action="right" style="min-height:26px; height:26px; width:26px; font-size:0.75rem;">▶</button>
          <button class="drag-card-remove" title="Remove chord" data-action="delete">✕</button>
        </div>
      `;

      // HTML5 Drag & Drop Listeners
      card.addEventListener("dragstart", (e) => {
        this.draggedIndex = idx;
        card.classList.add("dragging");
        e.dataTransfer.effectAllowed = "move";
      });

      card.addEventListener("dragend", () => {
        card.classList.remove("dragging");
        document.querySelectorAll(".chord-drag-card").forEach(c => c.classList.remove("drag-over"));
      });

      card.addEventListener("dragover", (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = "move";
        card.classList.add("drag-over");
      });

      card.addEventListener("dragleave", () => {
        card.classList.remove("drag-over");
      });

      card.addEventListener("drop", (e) => {
        e.preventDefault();
        card.classList.remove("drag-over");
        if (this.draggedIndex !== null && this.draggedIndex !== idx) {
          this.moveChord(this.draggedIndex, idx);
          this.draggedIndex = null;
        }
      });

      // Arrow & Delete buttons
      card.querySelector('[data-action="left"]').onclick = (e) => {
        e.stopPropagation();
        this.moveChord(idx, idx - 1);
      };
      card.querySelector('[data-action="right"]').onclick = (e) => {
        e.stopPropagation();
        this.moveChord(idx, idx + 1);
      };
      card.querySelector('[data-action="delete"]').onclick = (e) => {
        e.stopPropagation();
        this.removeChord(idx);
      };

      this.container.appendChild(card);
    });
  }
}
