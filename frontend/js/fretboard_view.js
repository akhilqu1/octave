/**
 * octave Fretboard Visualizer
 * High-performance vector SVG guitar neck renderer with explicit finger assignments,
 * string gauge variations, inlay markers, barre capsules, and transition motion trails.
 */

export class FretboardVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.width = 860;
    this.height = 190;
    this.numFrets = 12;
    this.fretPositions = [];
    this.stringPositions = [];
    this.currentVoicing = null;
    this.previousVoicing = null;
    this.showTransitions = true;

    this.calculateGeometry();
  }

  calculateGeometry() {
    const nutX = 80;
    const bridgeX = this.width - 25;
    const neckLength = bridgeX - nutX;

    this.fretPositions = [nutX]; // Fret 0 is Nut
    for (let i = 1; i <= this.numFrets; i++) {
      // Guitar physics scale formula: x_n = L * (1 - 2^(-n / 17.817))
      // Adjusted slightly for clear badge readability across upper frets
      const ratio = 1 - Math.pow(2, -i / 14.5);
      this.fretPositions.push(nutX + neckLength * ratio);
    }

    // 6 Strings: Y positions from Low E (str 0) to High e (str 5)
    this.stringPositions = [
      32,  // String 0: Low E (6th string)
      56,  // String 1: A (5th string)
      80,  // String 2: D (4th string)
      104, // String 3: G (3rd string)
      128, // String 4: B (2nd string)
      152  // String 5: High e (1st string)
    ];

    this.stringNames = ["E2", "A2", "D3", "G3", "B3", "E4"];
  }

  render(voicing, previousVoicing = null) {
    this.currentVoicing = voicing;
    this.previousVoicing = previousVoicing;

    if (!this.container) return;

    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("viewBox", `0 0 ${this.width} ${this.height}`);
    svg.setAttribute("class", "fretboard-svg");

    // 1. Neck Wood Background
    const neck = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    neck.setAttribute("x", "70");
    neck.setAttribute("y", "18");
    neck.setAttribute("width", `${this.width - 90}`);
    neck.setAttribute("height", "150");
    neck.setAttribute("class", "neck-wood");
    svg.appendChild(neck);

    // 2. Fret Inlays (Pearl Markers at 3, 5, 7, 9, and double at 12)
    this.renderInlays(svg);

    // 3. Fret Wires
    this.renderFrets(svg);

    // 4. Nut (Fret 0)
    const nut = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    nut.setAttribute("x", "74");
    nut.setAttribute("y", "18");
    nut.setAttribute("width", "8");
    nut.setAttribute("height", "150");
    nut.setAttribute("class", "fret-nut");
    nut.setAttribute("rx", "2");
    svg.appendChild(nut);

    // 5. Guitar Strings
    this.renderStrings(svg);

    // 6. Transition Ghost Trails (if previous chord provided)
    if (this.showTransitions && previousVoicing) {
      this.renderTransitionTrails(svg, previousVoicing, voicing);
    }

    // 7. Barre Capsules
    this.renderBarres(svg, voicing);

    // 8. Open / Muted String Badges & Fretted Finger Markers
    this.renderNotes(svg, voicing);

    this.container.innerHTML = "";
    this.container.appendChild(svg);
  }

  renderInlays(svg) {
    const singleInlayFrets = [3, 5, 7, 9];
    const centerY = (this.stringPositions[2] + this.stringPositions[3]) / 2;

    singleInlayFrets.forEach(fret => {
      const x = (this.fretPositions[fret - 1] + this.fretPositions[fret]) / 2;
      const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      dot.setAttribute("cx", x);
      dot.setAttribute("cy", centerY);
      dot.setAttribute("r", "5.5");
      dot.setAttribute("class", "fret-inlay");
      svg.appendChild(dot);
    });

    // 12th Fret Double Inlay
    const x12 = (this.fretPositions[11] + this.fretPositions[12]) / 2;
    const dot1 = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot1.setAttribute("cx", x12);
    dot1.setAttribute("cy", this.stringPositions[1] + 12);
    dot1.setAttribute("r", "5");
    dot1.setAttribute("class", "fret-inlay");
    svg.appendChild(dot1);

    const dot2 = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot2.setAttribute("cx", x12);
    dot2.setAttribute("cy", this.stringPositions[4] - 12);
    dot2.setAttribute("r", "5");
    dot2.setAttribute("class", "fret-inlay");
    svg.appendChild(dot2);
  }

  renderFrets(svg) {
    for (let i = 1; i <= this.numFrets; i++) {
      const x = this.fretPositions[i];
      const fretLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
      fretLine.setAttribute("x1", x);
      fretLine.setAttribute("y1", "18");
      fretLine.setAttribute("x2", x);
      fretLine.setAttribute("y2", "168");
      fretLine.setAttribute("class", "fret-wire");
      svg.appendChild(fretLine);

      // Fret number label below neck
      const numLabel = document.createElementNS("http://www.w3.org/2000/svg", "text");
      const midFretX = (this.fretPositions[i - 1] + x) / 2;
      numLabel.setAttribute("x", midFretX);
      numLabel.setAttribute("y", "184");
      numLabel.setAttribute("class", "fret-number-label");
      numLabel.textContent = i;
      svg.appendChild(numLabel);
    }
  }

  renderStrings(svg) {
    this.stringPositions.forEach((y, idx) => {
      // String label at headstock
      const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
      label.setAttribute("x", "30");
      label.setAttribute("y", y + 4);
      label.setAttribute("class", "string-tuning-label");
      label.textContent = this.stringNames[idx];
      svg.appendChild(label);

      // String line
      const strLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
      strLine.setAttribute("x1", "70");
      strLine.setAttribute("y1", y);
      strLine.setAttribute("x2", `${this.width - 25}`);
      strLine.setAttribute("y2", y);
      strLine.setAttribute("class", `guitar-string str-${6 - idx}`);
      strLine.setAttribute("id", `guitar-str-${idx}`);
      svg.appendChild(strLine);
    });
  }

  renderBarres(svg, voicing) {
    if (!voicing.barres || voicing.barres.length === 0) {
      // Check fallback if finger 1 clamps multiple strings at same fret
      const f1Indices = [];
      let barreFret = null;
      voicing.fingers.forEach((finger, sIdx) => {
        if (finger === 1 && voicing.frets[sIdx] > 0) {
          f1Indices.push(sIdx);
          barreFret = voicing.frets[sIdx];
        }
      });

      if (f1Indices.length >= 2 && barreFret) {
        this.drawBarreCapsule(svg, f1Indices, barreFret);
      }
      return;
    }

    voicing.barres.forEach(barre => {
      if (barre.strings.length >= 2) {
        this.drawBarreCapsule(svg, barre.strings, barre.fret);
      }
    });
  }

  drawBarreCapsule(svg, strings, fret) {
    const minStr = Math.min(...strings);
    const maxStr = Math.max(...strings);

    const x = (this.fretPositions[fret - 1] + this.fretPositions[fret]) / 2;
    const yTop = this.stringPositions[minStr] - 14;
    const yBottom = this.stringPositions[maxStr] + 14;
    const height = yBottom - yTop;

    const capsule = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    capsule.setAttribute("x", x - 13);
    capsule.setAttribute("y", yTop);
    capsule.setAttribute("width", "26");
    capsule.setAttribute("height", height);
    capsule.setAttribute("class", "barre-capsule");
    svg.appendChild(capsule);
  }

  renderNotes(svg, voicing) {
    voicing.frets.forEach((fret, sIdx) => {
      const y = this.stringPositions[sIdx];
      const finger = voicing.fingers[sIdx];
      const noteName = voicing.notes ? voicing.notes[sIdx] : "";
      const pitchHz = voicing.pitches_hz ? voicing.pitches_hz[sIdx] : 0;

      if (fret === -1) {
        // Muted string badge at nut
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "badge-mute");

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", "52");
        circle.setAttribute("cy", y);
        circle.setAttribute("r", "10");
        circle.setAttribute("class", "badge-mute");

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "52");
        text.setAttribute("y", y);
        text.setAttribute("class", "badge-mute-text");
        text.textContent = "✕";

        g.appendChild(circle);
        g.appendChild(text);
        svg.appendChild(g);
      } else if (fret === 0) {
        // Open ringing string badge at nut
        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "badge-open");
        g.style.cursor = "pointer";
        g.onclick = () => {
          if (window.guitarAudio) {
            window.guitarAudio.pluckString(pitchHz, window.guitarAudio.audioCtx.currentTime, 2.0, false, sIdx);
            this.vibrateString(sIdx);
          }
        };

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", "52");
        circle.setAttribute("cy", y);
        circle.setAttribute("r", "10");
        circle.setAttribute("class", "badge-open");

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", "52");
        text.setAttribute("y", y);
        text.setAttribute("class", "badge-open-text");
        text.textContent = "O";

        g.appendChild(circle);
        g.appendChild(text);
        svg.appendChild(g);
      } else if (fret > 0) {
        // Fretted note badge
        const x = (this.fretPositions[fret - 1] + this.fretPositions[fret]) / 2;

        const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
        g.setAttribute("class", "fret-badge");
        g.onclick = () => {
          if (window.guitarAudio) {
            window.guitarAudio.pluckString(pitchHz, window.guitarAudio.audioCtx.currentTime, 2.0, false, sIdx);
            this.vibrateString(sIdx);
          }
        };

        const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
        circle.setAttribute("cx", x);
        circle.setAttribute("cy", y);
        circle.setAttribute("r", "12");

        let fingerClass = `finger-${finger}`;
        if (finger === -1) fingerClass = "finger-thumb";
        circle.setAttribute("class", `fret-badge-circle ${fingerClass}`);

        const text = document.createElementNS("http://www.w3.org/2000/svg", "text");
        text.setAttribute("x", x);
        text.setAttribute("y", y);
        text.setAttribute("class", "fret-badge-text-finger");
        text.textContent = finger > 0 ? finger : (finger === -1 ? "T" : "");

        g.appendChild(circle);
        g.appendChild(text);

        // Note pitch pill tag
        if (noteName && noteName !== "X") {
          const pill = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          pill.setAttribute("x", x - 12);
          pill.setAttribute("y", y + 13);
          pill.setAttribute("width", "24");
          pill.setAttribute("height", "12");
          pill.setAttribute("class", "fret-note-pill");

          const noteText = document.createElementNS("http://www.w3.org/2000/svg", "text");
          noteText.setAttribute("x", x);
          noteText.setAttribute("y", y + 19);
          noteText.setAttribute("class", "fret-note-text");
          noteText.textContent = noteName.replace(/[0-9]/g, ""); // e.g. "C" from "C3"

          g.appendChild(pill);
          g.appendChild(noteText);
        }

        svg.appendChild(g);
      }
    });
  }

  renderTransitionTrails(svg, prevVoicing, currVoicing) {
    const prevFingers = {};
    prevVoicing.frets.forEach((fret, sIdx) => {
      const finger = prevVoicing.fingers[sIdx];
      if (fret > 0 && finger > 0 && !prevFingers[finger]) {
        const x = (this.fretPositions[fret - 1] + this.fretPositions[fret]) / 2;
        const y = this.stringPositions[sIdx];
        prevFingers[finger] = { x, y, fret, sIdx };
      }
    });

    currVoicing.frets.forEach((fret, sIdx) => {
      const finger = currVoicing.fingers[sIdx];
      if (fret > 0 && finger > 0 && prevFingers[finger]) {
        const prev = prevFingers[finger];
        const currX = (this.fretPositions[fret - 1] + this.fretPositions[fret]) / 2;
        const currY = this.stringPositions[sIdx];

        if (prev.fret === fret && prev.sIdx === sIdx) {
          // Static Pivot Finger Anchor Ring!
          const pivotHalo = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          pivotHalo.setAttribute("cx", currX);
          pivotHalo.setAttribute("cy", currY);
          pivotHalo.setAttribute("r", "18");
          pivotHalo.setAttribute("fill", "none");
          pivotHalo.setAttribute("stroke", "#2563eb");
          pivotHalo.setAttribute("stroke-width", "2.5");
          pivotHalo.setAttribute("stroke-dasharray", "3 2");
          svg.appendChild(pivotHalo);
        } else {
          // Dynamic Motion Trail
          const trail = document.createElementNS("http://www.w3.org/2000/svg", "line");
          trail.setAttribute("x1", prev.x);
          trail.setAttribute("y1", prev.y);
          trail.setAttribute("x2", currX);
          trail.setAttribute("y2", currY);
          trail.setAttribute("class", "transition-trail");
          svg.appendChild(trail);

          // Origin ghost dot
          const originDot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
          originDot.setAttribute("cx", prev.x);
          originDot.setAttribute("cy", prev.y);
          originDot.setAttribute("r", "4");
          originDot.setAttribute("class", "transition-anchor-dot");
          svg.appendChild(originDot);
        }
      }
    });
  }

  vibrateString(stringIdx) {
    const strElem = document.getElementById(`guitar-str-${stringIdx}`);
    if (strElem) {
      strElem.classList.add("vibrating");
      setTimeout(() => {
        strElem.classList.remove("vibrating");
      }, 350);
    }
  }
}
