/**
 * octave Master Application Orchestrator
 * Coordinates view routing, intro title animation, progression authoring,
 * MIDI drag-and-drop parsing, computational buffer loading, and simplified results display.
 */

import { OctaveApiClient } from "./api_client.js?v=7";
import { FretboardVisualizer } from "./fretboard_view.js?v=7";
import { ProgressionManager } from "./progression_manager.js?v=7";
import { MidiFileHandler } from "./midi_handler.js?v=7";

class OctaveApp {
  constructor() {
    this.currentMode = "site"; // "site" (scrollspy marketing/story) or "app" (chord studio)
    this.appView = "input"; // "input", "buffer", "results"
    this.currentView = "landing";
    this.visualizer = null;
    this.progressionManager = null;
    this.midiHandler = null;

    this.currentTelemetry = null;
    this.currentStepIndex = 0;
    this.viewMode = "optimized"; // "optimized" or "standard"
    this.isPlayingProgression = false;
    this.playbackInterval = null;
    this.updateScrollspy = null;
  }

  async init() {
    // 1. Initialize Fretboard Visualizer for Results view
    this.visualizer = new FretboardVisualizer("results-fretboard-container");

    // 2. Initialize Progression Manager & MIDI Handler for Input view
    this.progressionManager = new ProgressionManager("chord-drag-board", (chords) => {
      // Chords updated
    });

    this.midiHandler = new MidiFileHandler("midi-dropzone", "midi-file-input", (parsedChords) => {
      this.progressionManager.setProgression(parsedChords);
    });

    // 3. Bind Navigation, Scrollspy, and User Controls
    this.bindNavigation();
    this.initScrollspy();
    this.bindInputControls();
    this.bindResultsControls();

    // 4. Trigger Cinematic Intro Animation: OCTAVE -> 8 -> 8VE -> Top Left -> App Reveal
    this.runIntroAnimation();
  }

  /**
   * Opening Animation Sequence:
   * 1. Displays large 'OCTAVE' across the screen with nothing else visible.
   * 2. 'OCTAVE' shrinks down into an '8'.
   * 3. 'VE' joins '8' to form the full message '8VE'.
   * 4. '8VE' moves over into the top left corner (docking into the brand badge).
   * 5. The full application and navbar are smoothly unveiled.
   */
  runIntroAnimation() {
    const splash = document.getElementById("app-intro-splash");
    const introOctave = document.getElementById("intro-word-octave");
    const intro8ve = document.getElementById("intro-8ve-group");
    const brandIcon = document.querySelector(".brand-icon-mini");

    if (!splash || !introOctave || !intro8ve) {
      document.body.classList.remove("intro-running");
      document.body.classList.add("intro-complete");
      return;
    }

    let isFinished = false;
    const finishIntro = () => {
      if (isFinished) return;
      isFinished = true;
      splash.classList.add("fade-out");
      document.body.classList.remove("intro-running");
      document.body.classList.add("intro-complete");
      setTimeout(() => {
        splash.style.display = "none";
      }, 600);
    };

    // User can click anywhere on the splash to skip directly to the app
    splash.onclick = () => finishIntro();

    // Reduced motion accessibility check
    if (window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      finishIntro();
      return;
    }

    // Step 1: Hold the large 'OCTAVE' across screen for 1.15 seconds
    setTimeout(() => {
      if (isFinished) return;

      // Step 2: 'OCTAVE' shrinks down into '8'
      introOctave.classList.add("shrink-out");
      intro8ve.classList.add("show-8");

      // Step 3: 'VE' reveals next to '8', completing the message '8VE'
      setTimeout(() => {
        if (isFinished) return;
        intro8ve.classList.add("show-ve");

        // Step 4: The message '8VE' moves over to the top left corner
        setTimeout(() => {
          if (isFinished) return;
          if (brandIcon) {
            const targetRect = brandIcon.getBoundingClientRect();
            const currentRect = intro8ve.getBoundingClientRect();

            const currentCenterX = currentRect.left + currentRect.width / 2;
            const currentCenterY = currentRect.top + currentRect.height / 2;

            const targetCenterX = targetRect.left + targetRect.width / 2;
            const targetCenterY = targetRect.top + targetRect.height / 2;

            const dx = targetCenterX - currentCenterX;
            const dy = targetCenterY - currentCenterY;

            const targetScale = Math.max(0.3, Math.min(1.0, targetRect.height / (currentRect.height || 48)));

            intro8ve.style.transition = "transform 0.85s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.85s ease";
            intro8ve.style.transform = `translate(${dx}px, ${dy}px) scale(${targetScale})`;
          } else {
            intro8ve.style.transition = "transform 0.85s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.85s ease";
            intro8ve.style.transform = "translate(calc(-50vw + 48px), calc(-50vh + 32px)) scale(0.4)";
          }

          // Step 5: When '8VE' lands in top-left, smoothly unveil the full application
          setTimeout(() => {
            finishIntro();
          }, 850);
        }, 650); // Pause so user sees the complete '8VE' message
      }, 650); // Pause so user sees the '8'
    }, 1150); // Initial large 'OCTAVE' duration
  }

  /**
   * Initializes Scrollspy on the marketing/story sections:
   * Dynamically tracks when Hero, Our Story, or Team & Musicians are in viewport
   * and highlights the appropriate navbar item.
   */
  initScrollspy() {
    const sections = [
      { id: "hero", linkId: null },
      { id: "about", linkId: "nav-about-link" },
      { id: "creators", linkId: "nav-creators-link" }
    ];

    this.updateScrollspy = () => {
      // Only run scrollspy when on the public site/story mode
      if (this.currentMode !== "site") return;

      const scrollY = window.scrollY;
      const navbarHeight = 85;

      let activeSectionId = "hero";
      for (const sec of sections) {
        const el = document.getElementById(sec.id);
        if (el) {
          const top = el.offsetTop - navbarHeight - 40;
          if (scrollY >= top) {
            activeSectionId = sec.id;
          }
        }
      }

      const navAbout = document.getElementById("nav-about-link");
      const navCreators = document.getElementById("nav-creators-link");
      const navPlay = document.getElementById("nav-play-link");

      if (navAbout) navAbout.classList.toggle("active", activeSectionId === "about");
      if (navCreators) navCreators.classList.toggle("active", activeSectionId === "creators");
      if (navPlay) navPlay.classList.remove("active");
    };

    window.addEventListener("scroll", this.updateScrollspy, { passive: true });
    this.updateScrollspy();
  }

  /**
   * Enters the actual App Workspace (Chord Builder / Buffer / Fretboard Results).
   * Only reachable when the user clicks a Play button!
   */
  enterApp(initialAppView = "input") {
    this.currentMode = "app";

    const landingFlow = document.getElementById("landing-flow");
    const appWorkspace = document.getElementById("app-workspace");

    if (landingFlow) landingFlow.style.display = "none";
    if (appWorkspace) {
      appWorkspace.style.display = "block";
    }

    // Update navbar active state
    const navAbout = document.getElementById("nav-about-link");
    const navCreators = document.getElementById("nav-creators-link");
    const navPlay = document.getElementById("nav-play-link");

    if (navAbout) navAbout.classList.remove("active");
    if (navCreators) navCreators.classList.remove("active");
    if (navPlay) navPlay.classList.add("active");

    this.setAppView(initialAppView);
  }

  /**
   * Exits the App Workspace and returns to the marketing/story scrollspy layout.
   */
  exitApp(targetSectionId = "hero") {
    this.currentMode = "site";

    // Stop audio playback if running
    if (this.isPlayingProgression) {
      this.stopProgressionPlayback();
    }

    const landingFlow = document.getElementById("landing-flow");
    const appWorkspace = document.getElementById("app-workspace");

    if (appWorkspace) appWorkspace.style.display = "none";
    if (landingFlow) landingFlow.style.display = "flex";

    const navPlay = document.getElementById("nav-play-link");
    if (navPlay) navPlay.classList.remove("active");

    if (targetSectionId && targetSectionId !== "hero") {
      const targetEl = document.getElementById(targetSectionId);
      if (targetEl) {
        setTimeout(() => {
          targetEl.scrollIntoView({ behavior: "smooth" });
        }, 30);
      }
    } else {
      window.scrollTo({ top: 0, behavior: "smooth" });
    }

    if (this.updateScrollspy) {
      setTimeout(() => this.updateScrollspy(), 100);
    }
  }

  /**
   * Switches internal view within the App Workspace (input, buffer, results)
   */
  setAppView(viewName) {
    this.appView = viewName;

    // Stop audio playback if switching away from results
    if (viewName !== "results" && this.isPlayingProgression) {
      this.stopProgressionPlayback();
    }

    const appViews = ["input", "buffer", "results"];
    appViews.forEach(v => {
      const el = document.getElementById(`view-${v}`);
      if (el) {
        if (v === viewName) {
          el.classList.add("active");
        } else {
          el.classList.remove("active");
        }
      }
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  /**
   * Unified View Router (backward compatible with all previous calls)
   */
  navigateTo(viewName) {
    this.currentView = viewName;

    if (viewName === "landing" || viewName === "hero") {
      this.exitApp("hero");
    } else if (viewName === "about") {
      this.exitApp("about");
    } else if (viewName === "creators") {
      this.exitApp("creators");
    } else if (viewName === "input" || viewName === "buffer" || viewName === "results") {
      if (this.currentMode === "app") {
        this.setAppView(viewName);
      } else {
        this.enterApp(viewName);
      }
    }
  }

  bindNavigation() {
    // Brand Logo Home Link
    const brandHome = document.getElementById("brand-home-link");
    if (brandHome) {
      brandHome.onclick = (e) => {
        e.preventDefault();
        if (this.currentMode === "app") {
          this.exitApp("hero");
        } else {
          window.scrollTo({ top: 0, behavior: "smooth" });
        }
      };
    }

    // Top Nav: Our Story
    const navAbout = document.getElementById("nav-about-link");
    if (navAbout) {
      navAbout.onclick = (e) => {
        e.preventDefault();
        if (this.currentMode === "app") {
          this.exitApp("about");
        } else {
          const target = document.getElementById("about");
          if (target) target.scrollIntoView({ behavior: "smooth" });
        }
      };
    }

    // Top Nav: Team & Musicians
    const navCreators = document.getElementById("nav-creators-link");
    if (navCreators) {
      navCreators.onclick = (e) => {
        e.preventDefault();
        if (this.currentMode === "app") {
          this.exitApp("creators");
        } else {
          const target = document.getElementById("creators");
          if (target) target.scrollIntoView({ behavior: "smooth" });
        }
      };
    }

    // Top Nav: Play Chords (Enters App)
    const navPlay = document.getElementById("nav-play-link");
    if (navPlay) {
      navPlay.onclick = (e) => {
        e.preventDefault();
        this.enterApp("input");
      };
    }

    // Big Center Play Button in Hero Section (Enters App)
    const bigPlayBtn = document.getElementById("big-center-play-btn");
    if (bigPlayBtn) {
      bigPlayBtn.onclick = () => {
        this.enterApp("input");
      };
    }

    // Story Section Call To Action Play Button (Enters App)
    const storyPlayBtn = document.getElementById("story-play-btn");
    if (storyPlayBtn) {
      storyPlayBtn.onclick = () => {
        this.enterApp("input");
      };
    }

    // Team Section Call To Action Play Button (Enters App)
    const teamPlayBtn = document.getElementById("team-play-btn");
    if (teamPlayBtn) {
      teamPlayBtn.onclick = () => {
        this.enterApp("input");
      };
    }

    // App Workspace Bar: "← Back to Overview"
    const exitAppBtn = document.getElementById("exit-app-btn");
    if (exitAppBtn) {
      exitAppBtn.onclick = () => {
        this.exitApp("hero");
      };
    }

    // Footer Links
    const footerAbout = document.getElementById("footer-about-link");
    if (footerAbout) {
      footerAbout.onclick = (e) => {
        e.preventDefault();
        if (this.currentMode === "app") {
          this.exitApp("about");
        } else {
          const target = document.getElementById("about");
          if (target) target.scrollIntoView({ behavior: "smooth" });
        }
      };
    }

    const footerCreators = document.getElementById("footer-creators-link");
    if (footerCreators) {
      footerCreators.onclick = (e) => {
        e.preventDefault();
        if (this.currentMode === "app") {
          this.exitApp("creators");
        } else {
          const target = document.getElementById("creators");
          if (target) target.scrollIntoView({ behavior: "smooth" });
        }
      };
    }

    // Edit Progression Back Button inside Results view
    const editBtn = document.getElementById("edit-progression-btn");
    if (editBtn) {
      editBtn.onclick = () => {
        this.setAppView("input");
      };
    }
  }

  bindInputControls() {
    // Preset dropdown loader
    const presetSelect = document.getElementById("preset-select");
    if (presetSelect) {
      const presetMap = {
        "barre_gauntlet": ["F", "Bm", "F#m", "C#m"],
        "pop_anthem": ["C", "G", "Am", "F"],
        "jazz_turnaround": ["Dm7", "G7", "Cmaj7", "A7"],
        "indie_rock": ["Bm", "G", "D", "A"],
        "folk_rock": ["G", "D", "Em", "C"]
      };

      presetSelect.onchange = () => {
        const selectedChords = presetMap[presetSelect.value];
        if (selectedChords) {
          this.progressionManager.setProgression(selectedChords);
        }
      };
    }

    // Max Span slider in Input view
    const spanSlider = document.getElementById("input-span-slider");
    const spanVal = document.getElementById("input-span-val");
    if (spanSlider && spanVal) {
      const labels = {
        "1": "1 fret (Closest)",
        "2": "2 frets (Gentle)",
        "3": "3 frets (Normal)",
        "4": "4 frets (Wide)"
      };
      spanSlider.oninput = () => {
        spanVal.textContent = labels[spanSlider.value] || `${spanSlider.value} frets`;
      };
    }

    // Primary "Start Optimization" Action Button
    const startOptBtn = document.getElementById("start-opt-btn");
    if (startOptBtn) {
      startOptBtn.onclick = () => {
        this.startOptimizationFlow();
      };
    }
  }

  clearProgression() {
    this.progressionManager.setProgression([]);
  }

  /**
   * Optimization Workflow:
   * 1. Navigates to the buffer loading view.
   * 2. Runs animated progress bar gradually from 0% -> 100% over ~5.0 seconds.
   * 3. Displays progressive plain-English status messages.
   * 4. Calls optimization engine concurrently and transitions to results view.
   */
  async startOptimizationFlow() {
    const chords = this.progressionManager.chords;
    if (!chords || chords.length === 0) {
      alert("Please add at least 1 chord to your song before finding easier shapes.");
      return;
    }

    // Switch to Buffer view
    this.navigateTo("buffer");

    const progressBar = document.getElementById("buffer-progress-fill");
    const pctCounter = document.getElementById("buffer-pct-counter");
    const statusMsg = document.getElementById("buffer-status-msg");

    // Initialize progress bar and percentage display
    if (progressBar) progressBar.style.width = "0%";
    if (pctCounter) pctCounter.textContent = "0%";

    const statusMilestones = [
      { pct: 0, msg: "Reading chord notes and song harmony..." },
      { pct: 14, msg: "Scanning the fretboard for comfortable finger positions..." },
      { pct: 28, msg: "Checking finger stretch and grip pressure..." },
      { pct: 44, msg: "Removing painful barre chords and wide stretches..." },
      { pct: 60, msg: "Finding shared anchor fingers for easy chord changes..." },
      { pct: 75, msg: "Picking the smoothest, most natural chord shapes..." },
      { pct: 90, msg: "Tuning clear acoustic chord sounds..." },
      { pct: 100, msg: "Done! Your easy-play chords are ready." }
    ];

    if (statusMsg) {
      statusMsg.textContent = statusMilestones[0].msg;
    }

    // Configure 5.0-second (5000ms) gradual progress animation
    const TOTAL_DURATION_MS = 5000;
    const startTime = performance.now();
    let timer = null;

    const progressPromise = new Promise((resolve) => {
      timer = setInterval(() => {
        const elapsed = performance.now() - startTime;
        const progressRatio = Math.min(elapsed / TOTAL_DURATION_MS, 1.0);
        const currentPct = Math.min(100, Math.floor(progressRatio * 100));

        if (progressBar) progressBar.style.width = `${currentPct}%`;
        if (pctCounter) pctCounter.textContent = `${currentPct}%`;

        // Select the active status message based on current percentage
        let activeMsg = statusMilestones[0].msg;
        for (const item of statusMilestones) {
          if (currentPct >= item.pct) {
            activeMsg = item.msg;
          }
        }
        if (statusMsg && statusMsg.textContent !== activeMsg) {
          statusMsg.textContent = activeMsg;
        }

        if (progressRatio >= 1.0) {
          clearInterval(timer);
          timer = null;
          resolve();
        }
      }, 40);
    });

    try {
      // Extract ergonomic constraints
      const spanSlider = document.getElementById("input-span-slider");
      const spanLimit = parseInt(spanSlider ? spanSlider.value : 2, 10);
      const banBarresToggle = document.getElementById("input-ban-barre-toggle");
      const banBarres = banBarresToggle ? banBarresToggle.checked : true;
      const openStringsToggle = document.getElementById("input-open-strings-toggle");
      const preferOpen = openStringsToggle ? openStringsToggle.checked : true;

      const customProfile = {
        id: "custom",
        name: "Custom Hand Comfort Profile",
        description: "User customized settings",
        max_fret_span: spanLimit,
        ban_barres: banBarres,
        prefer_open_drones: preferOpen,
        pinky_restriction: 0.5,
        index_clamp_sensitivity: 2.2,
        wrist_flexion_limit: 1.5,
        allow_harmonic_extensions: true
      };

      // Execute backend optimization concurrently with the 5-second progress animation
      const [telemetry] = await Promise.all([
        OctaveApiClient.optimizeProgression(chords, "custom", customProfile),
        progressPromise
      ]);

      this.currentTelemetry = telemetry;

      // Lock at 100% and notify completion
      if (progressBar) progressBar.style.width = "100%";
      if (pctCounter) pctCounter.textContent = "100%";
      if (statusMsg) statusMsg.textContent = "Done! Your easy-play chords are ready.";

      // Brief 400ms pause at 100% so the user observes completion before transitioning to results
      setTimeout(() => {
        this.currentStepIndex = 0;
        this.viewMode = "optimized";
        this.populateResultsView(telemetry);
        this.navigateTo("results");
      }, 400);
    } catch (err) {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
      console.error("Optimization failed:", err);
      alert(`Could not optimize chords: ${err.message}`);
      this.navigateTo("input");
    }
  }

  /**
   * Populates the Simplified Results View with celebration banner,
   * fretboard visualizer, and before/after comparisons.
   */
  populateResultsView(telemetry) {
    // 1. Celebratory Strain Saved Banner
    const strainPct = document.getElementById("res-strain-pct");
    const barresEliminated = document.getElementById("res-barres-eliminated");
    const travelSaved = document.getElementById("res-travel-saved");
    const openStrings = document.getElementById("res-open-strings");

    if (strainPct) strainPct.textContent = `-${telemetry.total_strain_reduction_pct}%`;
    if (barresEliminated) barresEliminated.textContent = `${telemetry.barres_eliminated_count} Barres Removed`;
    if (travelSaved) travelSaved.textContent = `-${telemetry.travel_reduction_pct}% Less Movement`;
    if (openStrings) openStrings.textContent = `+${telemetry.open_strings_gained_count} Open Strings`;

    // 2. Render Active Chord Step
    this.renderResultsChordStep();
  }

  renderResultsChordStep() {
    if (!this.currentTelemetry || !this.currentTelemetry.steps) return;
    const step = this.currentTelemetry.steps[this.currentStepIndex];
    if (!step) return;

    // Chord title
    const chordTitle = document.getElementById("res-chord-title");
    const activeVoicing = this.viewMode === "optimized" ? step.optimized_voicing : step.standard_voicing;
    if (chordTitle) {
      chordTitle.innerHTML = `Chord <strong>${this.currentStepIndex + 1}</strong> of ${this.currentTelemetry.steps.length}: <span style="color:var(--accent-primary); font-weight:700;">${activeVoicing.chord_name}</span>`;
    }

    // Previous voicing for motion trails
    let prevVoicing = null;
    if (this.currentStepIndex > 0) {
      const prevStep = this.currentTelemetry.steps[this.currentStepIndex - 1];
      prevVoicing = this.viewMode === "optimized" ? prevStep.optimized_voicing : prevStep.standard_voicing;
    }

    // Render SVG Fretboard
    this.visualizer.render(activeVoicing, prevVoicing);

    // Update Comparison Spec Cards
    this.updateComparisonSpecCards(step);
  }

  updateComparisonSpecCards(step) {
    const std = step.standard_voicing;
    const stdStrain = step.standard_strain;
    const opt = step.optimized_voicing;
    const optStrain = step.optimized_strain;

    const stdContainer = document.getElementById("res-spec-standard");
    const optContainer = document.getElementById("res-spec-optimized");

    if (stdContainer) {
      stdContainer.innerHTML = `
        <div class="spec-header-row">
          <span style="color:var(--text-secondary); font-weight:600;">Standard Chord: ${std.chord_name}</span>
          <span class="card-badge" style="background:var(--bg-canvas); color:var(--text-muted); border-color:var(--border-subtle);">Tougher Grip</span>
        </div>
        <div class="data-metric-line">
          <span class="key">Barre Clamp:</span>
          <span class="val ${stdStrain.is_barre_active ? 'text-red-500 font-bold' : ''}">
            ${stdStrain.is_barre_active ? `YES (${stdStrain.barre_strings_count} strings flat)` : 'None'}
          </span>
        </div>
        <div class="data-metric-line">
          <span class="key">Finger Stretch:</span>
          <span class="val">${stdStrain.fret_span} frets wide</span>
        </div>
        <div class="data-metric-line">
          <span class="key">Fingers Used:</span>
          <span class="val font-mono">${stdStrain.fingering_notation}</span>
        </div>
        <div class="data-metric-line">
          <span class="key">Hand Effort Level:</span>
          <span class="val font-bold" style="color:var(--accent-warning);">${stdStrain.total_chord_strain.toFixed(1)} pts (Heavy)</span>
        </div>
      `;
    }

    if (optContainer) {
      optContainer.innerHTML = `
        <div class="spec-header-row">
          <span style="color:var(--accent-primary); font-weight:700;">Easy Octave Shape: ${opt.chord_name}</span>
          <span class="card-badge" style="background:var(--accent-primary-subtle); color:var(--accent-primary); border-color:var(--accent-primary-border);">
            ${step.strain_reduction_pct}% Easier
          </span>
        </div>
        <div class="data-metric-line">
          <span class="key">Barre Clamp:</span>
          <span class="val font-bold" style="color:var(--accent-primary);">
            ${optStrain.is_barre_active ? 'Light' : 'NO BARRE (Zero Clamp)'}
          </span>
        </div>
        <div class="data-metric-line">
          <span class="key">Finger Stretch:</span>
          <span class="val" style="color:var(--accent-primary);">${optStrain.fret_span} frets (Gentle)</span>
        </div>
        <div class="data-metric-line">
          <span class="key">Fingers Used:</span>
          <span class="val font-mono" style="color:var(--accent-primary); font-weight:700;">${optStrain.fingering_notation}</span>
        </div>
        <div class="data-metric-line">
          <span class="key">Hand Effort Level:</span>
          <span class="val font-bold" style="color:var(--accent-primary);">${optStrain.total_chord_strain.toFixed(1)} pts (Very Light)</span>
        </div>
      `;
    }
  }

  bindResultsControls() {
    // Step Prev / Next buttons
    const prevBtn = document.getElementById("res-prev-btn");
    const nextBtn = document.getElementById("res-next-btn");

    if (prevBtn) {
      prevBtn.onclick = () => {
        if (!this.currentTelemetry) return;
        if (this.currentStepIndex > 0) {
          this.currentStepIndex--;
          this.renderResultsChordStep();
          this.playCurrentVoicingSound();
        }
      };
    }

    if (nextBtn) {
      nextBtn.onclick = () => {
        if (!this.currentTelemetry) return;
        if (this.currentStepIndex < this.currentTelemetry.steps.length - 1) {
          this.currentStepIndex++;
          this.renderResultsChordStep();
          this.playCurrentVoicingSound();
        }
      };
    }

    // Toggle Voicing (Optimized vs Standard)
    const toggleOpt = document.getElementById("res-toggle-opt");
    const toggleStd = document.getElementById("res-toggle-std");

    if (toggleOpt && toggleStd) {
      toggleOpt.onclick = () => {
        this.viewMode = "optimized";
        toggleOpt.classList.add("active");
        toggleStd.classList.remove("active", "standard");
        this.renderResultsChordStep();
      };

      toggleStd.onclick = () => {
        this.viewMode = "standard";
        toggleStd.classList.add("active", "standard");
        toggleOpt.classList.remove("active");
        this.renderResultsChordStep();
      };
    }

    // Strum Audio button
    const strumBtn = document.getElementById("res-strum-btn");
    if (strumBtn) {
      strumBtn.onclick = () => this.playCurrentVoicingSound();
    }

    // A/B Audition Compare button
    const abBtn = document.getElementById("res-ab-btn");
    if (abBtn) {
      abBtn.onclick = () => this.playABComparison();
    }

    // Play Progression Continuous Loop button
    const playProgBtn = document.getElementById("res-play-prog-btn");
    if (playProgBtn) {
      playProgBtn.onclick = () => this.toggleProgressionPlayback();
    }
  }

  playCurrentVoicingSound() {
    if (!this.currentTelemetry || !this.currentTelemetry.steps) return;
    const step = this.currentTelemetry.steps[this.currentStepIndex];
    if (!step) return;

    const voicing = this.viewMode === "optimized" ? step.optimized_voicing : step.standard_voicing;
    window.guitarAudio.playChord(voicing, 26, (strIdx) => {
      this.visualizer.vibrateString(strIdx);
    });
  }

  playABComparison() {
    if (!this.currentTelemetry || !this.currentTelemetry.steps) return;
    const step = this.currentTelemetry.steps[this.currentStepIndex];
    if (!step) return;

    const toggleOpt = document.getElementById("res-toggle-opt");
    const toggleStd = document.getElementById("res-toggle-std");

    window.guitarAudio.playABComparison(step.standard_voicing, step.optimized_voicing, (state) => {
      if (state === "standard") {
        this.viewMode = "standard";
        if (toggleStd) toggleStd.classList.add("active", "standard");
        if (toggleOpt) toggleOpt.classList.remove("active");
        this.renderResultsChordStep();
      } else if (state === "optimized") {
        this.viewMode = "optimized";
        if (toggleOpt) toggleOpt.classList.add("active");
        if (toggleStd) toggleStd.classList.remove("active", "standard");
        this.renderResultsChordStep();
      }
    });
  }

  toggleProgressionPlayback() {
    const playBtn = document.getElementById("res-play-prog-btn");
    if (this.isPlayingProgression) {
      this.stopProgressionPlayback();
      return;
    }

    this.isPlayingProgression = true;
    if (playBtn) playBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="6" width="12" height="12"/></svg> Stop Playing';

    let stepIdx = 0;
    const totalSteps = this.currentTelemetry.steps.length;

    const playStep = () => {
      if (!this.isPlayingProgression) return;
      this.currentStepIndex = stepIdx;
      this.renderResultsChordStep();
      this.playCurrentVoicingSound();
      stepIdx = (stepIdx + 1) % totalSteps;
    };

    playStep();
    this.playbackInterval = setInterval(playStep, 1900);
  }

  stopProgressionPlayback() {
    this.isPlayingProgression = false;
    if (this.playbackInterval) {
      clearInterval(this.playbackInterval);
      this.playbackInterval = null;
    }
    const playBtn = document.getElementById("res-play-prog-btn");
    if (playBtn) playBtn.innerHTML = '<svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg> Play All Chords';
  }
}

// Instantiate and attach globally
window.octaveApp = new OctaveApp();
window.addEventListener("DOMContentLoaded", () => {
  window.octaveApp.init();
});
