/**
 * Octave 3D Acoustic Guitar Experience
 * High-performance WebGL 3D model using Three.js.
 * Renders an acoustic dreadnought guitar with tonewood materials,
 * soundboard rosette, frets, phosphor bronze strings, and continuous slow rotation.
 */

class Guitar3DViewer {
  constructor(containerId = "hero-guitar-3d-canvas") {
    this.container = document.getElementById(containerId);
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.guitarGroup = null;
    this.isRotating = true;
    this.animationFrameId = null;
    this.clock = null;

    // Mouse parallax
    this.targetRotationX = 0.12;
    this.targetRotationY = 0;
    this.mouse = { x: 0, y: 0 };
    
    // Bind methods
    this.onWindowResize = this.onWindowResize.bind(this);
    this.onMouseMove = this.onMouseMove.bind(this);
    this.animate = this.animate.bind(this);
  }

  init() {
    if (!this.container || typeof THREE === "undefined") {
      console.warn("Three.js or 3D container not available");
      return;
    }

    let width = this.container.clientWidth || this.container.parentElement?.clientWidth || window.innerWidth;
    let height = this.container.clientHeight || this.container.parentElement?.clientHeight || window.innerHeight;
    if (width <= 0) width = window.innerWidth;
    if (height <= 0) height = window.innerHeight;

    // 1. Scene & Clock
    this.scene = new THREE.Scene();
    this.clock = new THREE.Clock();

    // 2. Camera with optimized near/far planes for maximum depth buffer precision
    this.camera = new THREE.PerspectiveCamera(40, width / height, 0.5, 50);
    this.camera.position.set(0, 0, 11.5);

    // 3. Renderer with antialiasing and alpha transparency (standard 24-bit depth buffer)
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.container,
      antialias: true,
      alpha: true,
      powerPreference: "high-performance"
    });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    // 4. Lighting Rig (Atmospheric Golden Hour & Warm Rim Light)
    this.setupLighting();

    // 5. Construct 3D Acoustic Guitar Geometry
    this.buildGuitarModel();

    // 6. Background Dust/Sound Particles
    this.buildSoundParticles();

    // 7. Event Listeners
    window.addEventListener("resize", this.onWindowResize, { passive: true });
    window.addEventListener("mousemove", this.onMouseMove, { passive: true });

    // 8. Trigger initial responsive layout calibration
    this.onWindowResize();

    // 9. Start Rendering Loop
    this.animate();
  }

  setupLighting() {
    // Warm ambient light
    const ambient = new THREE.AmbientLight(0x2a1810, 1.4);
    this.scene.add(ambient);

    // Key Light (Warm golden sunlight)
    const keyLight = new THREE.DirectionalLight(0xffeedd, 2.2);
    keyLight.position.set(5, 6, 8);
    this.scene.add(keyLight);

    // Golden Rim Light (from behind/side for dramatic NASA-style horizon glow)
    const rimLight = new THREE.DirectionalLight(0xd97724, 3.2);
    rimLight.position.set(-6, 3, -4);
    this.scene.add(rimLight);

    // Bottom fill light (subtle tonewood warmth)
    const fillLight = new THREE.DirectionalLight(0xb87333, 1.0);
    fillLight.position.set(0, -6, 4);
    this.scene.add(fillLight);
  }

  buildGuitarModel() {
    this.guitarGroup = new THREE.Group();

    // Materials
    const rosewoodMat = new THREE.MeshStandardMaterial({
      color: 0x22130c,
      roughness: 0.35,
      metalness: 0.1
    });

    const spruceTopMat = new THREE.MeshStandardMaterial({
      color: 0xc88f58,
      roughness: 0.45,
      metalness: 0.05
    });

    const ebonyMat = new THREE.MeshStandardMaterial({
      color: 0x140e0a,
      roughness: 0.3,
      metalness: 0.1
    });

    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xd97724,
      roughness: 0.3,
      metalness: 0.7
    });

    const silverMat = new THREE.MeshStandardMaterial({
      color: 0xd1d5db,
      roughness: 0.25,
      metalness: 0.85
    });

    const stringMat = new THREE.MeshStandardMaterial({
      color: 0xedb372,
      roughness: 0.2,
      metalness: 0.8
    });

    // --- 1. Acoustic Body (Hourglass Extrusion) ---
    const bodyShape = new THREE.Shape();
    // Start at bottom center
    bodyShape.moveTo(0, -2.4);
    // Lower bout right
    bodyShape.bezierCurveTo(1.55, -2.4, 2.05, -1.75, 1.95, -0.65);
    // Waist right
    bodyShape.bezierCurveTo(1.85, 0.0, 1.35, 0.45, 1.25, 0.85);
    // Upper bout right
    bodyShape.bezierCurveTo(1.15, 1.35, 1.7, 1.85, 1.5, 2.25);
    bodyShape.bezierCurveTo(1.3, 2.65, 0.55, 2.75, 0, 2.75);
    // Upper bout left
    bodyShape.bezierCurveTo(-0.55, 2.75, -1.3, 2.65, -1.5, 2.25);
    bodyShape.bezierCurveTo(-1.7, 1.85, -1.15, 1.35, -1.25, 0.85);
    // Waist left
    bodyShape.bezierCurveTo(-1.35, 0.45, -1.85, 0.0, -1.95, -0.65);
    // Lower bout left
    bodyShape.bezierCurveTo(-2.05, -1.75, -1.55, -2.4, 0, -2.4);

    const extrudeSettings = {
      depth: 0.85,
      bevelEnabled: true,
      bevelSegments: 3,
      steps: 1,
      bevelSize: 0.06,
      bevelThickness: 0.06
    };

    const bodyGeo = new THREE.ExtrudeGeometry(bodyShape, extrudeSettings);
    bodyGeo.center();

    // Assign multi-material groups on the single extruded body:
    // Back cap = Indian Rosewood, Front Soundboard cap = Sitka Spruce, Sides & Bevel = Indian Rosewood
    // Completely eliminates duplicate front-plate meshes and guarantees zero coplanar flickering!
    const half = bodyGeo.groups[0].count / 2;
    bodyGeo.groups = [
      { start: 0, count: half, materialIndex: 0 },          // Back cap: rosewoodMat
      { start: half, count: half, materialIndex: 1 },       // Front cap: spruceTopMat
      { start: bodyGeo.groups[1].start, count: bodyGeo.groups[1].count, materialIndex: 0 } // Sides & bevels: rosewoodMat
    ];

    const bodyMesh = new THREE.Mesh(bodyGeo, [rosewoodMat, spruceTopMat]);
    this.guitarGroup.add(bodyMesh);

    // Soundhole (Recessed dark cavity)
    const soundholeGeo = new THREE.CircleGeometry(0.55, 32);
    const soundholeMat = new THREE.MeshBasicMaterial({ color: 0x0a0503 });
    const soundholeMesh = new THREE.Mesh(soundholeGeo, soundholeMat);
    soundholeMesh.position.set(0, 0.85, 0.487);
    this.guitarGroup.add(soundholeMesh);

    // Rosette Inlay Rings
    const rosetteGeo1 = new THREE.RingGeometry(0.56, 0.62, 32);
    const rosetteMesh1 = new THREE.Mesh(rosetteGeo1, goldMat);
    rosetteMesh1.position.set(0, 0.85, 0.488);
    this.guitarGroup.add(rosetteMesh1);

    const rosetteGeo2 = new THREE.RingGeometry(0.66, 0.72, 32);
    const rosetteMesh2 = new THREE.Mesh(rosetteGeo2, rosewoodMat);
    rosetteMesh2.position.set(0, 0.85, 0.488);
    this.guitarGroup.add(rosetteMesh2);

    // Pickguard (Teardrop under soundhole)
    const pickguardShape = new THREE.Shape();
    pickguardShape.moveTo(0.55, 0.85);
    pickguardShape.bezierCurveTo(1.1, 0.85, 1.35, 0.35, 1.25, -0.2);
    pickguardShape.bezierCurveTo(1.15, -0.65, 0.6, -0.65, 0.4, -0.3);
    pickguardShape.bezierCurveTo(0.2, 0.1, 0.35, 0.7, 0.55, 0.85);
    const pickguardGeo = new THREE.ShapeGeometry(pickguardShape);
    const pickguardMat = new THREE.MeshStandardMaterial({ color: 0x241108, roughness: 0.2, metalness: 0.1 });
    const pickguardMesh = new THREE.Mesh(pickguardGeo, pickguardMat);
    pickguardMesh.position.z = 0.489;
    this.guitarGroup.add(pickguardMesh);

    // Bridge & Saddle (Ebony block + bone saddle)
    const bridgeGeo = new THREE.BoxGeometry(1.4, 0.35, 0.09);
    const bridgeMesh = new THREE.Mesh(bridgeGeo, ebonyMat);
    bridgeMesh.position.set(0, -1.0, 0.53);
    this.guitarGroup.add(bridgeMesh);

    const saddleGeo = new THREE.BoxGeometry(0.9, 0.05, 0.06);
    const saddleMat = new THREE.MeshStandardMaterial({ color: 0xf5f0e1, roughness: 0.3 });
    const saddleMesh = new THREE.Mesh(saddleGeo, saddleMat);
    saddleMesh.position.set(0, -0.98, 0.605);
    this.guitarGroup.add(saddleMesh);

    // 6 Bridge Pins
    for (let i = 0; i < 6; i++) {
      const pinGeo = new THREE.CylinderGeometry(0.02, 0.02, 0.05, 8);
      const pinMesh = new THREE.Mesh(pinGeo, saddleMat);
      pinMesh.position.set(-0.35 + i * 0.14, -1.08, 0.585);
      pinMesh.rotation.x = Math.PI / 2;
      this.guitarGroup.add(pinMesh);
    }

    // --- 2. Mahogany Neck ---
    const neckLength = 2.48;
    const neckGeo = new THREE.BoxGeometry(0.50, neckLength, 0.28);
    const neckMesh = new THREE.Mesh(neckGeo, rosewoodMat);
    neckMesh.position.set(0, 3.44, 0.35);
    this.guitarGroup.add(neckMesh);

    // Neck Heel Block (Tapered wood joint connecting neck to body back)
    const heelGeo = new THREE.BoxGeometry(0.48, 0.60, 0.26);
    const heelMesh = new THREE.Mesh(heelGeo, rosewoodMat);
    heelMesh.position.set(0, 2.30, 0.12);
    this.guitarGroup.add(heelMesh);

    // Fretboard (Fingerboard: firmly elevated above soundboard, eliminating coplanar overlap)
    const fretboardGeo = new THREE.BoxGeometry(0.52, 3.53, 0.06);
    const fretboardMesh = new THREE.Mesh(fretboardGeo, ebonyMat);
    fretboardMesh.position.set(0, 2.915, 0.525); // Bounds: z in [0.495, 0.555] -> clear of soundboard z: 0.485
    this.guitarGroup.add(fretboardMesh);

    // Frets (19 silver wires seated on top of fretboard surface at z = 0.555)
    for (let f = 1; f <= 19; f++) {
      const fretY = 4.65 - (f * 0.18);
      const fretGeo = new THREE.BoxGeometry(0.50, 0.016, 0.024);
      const fretMesh = new THREE.Mesh(fretGeo, silverMat);
      fretMesh.position.set(0, fretY, 0.567);
      this.guitarGroup.add(fretMesh);
    }

    // Pearloid Fret Inlay Markers (Dots at frets 3, 5, 7, 9, 12, 15)
    const dotFrets = [3, 5, 7, 9, 12, 15];
    dotFrets.forEach(f => {
      const dotY = 4.65 - (f * 0.18) + 0.09;
      if (f === 12) {
        // Double dot at 12th fret
        const dot1 = new THREE.Mesh(new THREE.CircleGeometry(0.025, 8), saddleMat);
        dot1.position.set(-0.12, dotY, 0.557);
        this.guitarGroup.add(dot1);
        const dot2 = new THREE.Mesh(new THREE.CircleGeometry(0.025, 8), saddleMat);
        dot2.position.set(0.12, dotY, 0.557);
        this.guitarGroup.add(dot2);
      } else {
        const dot = new THREE.Mesh(new THREE.CircleGeometry(0.025, 8), saddleMat);
        dot.position.set(0, dotY, 0.557);
        this.guitarGroup.add(dot);
      }
    });

    // Bone Nut at top of fretboard
    const nutGeo = new THREE.BoxGeometry(0.54, 0.06, 0.06);
    const nutMesh = new THREE.Mesh(nutGeo, saddleMat);
    nutMesh.position.set(0, 4.68, 0.57);
    this.guitarGroup.add(nutMesh);

    // --- 3. Headstock (Iconic 3+3 Shape) ---
    const headstockShape = new THREE.Shape();
    headstockShape.moveTo(-0.28, 0);
    headstockShape.lineTo(0.28, 0);
    headstockShape.lineTo(0.34, 1.4);
    headstockShape.bezierCurveTo(0.2, 1.6, 0.0, 1.45, 0, 1.55);
    headstockShape.bezierCurveTo(0.0, 1.45, -0.2, 1.6, -0.34, 1.4);
    headstockShape.lineTo(-0.28, 0);

    // Explicit bevelThickness prevents Three.js from falling back to default thickness of 6 units
    const headstockGeo = new THREE.ExtrudeGeometry(headstockShape, { 
      depth: 0.16, 
      bevelEnabled: true, 
      bevelSize: 0.015, 
      bevelThickness: 0.015 
    });
    const headstockMesh = new THREE.Mesh(headstockGeo, rosewoodMat);
    headstockMesh.position.set(0, 4.68, 0.44);
    headstockMesh.rotation.x = -0.15; // Realistic angled headstock pitch
    this.guitarGroup.add(headstockMesh);

    // Headstock Logo Inlay ("8VE")
    const logoBadge = new THREE.Mesh(new THREE.CircleGeometry(0.12, 16), goldMat);
    logoBadge.position.set(0, 5.75, 0.44 - ((5.75 - 4.68) * 0.15) + 0.165);
    logoBadge.rotation.x = -0.15;
    this.guitarGroup.add(logoBadge);

    // 6 Gold Tuning Machine Head Pegs (3 Left, 3 Right) - flush to angled headstock
    for (let p = 0; p < 3; p++) {
      const pegY = 4.95 + (p * 0.38);
      const pegZ = 0.44 - ((pegY - 4.68) * 0.15) + 0.08;

      // Left Tuner
      const postLeft = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.18, 8), silverMat);
      postLeft.position.set(-0.36, pegY, pegZ);
      postLeft.rotation.z = Math.PI / 2;
      this.guitarGroup.add(postLeft);

      const buttonLeft = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.15, 0.08), goldMat);
      buttonLeft.position.set(-0.46, pegY, pegZ);
      this.guitarGroup.add(buttonLeft);

      // Right Tuner
      const postRight = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.18, 8), silverMat);
      postRight.position.set(0.36, pegY, pegZ);
      postRight.rotation.z = Math.PI / 2;
      this.guitarGroup.add(postRight);

      const buttonRight = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.15, 0.08), goldMat);
      buttonRight.position.set(0.46, pegY, pegZ);
      this.guitarGroup.add(buttonRight);
    }

    // --- 4. 6 Phosphor Bronze Strings ---
    const stringGauges = [0.016, 0.014, 0.012, 0.010, 0.008, 0.006];
    for (let s = 0; s < 6; s++) {
      const startX = -0.32 + (s * 0.128); // Bridge spacing
      const endX = -0.18 + (s * 0.072);   // Nut spacing
      const postY = 4.95 + (Math.floor(s / 2) * 0.38);
      const postZ = 0.44 - ((postY - 4.68) * 0.15) + 0.08;

      const strPoints = [
        new THREE.Vector3(startX, -0.98, 0.635),
        new THREE.Vector3(endX, 4.68, 0.60),
        new THREE.Vector3(endX * 0.85, postY, postZ + 0.02)
      ];

      const curve = new THREE.CatmullRomCurve3(strPoints);
      const strGeo = new THREE.TubeGeometry(curve, 24, stringGauges[s], 6, false);
      const strMesh = new THREE.Mesh(strGeo, stringMat);
      this.guitarGroup.add(strMesh);
    }

    // Initial orientation: floating elegantly at a 3D perspective angle
    this.guitarGroup.position.set(2.4, -0.2, 0); // Offset to right half of screen
    this.guitarGroup.rotation.set(0.12, -0.35, -0.15);
    this.guitarGroup.scale.set(1.28, 1.28, 1.28);

    this.scene.add(this.guitarGroup);
  }

  buildSoundParticles() {
    // Subtle acoustic harmonic particles floating in the background
    const particleCount = 140;
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    const color1 = new THREE.Color(0xd97724);
    const color2 = new THREE.Color(0xfbbf24);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 18;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 14;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10 - 2;

      const mixed = color1.clone().lerp(color2, Math.random());
      colors[i * 3] = mixed.r;
      colors[i * 3 + 1] = mixed.g;
      colors[i * 3 + 2] = mixed.b;
    }

    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const material = new THREE.PointsMaterial({
      size: 0.08,
      vertexColors: true,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(geometry, material);
    this.scene.add(this.particles);
  }

  onMouseMove(e) {
    const windowHalfX = window.innerWidth / 2;
    const windowHalfY = window.innerHeight / 2;
    this.mouse.x = (e.clientX - windowHalfX) / windowHalfX;
    this.mouse.y = (e.clientY - windowHalfY) / windowHalfY;

    // Subtle parallax tilt towards mouse
    this.targetRotationX = 0.12 + (this.mouse.y * 0.15);
  }

  onWindowResize() {
    if (!this.container || !this.renderer || !this.camera) return;
    const width = this.container.clientWidth || window.innerWidth;
    const height = this.container.clientHeight || window.innerHeight;

    this.camera.aspect = width / height;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(width, height);

    // Responsive positioning: center guitar on mobile, right-offset on desktop
    if (this.guitarGroup) {
      if (width < 860) {
        this.guitarGroup.position.set(0, -0.6, -1.0);
        this.guitarGroup.scale.set(0.95, 0.95, 0.95);
      } else {
        this.guitarGroup.position.set(2.4, -0.2, 0);
        this.guitarGroup.scale.set(1.28, 1.28, 1.28);
      }
    }
  }

  toggleRotation() {
    this.isRotating = !this.isRotating;
    return this.isRotating;
  }

  animate() {
    this.animationFrameId = requestAnimationFrame(this.animate);

    if (this.guitarGroup) {
      const elapsedTime = this.clock.getElapsedTime();

      // Slow, hypnotic 3D rotation
      if (this.isRotating) {
        this.guitarGroup.rotation.y += 0.0055;
      }

      // Gentle vertical floating breathing motion
      this.guitarGroup.position.y += (Math.sin(elapsedTime * 1.1) * 0.0018);

      // Subtle parallax response to mouse
      this.guitarGroup.rotation.x += (this.targetRotationX - this.guitarGroup.rotation.x) * 0.04;
    }

    if (this.particles) {
      this.particles.rotation.y += 0.0008;
      this.particles.rotation.x += 0.0004;
    }

    this.renderer.render(this.scene, this.camera);
  }
}

// Attach globally
window.Guitar3DViewer = Guitar3DViewer;
