/**
 * octave MIDI File Handler
 * Handles drag-and-drop and manual file uploads for standard .mid / .midi files,
 * calling the backend API to automatically extract chronological chord progressions.
 */

export class MidiFileHandler {
  constructor(dropzoneId, fileInputId, onChordsParsed) {
    this.dropzone = document.getElementById(dropzoneId);
    this.fileInput = document.getElementById(fileInputId);
    this.onChordsParsed = onChordsParsed;

    this.initEvents();
  }

  initEvents() {
    if (!this.dropzone) return;

    // Click dropzone to open system file dialog
    this.dropzone.onclick = () => {
      if (this.fileInput) this.fileInput.click();
    };

    // File input selection
    if (this.fileInput) {
      this.fileInput.onchange = (e) => {
        const file = e.target.files[0];
        if (file) this.processFile(file);
      };
    }

    // Drag-over styling
    this.dropzone.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.dropzone.classList.add("drag-active");
    });

    this.dropzone.addEventListener("dragleave", (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.dropzone.classList.remove("drag-active");
    });

    this.dropzone.addEventListener("drop", (e) => {
      e.preventDefault();
      e.stopPropagation();
      this.dropzone.classList.remove("drag-active");

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        this.processFile(files[0]);
      }
    });
  }

  async processFile(file) {
    const statusLabel = document.getElementById("midi-status-label");
    if (statusLabel) {
      statusLabel.textContent = `Reading chords from "${file.name}"...`;
    }

    try {
      const formData = new FormData();
      formData.append("file", file);

      const API_BASE = (window.location && window.location.protocol.startsWith("http"))
        ? "" 
        : "http://127.0.0.1:8000";

      const res = await fetch(`${API_BASE}/api/midi/parse`, {
        method: "POST",
        body: formData
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || "Could not read MIDI file");
      }

      const data = await res.json();
      if (data.chords && data.chords.length > 0) {
        if (statusLabel) {
          statusLabel.innerHTML = `Found <strong>${data.chords.length} chords</strong>: ${data.chords.join(" → ")}`;
        }
        if (this.onChordsParsed) {
          this.onChordsParsed(data.chords);
        }
      } else {
        throw new Error("No chords found in this MIDI file");
      }
    } catch (err) {
      console.error("MIDI parsing error:", err);
      if (statusLabel) {
        statusLabel.textContent = `Could not read file: ${err.message}. Try another .mid file or choose chords above.`;
      }
    }
  }
}
