/**
 * NEXUS-PARK // 3D Interactive Commercial Facility Twin
 * Powered by Three.js WebGL & OrbitControls
 * Conforms to 3d-website-architect standards: 60fps, purposeful 3D, commercial usability
 */

class ThreeParkingVisualizer {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    if (!this.container) return;

    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.raycaster = new THREE.Raycaster();
    this.mouse = new THREE.Vector2();
    this.slotsData = {};
    this.slotMeshes = {};
    this.carMeshes = {};
    this.coneMeshes = {};
    this.hoveredSlotId = null;
    this.selectedSlotId = null;
    this.activeFilter = 'ALL';
    this.searchQuery = '';
    this.isInitialized = false;
    this.animationFrameId = null;
    this.clock = new THREE.Clock();

    // 16 Commercial Parking Bays Layout
    // Lane 1 (North): Bays S01 to S08 (Z = -6.5)
    // Central Ingress/Egress Lane: Z = 0
    // Lane 2 (South): Bays S09 to S16 (Z = 6.5)
    this.slotLayout = {
      'S01': { x: -17.5, z: -6.5, type: 'COMPACT', bay: 1 },
      'S02': { x: -12.5, z: -6.5, type: 'COMPACT', bay: 2 },
      'S03': { x: -7.5,  z: -6.5, type: 'COMPACT', bay: 3 },
      'S04': { x: -2.5,  z: -6.5, type: 'COMPACT', bay: 4 },
      'S05': { x: 2.5,   z: -6.5, type: 'COMPACT', bay: 5 },
      'S06': { x: 7.5,   z: -6.5, type: 'COMPACT', bay: 6 },
      'S07': { x: 12.5,  z: -6.5, type: 'COMPACT', bay: 7 },
      'S08': { x: 17.5,  z: -6.5, type: 'COMPACT', bay: 8 },

      'S09': { x: -17.5, z: 6.5, type: 'EV_CHARGING', bay: 9 },
      'S10': { x: -12.5, z: 6.5, type: 'EV_CHARGING', bay: 10 },
      'S11': { x: -7.5,  z: 6.5, type: 'EV_CHARGING', bay: 11 },
      'S12': { x: -2.5,  z: 6.5, type: 'EV_CHARGING', bay: 12 },
      'S13': { x: 2.5,   z: 6.5, type: 'SUV_HEAVY', bay: 13 },
      'S14': { x: 7.5,   z: 6.5, type: 'SUV_HEAVY', bay: 14 },
      'S15': { x: 12.5,  z: 6.5, type: 'VALET', bay: 15 },
      'S16': { x: 17.5,  z: 6.5, type: 'VALET', bay: 16 }
    };

    this.init();
  }

  init() {
    if (!window.THREE) {
      console.warn('Three.js library not loaded yet');
      return;
    }

    const width = this.container.clientWidth || 800;
    const height = this.container.clientHeight || 520;

    // 1. Scene
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x06080d);
    this.scene.fog = new THREE.FogExp2(0x06080d, 0.014);

    // 2. Camera
    this.camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    this.camera.position.set(0, 32, 28);
    this.camera.lookAt(0, 0, 0);

    // 3. Renderer
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
    this.renderer.setSize(width, height);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    this.container.innerHTML = '';
    this.container.appendChild(this.renderer.domElement);

    // 4. OrbitControls
    if (window.THREE.OrbitControls) {
      this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
      this.controls.enableDamping = true;
      this.controls.dampingFactor = 0.05;
      this.controls.maxPolarAngle = Math.PI / 2.05;
      this.controls.minDistance = 12;
      this.controls.maxDistance = 65;
      this.controls.target.set(0, 0, 0);
    }

    // 5. Lighting & Geometry
    this.setupLighting();
    this.createFacilityGround();
    this.createParkingBays();

    // 6. Events & Animation Loop
    this.bindEvents();
    this.isInitialized = true;
    this.animate();
  }

  setupLighting() {
    const ambientLight = new THREE.AmbientLight(0x1a2638, 1.25);
    this.scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xdbeafe, 1.85);
    dirLight.position.set(22, 42, 22);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 0.5;
    dirLight.shadow.camera.far = 100;
    dirLight.shadow.camera.left = -30;
    dirLight.shadow.camera.right = 30;
    dirLight.shadow.camera.top = 22;
    dirLight.shadow.camera.bottom = -22;
    dirLight.shadow.bias = -0.0005;
    this.scene.add(dirLight);

    const rimLight = new THREE.DirectionalLight(0x0ea5e9, 0.95);
    rimLight.position.set(-25, 16, -20);
    this.scene.add(rimLight);

    const facilityFlood = new THREE.PointLight(0x10e761, 0.8, 40, 1.8);
    facilityFlood.position.set(0, 18, 0);
    this.scene.add(facilityFlood);
  }

  createFacilityGround() {
    const groundGeo = new THREE.PlaneGeometry(62, 38);
    const groundMat = new THREE.MeshStandardMaterial({
      color: 0x0c1017,
      roughness: 0.85,
      metalness: 0.15
    });
    const ground = new THREE.Mesh(groundGeo, groundMat);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    this.scene.add(ground);

    // Central Driving Lane Divider Lines
    const laneGeo = new THREE.PlaneGeometry(52, 0.35);
    const laneMat = new THREE.MeshBasicMaterial({ color: 0x334155, transparent: true, opacity: 0.65 });

    const topDivider = new THREE.Mesh(laneGeo, laneMat);
    topDivider.rotation.x = -Math.PI / 2;
    topDivider.position.set(0, 0.015, -2.6);
    this.scene.add(topDivider);

    const btmDivider = new THREE.Mesh(laneGeo, laneMat);
    btmDivider.rotation.x = -Math.PI / 2;
    btmDivider.position.set(0, 0.015, 2.6);
    this.scene.add(btmDivider);

    // Dashed Centerline
    for (let i = 0; i < 13; i++) {
      const dashGeo = new THREE.PlaneGeometry(2.4, 0.25);
      const dashMat = new THREE.MeshBasicMaterial({ color: 0x64748b });
      const dash = new THREE.Mesh(dashGeo, dashMat);
      dash.rotation.x = -Math.PI / 2;
      dash.position.set(-23 + i * 3.8, 0.02, 0);
      this.scene.add(dash);
    }

    // Directional Traffic Arrows
    this.createTarmacArrow(-16, 1.3, 1);
    this.createTarmacArrow(16, -1.3, -1);

    // Perimeter Curbs
    const curbMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.7, metalness: 0.3 });
    const topCurb = new THREE.Mesh(new THREE.BoxGeometry(56, 0.45, 0.65), curbMat);
    topCurb.position.set(0, 0.22, -11.8);
    topCurb.castShadow = true;
    topCurb.receiveShadow = true;
    this.scene.add(topCurb);

    const btmCurb = new THREE.Mesh(new THREE.BoxGeometry(56, 0.45, 0.65), curbMat);
    btmCurb.position.set(0, 0.22, 11.8);
    btmCurb.castShadow = true;
    btmCurb.receiveShadow = true;
    this.scene.add(btmCurb);
  }

  createTarmacArrow(x, z, dir) {
    const arrowShape = new THREE.Shape();
    arrowShape.moveTo(0, -1.2 * dir);
    arrowShape.lineTo(0.65, -0.4 * dir);
    arrowShape.lineTo(0.28, -0.4 * dir);
    arrowShape.lineTo(0.28, 1.2 * dir);
    arrowShape.lineTo(-0.28, 1.2 * dir);
    arrowShape.lineTo(-0.28, -0.4 * dir);
    arrowShape.lineTo(-0.65, -0.4 * dir);
    arrowShape.closePath();

    const arrowGeo = new THREE.ShapeGeometry(arrowShape);
    const arrowMat = new THREE.MeshBasicMaterial({ color: 0x0ea5e9, transparent: true, opacity: 0.5 });
    const arrow = new THREE.Mesh(arrowGeo, arrowMat);
    arrow.rotation.x = -Math.PI / 2;
    arrow.rotation.z = Math.PI / 2;
    arrow.position.set(x, 0.025, z);
    this.scene.add(arrow);
  }

  createParkingBays() {
    const slotGroup = new THREE.Group();

    Object.keys(this.slotLayout).forEach(slotId => {
      const cfg = this.slotLayout[slotId];
      const isTopRow = cfg.z < 0;

      const bayWidth = 4.3;
      const bayLength = 6.9;
      const bayGeo = new THREE.BoxGeometry(bayWidth, 0.08, bayLength);

      const bayMat = new THREE.MeshStandardMaterial({
        color: 0x111827,
        roughness: 0.6,
        metalness: 0.2
      });

      const bayMesh = new THREE.Mesh(bayGeo, bayMat);
      bayMesh.position.set(cfg.x, 0.04, cfg.z);
      bayMesh.receiveShadow = true;
      bayMesh.userData = { slotId, type: cfg.type, bay: cfg.bay };

      // Glowing bay border
      const borderGeo = new THREE.BufferGeometry();
      const hw = bayWidth / 2 - 0.1;
      const hl = bayLength / 2 - 0.1;
      const points = [
        new THREE.Vector3(-hw, 0.06, -hl),
        new THREE.Vector3(hw, 0.06, -hl),
        new THREE.Vector3(hw, 0.06, hl),
        new THREE.Vector3(-hw, 0.06, hl),
        new THREE.Vector3(-hw, 0.06, -hl)
      ];
      borderGeo.setFromPoints(points);

      const borderMat = new THREE.LineBasicMaterial({ color: 0x10e761, linewidth: 2 });
      const borderLine = new THREE.Line(borderGeo, borderMat);
      bayMesh.add(borderLine);

      // Floor point light
      const bayLight = new THREE.PointLight(0x10e761, 0.45, 6.5);
      bayLight.position.set(0, 0.3, isTopRow ? -hl : hl);
      bayMesh.add(bayLight);

      // EV Charging Station post
      if (cfg.type === 'EV_CHARGING') {
        const pillar = new THREE.Mesh(
          new THREE.BoxGeometry(0.55, 2.1, 0.45),
          new THREE.MeshStandardMaterial({ color: 0x06b6d4, roughness: 0.3, metalness: 0.7 })
        );
        pillar.position.set(hw - 0.45, 1.05, isTopRow ? -hl + 0.55 : hl - 0.55);
        pillar.castShadow = true;

        const beacon = new THREE.Mesh(
          new THREE.SphereGeometry(0.12, 16, 16),
          new THREE.MeshBasicMaterial({ color: 0x00f0ff })
        );
        beacon.position.y = 1.1;
        pillar.add(beacon);
        bayMesh.add(pillar);
      }

      // Valet / Priority Pedestal
      if (cfg.type === 'VALET') {
        const valetPost = new THREE.Mesh(
          new THREE.CylinderGeometry(0.16, 0.22, 1.9, 16),
          new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8, roughness: 0.2 })
        );
        valetPost.position.set(-hw + 0.45, 0.95, isTopRow ? -hl + 0.55 : hl - 0.55);
        valetPost.castShadow = true;
        bayMesh.add(valetPost);
      }

      this.slotMeshes[slotId] = {
        mesh: bayMesh,
        border: borderLine,
        light: bayLight,
        cfg: cfg
      };

      slotGroup.add(bayMesh);
    });

    this.scene.add(slotGroup);
  }

  createVehicleModel(vehicleType, plate, pid) {
    const carGroup = new THREE.Group();

    let bodyWidth = 2.4;
    let bodyLength = 4.8;
    let bodyHeight = 1.2;
    let cabinLength = 2.8;
    let cabinHeight = 0.85;

    let bodyColor = 0x2563eb;
    let emissiveColor = 0x000000;

    if (vehicleType === 'EMERGENCY') {
      bodyColor = 0xf8fafc;
      bodyHeight = 1.6;
      cabinHeight = 1.1;
      emissiveColor = 0x1e293b;
    } else if (vehicleType === 'EV') {
      bodyColor = 0x06b6d4;
      emissiveColor = 0x083344;
    } else if (vehicleType === 'SUV') {
      bodyColor = 0x334155;
      bodyWidth = 2.6;
      bodyLength = 5.2;
      bodyHeight = 1.5;
      cabinHeight = 1.0;
    } else {
      const colors = [0x1e293b, 0x3b82f6, 0x475569, 0x0284c7, 0x0f172a];
      bodyColor = colors[Math.abs(plate.charCodeAt(0) + plate.charCodeAt(plate.length - 1)) % colors.length];
    }

    const chassis = new THREE.Mesh(
      new THREE.BoxGeometry(bodyWidth, bodyHeight, bodyLength),
      new THREE.MeshStandardMaterial({ color: bodyColor, roughness: 0.35, metalness: 0.75, emissive: emissiveColor })
    );
    chassis.position.y = bodyHeight / 2 + 0.35;
    chassis.castShadow = true;
    chassis.receiveShadow = true;
    carGroup.add(chassis);

    const cabin = new THREE.Mesh(
      new THREE.BoxGeometry(bodyWidth * 0.88, cabinHeight, cabinLength),
      new THREE.MeshStandardMaterial({ color: 0x090d16, roughness: 0.1, metalness: 0.95 })
    );
    cabin.position.set(0, chassis.position.y + bodyHeight / 2 + cabinHeight / 2 - 0.05, -0.2);
    cabin.castShadow = true;
    carGroup.add(cabin);

    // 4 Wheels
    const wheelGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.35, 18);
    const wheelMat = new THREE.MeshStandardMaterial({ color: 0x0a0a0a, roughness: 0.9 });
    const wheelOffsets = [
      [-bodyWidth / 2 - 0.05, 0.42, bodyLength / 3],
      [bodyWidth / 2 + 0.05,  0.42, bodyLength / 3],
      [-bodyWidth / 2 - 0.05, 0.42, -bodyLength / 3],
      [bodyWidth / 2 + 0.05,  0.42, -bodyLength / 3]
    ];
    wheelOffsets.forEach(([wx, wy, wz]) => {
      const wheel = new THREE.Mesh(wheelGeo, wheelMat);
      wheel.rotation.z = Math.PI / 2;
      wheel.position.set(wx, wy, wz);
      wheel.castShadow = true;
      carGroup.add(wheel);
    });

    // Headlights & Taillights
    const hlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.2, 0.1), new THREE.MeshBasicMaterial({ color: 0xffffff }));
    hlLeft.position.set(-bodyWidth / 3, chassis.position.y, bodyLength / 2 + 0.02);
    const hlRight = hlLeft.clone();
    hlRight.position.x = bodyWidth / 3;
    carGroup.add(hlLeft);
    carGroup.add(hlRight);

    const tlLeft = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.18, 0.1), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
    tlLeft.position.set(-bodyWidth / 3, chassis.position.y, -bodyLength / 2 - 0.02);
    const tlRight = tlLeft.clone();
    tlRight.position.x = bodyWidth / 3;
    carGroup.add(tlLeft);
    carGroup.add(tlRight);

    // Emergency Strobe
    if (vehicleType === 'EMERGENCY') {
      const strobeGroup = new THREE.Group();
      const strobeBase = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.15, 0.4), new THREE.MeshBasicMaterial({ color: 0x111827 }));
      strobeBase.position.set(0, cabin.position.y + cabinHeight / 2 + 0.1, 0);

      const redBeacon = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.2, 0.35), new THREE.MeshBasicMaterial({ color: 0xef4444 }));
      redBeacon.position.set(-0.4, 0.1, 0);

      const blueBeacon = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.2, 0.35), new THREE.MeshBasicMaterial({ color: 0x3b82f6 }));
      blueBeacon.position.set(0.4, 0.1, 0);

      strobeBase.add(redBeacon);
      strobeBase.add(blueBeacon);
      strobeGroup.add(strobeBase);
      carGroup.add(strobeGroup);
      carGroup.userData.strobe = { red: redBeacon, blue: blueBeacon };
    }

    // Floating 3D Plate Pill
    const plateSprite = this.createPlateSprite(plate);
    plateSprite.position.set(0, chassis.position.y + bodyHeight + 1.25, 0);
    carGroup.add(plateSprite);

    carGroup.userData = { plate, pid, vehicleType };
    return carGroup;
  }

  createPlateSprite(plate) {
    const canvas = document.createElement('canvas');
    canvas.width = 256;
    canvas.height = 72;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = 'rgba(7, 10, 16, 0.92)';
    ctx.strokeStyle = '#00f0ff';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.roundRect(6, 6, 244, 60, 12);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 28px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(plate, 128, 44);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(3.2, 0.9, 1.0);
    return sprite;
  }

  createMaintenanceCone() {
    const coneGroup = new THREE.Group();
    const cone = new THREE.Mesh(
      new THREE.ConeGeometry(0.35, 1.1, 16),
      new THREE.MeshStandardMaterial({ color: 0xef4444, roughness: 0.4 })
    );
    cone.position.y = 0.55;
    cone.castShadow = true;
    coneGroup.add(cone);

    const stripe = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.27, 0.25, 16),
      new THREE.MeshBasicMaterial({ color: 0xffffff })
    );
    stripe.position.y = 0.55;
    coneGroup.add(stripe);

    return coneGroup;
  }

  updateSlots(slots) {
    if (!slots || !this.isInitialized) return;
    this.slotsData = slots;

    Object.keys(slots).forEach(slotId => {
      const slot = slots[slotId];
      const slotNode = this.slotMeshes[slotId];
      if (!slotNode) return;

      const isOccupied = slot.status === 'OCCUPIED';
      const isReserved = slot.status === 'RESERVED';
      const isOutOfService = slot.status === 'OUT_OF_SERVICE';
      const isTopRow = slotNode.cfg.z < 0;

      // Color mapping
      let glowColor = 0x10e761; // Lime (Available)
      if (isOccupied) glowColor = 0x00f0ff; // Cyan (Occupied)
      else if (isReserved) glowColor = 0xf59e0b; // Amber (Reserved)
      else if (isOutOfService) glowColor = 0xef4444; // Red (Out of service)

      if (slotId === this.selectedSlotId) {
        glowColor = 0xffffff;
      }

      slotNode.border.material.color.setHex(glowColor);
      slotNode.light.color.setHex(glowColor);
      slotNode.light.intensity = isOccupied ? 0.8 : (isReserved ? 0.6 : 0.4);

      // Filtering visibility check
      let matchesFilter = true;
      if (this.activeFilter === 'AVAILABLE' && slot.status !== 'FREE') matchesFilter = false;
      if (this.activeFilter === 'OCCUPIED' && slot.status !== 'OCCUPIED') matchesFilter = false;
      if (this.activeFilter === 'RESERVED' && slot.status !== 'RESERVED') matchesFilter = false;
      if (this.activeFilter === 'MAINTENANCE' && slot.status !== 'OUT_OF_SERVICE') matchesFilter = false;

      // Search query check
      if (this.searchQuery) {
        const matchesSlot = slotId.toLowerCase().includes(this.searchQuery);
        const matchesPlate = (slot.current_plate || '').toLowerCase().includes(this.searchQuery);
        if (!matchesSlot && !matchesPlate) matchesFilter = false;
      }

      slotNode.mesh.visible = matchesFilter;

      // Maintenance cone management
      if (isOutOfService) {
        if (!this.coneMeshes[slotId]) {
          const cone = this.createMaintenanceCone();
          cone.position.set(slotNode.cfg.x, 0.05, slotNode.cfg.z);
          this.scene.add(cone);
          this.coneMeshes[slotId] = cone;
        }
        this.coneMeshes[slotId].visible = matchesFilter;
      } else if (this.coneMeshes[slotId]) {
        this.scene.remove(this.coneMeshes[slotId]);
        delete this.coneMeshes[slotId];
      }

      // Vehicle management
      if (isOccupied && slot.current_plate) {
        const currentCar = this.carMeshes[slotId];
        if (!currentCar || currentCar.userData.plate !== slot.current_plate) {
          if (currentCar) {
            this.scene.remove(currentCar);
            delete this.carMeshes[slotId];
          }

          let vType = 'STANDARD';
          if (slotNode.cfg.type === 'EV_CHARGING') vType = 'EV';
          if (slotNode.cfg.type === 'SUV_HEAVY') vType = 'SUV';
          if (slotNode.cfg.type === 'VALET') vType = 'EMERGENCY';

          const newCar = this.createVehicleModel(vType, slot.current_plate, slot.current_pid || 'P---');
          newCar.position.set(slotNode.cfg.x, 0.05, slotNode.cfg.z);
          newCar.rotation.y = isTopRow ? 0 : Math.PI;

          newCar.position.y = 2.5;
          this.animateCarDropIn(newCar, 0.05);

          this.scene.add(newCar);
          this.carMeshes[slotId] = newCar;
        }
        if (this.carMeshes[slotId]) {
          this.carMeshes[slotId].visible = matchesFilter;
        }
      } else {
        if (this.carMeshes[slotId]) {
          this.animateCarDepart(this.carMeshes[slotId], () => {
            this.scene.remove(this.carMeshes[slotId]);
            delete this.carMeshes[slotId];
          });
        }
      }
    });
  }

  animateCarDropIn(car, targetY) {
    const startY = car.position.y;
    let t = 0;
    const interval = setInterval(() => {
      t += 0.08;
      car.position.y = THREE.MathUtils.lerp(startY, targetY, Math.min(t, 1));
      if (t >= 1) clearInterval(interval);
    }, 16);
  }

  animateCarDepart(car, onComplete) {
    let t = 0;
    const interval = setInterval(() => {
      t += 0.1;
      car.position.y += 0.3;
      car.scale.multiplyScalar(0.92);
      if (t >= 1) {
        clearInterval(interval);
        if (onComplete) onComplete();
      }
    }, 16);
  }

  setFilter(filterMode) {
    this.activeFilter = filterMode;
    if (this.slotsData) {
      this.updateSlots(this.slotsData);
    }
  }

  setSearch(query) {
    this.searchQuery = (query || '').toLowerCase().trim();
    if (this.slotsData) {
      this.updateSlots(this.slotsData);
    }
  }

  bindEvents() {
    window.addEventListener('resize', () => {
      if (!this.container || !this.renderer || !this.camera) return;
      const w = this.container.clientWidth;
      const h = this.container.clientHeight;
      if (w > 0 && h > 0) {
        this.camera.aspect = w / h;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(w, h);
      }
    });

    this.container.addEventListener('mousemove', (e) => {
      const rect = this.container.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this.checkRaycastHover();
    });

    this.container.addEventListener('click', (e) => {
      const rect = this.container.getBoundingClientRect();
      this.mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      this.mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
      this.handleSlotClick();
    });

    const btnIso = document.getElementById('btn-3d-cam-iso');
    const btnTop = document.getElementById('btn-3d-cam-top');
    const btnGate = document.getElementById('btn-3d-cam-gate');

    if (btnIso) btnIso.addEventListener('click', () => this.setCameraPreset('iso'));
    if (btnTop) btnTop.addEventListener('click', () => this.setCameraPreset('top'));
    if (btnGate) btnGate.addEventListener('click', () => this.setCameraPreset('gate'));
  }

  checkRaycastHover() {
    if (!this.camera || !this.scene) return;
    this.raycaster.setFromCamera(this.mouse, this.camera);

    const interactiveBays = Object.values(this.slotMeshes).map(s => s.mesh).filter(m => m.visible);
    const intersects = this.raycaster.intersectObjects(interactiveBays, false);

    const tooltip = document.getElementById('three-hud-tooltip');

    if (intersects.length > 0) {
      const hitBay = intersects[0].object;
      const slotId = hitBay.userData.slotId;
      this.container.style.cursor = 'pointer';

      if (this.hoveredSlotId !== slotId) {
        this.hoveredSlotId = slotId;
        const slotData = this.slotsData[slotId];
        if (tooltip && slotData) {
          const isOcc = slotData.status === 'OCCUPIED';
          const isRes = slotData.status === 'RESERVED';
          const isMaint = slotData.status === 'OUT_OF_SERVICE';

          let statusColor = '#10e761';
          let statusLabel = 'AVAILABLE';
          if (isOcc) { statusColor = '#00f0ff'; statusLabel = 'OCCUPIED'; }
          else if (isRes) { statusColor = '#f59e0b'; statusLabel = 'RESERVED'; }
          else if (isMaint) { statusColor = '#ef4444'; statusLabel = 'OUT OF SERVICE'; }

          tooltip.innerHTML = `
            <div style="font-weight: 700; color: #f8fafc; font-size: 0.85rem; display: flex; justify-content: space-between;">
              <span>Space ${slotId}</span>
              <span style="color: ${statusColor};">${statusLabel}</span>
            </div>
            <div style="font-size: 0.72rem; color: #94a3b8; margin-top: 2px;">
              Category: ${slotData.slot_type} · Bay #${slotData.bay_number}
            </div>
            ${isOcc ? `
              <div style="margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.1); font-family: monospace; font-size: 0.78rem; color: #38bdf8;">
                🚘 ${slotData.current_plate}
              </div>
            ` : (isRes ? '<div style="color: #f59e0b; font-size: 0.72rem; margin-top: 4px;">Advance Booking Held</div>' : (isMaint ? '<div style="color: #ef4444; font-size: 0.72rem; margin-top: 4px;">Under Maintenance</div>' : '<div style="color: #10e761; font-size: 0.72rem; margin-top: 4px;">Ready for Vehicle Assignment</div>'))}
          `;
          tooltip.style.display = 'block';
        }
      }
    } else {
      this.container.style.cursor = 'default';
      this.hoveredSlotId = null;
      if (tooltip) tooltip.style.display = 'none';
    }
  }

  handleSlotClick() {
    if (!this.camera || !this.scene) return;
    this.raycaster.setFromCamera(this.mouse, this.camera);

    const interactiveBays = Object.values(this.slotMeshes).map(s => s.mesh).filter(m => m.visible);
    const intersects = this.raycaster.intersectObjects(interactiveBays, false);

    if (intersects.length > 0) {
      const slotId = intersects[0].object.userData.slotId;
      this.selectSlot(slotId);
      if (window.parkingLotViz) {
        window.parkingLotViz.inspectSlot(slotId);
      }
      if (window.app) {
        window.app.playSound('click');
      }
    }
  }

  selectSlot(slotId) {
    this.selectedSlotId = slotId;
    if (this.slotsData) {
      this.updateSlots(this.slotsData);
    }
  }

  setCameraPreset(preset) {
    if (!this.camera || !this.controls) return;
    if (window.app) window.app.playSound('click');

    let targetPos = { x: 0, y: 32, z: 28 };
    let lookTarget = { x: 0, y: 0, z: 0 };

    if (preset === 'top') {
      targetPos = { x: 0, y: 44, z: 0.1 };
    } else if (preset === 'gate') {
      targetPos = { x: -28, y: 14, z: 12 };
      lookTarget = { x: -5, y: 0, z: 0 };
    } else {
      targetPos = { x: 22, y: 28, z: 26 };
    }

    this.animateCameraMove(targetPos, lookTarget);
  }

  animateCameraMove(pos, look) {
    const startPos = this.camera.position.clone();
    let t = 0;
    const interval = setInterval(() => {
      t += 0.05;
      const factor = THREE.MathUtils.smoothstep(t, 0, 1);
      this.camera.position.set(
        THREE.MathUtils.lerp(startPos.x, pos.x, factor),
        THREE.MathUtils.lerp(startPos.y, pos.y, factor),
        THREE.MathUtils.lerp(startPos.z, pos.z, factor)
      );
      this.controls.target.set(look.x, look.y, look.z);
      this.controls.update();

      if (t >= 1) clearInterval(interval);
    }, 16);
  }

  animate() {
    this.animationFrameId = requestAnimationFrame(() => this.animate());

    const delta = this.clock.getDelta();
    const elapsedTime = this.clock.getElapsedTime();

    Object.values(this.carMeshes).forEach(car => {
      if (car.userData.strobe) {
        const strobeState = Math.sin(elapsedTime * 12) > 0;
        car.userData.strobe.red.material.color.setHex(strobeState ? 0xef4444 : 0x330000);
        car.userData.strobe.blue.material.color.setHex(!strobeState ? 0x3b82f6 : 0x000033);
      }
    });

    if (this.controls) {
      this.controls.update();
    }

    if (this.renderer && this.scene && this.camera) {
      this.renderer.render(this.scene, this.camera);
    }
  }

  dispose() {
    if (this.animationFrameId) {
      cancelAnimationFrame(this.animationFrameId);
    }
    if (this.renderer) {
      this.renderer.dispose();
    }
  }
}

window.ThreeParkingVisualizer = ThreeParkingVisualizer;
