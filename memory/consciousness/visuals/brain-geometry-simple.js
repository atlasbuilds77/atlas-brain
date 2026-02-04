/**
 * Brain Geometry for Three.js - Simple Version
 * Creates anatomical brain shape with hemispheres and major lobes
 */

// Simple brain geometry creation without ES6 modules
function createSimpleBrainGeometry(detail = 32) {
  const vertices = [];
  const indices = [];
  const normals = [];
  
  const totalDetail = detail + 1;
  
  // Generate vertices for a brain-like shape
  for (let hemisphere = 0; hemisphere < 2; hemisphere++) {
    const side = hemisphere === 0 ? -1 : 1;
    
    for (let i = 0; i <= detail; i++) {
      const u = i / detail * Math.PI;
      
      for (let j = 0; j <= detail; j++) {
        const v = j / detail * Math.PI * 2;
        
        // Brain-like parametric equations
        const r = 1 + 0.2 * Math.sin(u * 4) * Math.cos(v * 3) +
                  0.1 * Math.sin(u * 8) * Math.cos(v * 6);
        
        // Hemisphere separation
        const xOffset = side * 0.1;
        
        // Convert to Cartesian
        const x = (r * Math.sin(u) * Math.cos(v) + xOffset) * 1.5;
        const y = (r * Math.sin(u) * Math.sin(v)) * 1.2;
        const z = (r * Math.cos(u)) * 1.8;
        
        // Add some lobe-specific shaping
        let lobeX = x, lobeY = y, lobeZ = z;
        
        // Frontal lobe bulge (top front)
        if (u < Math.PI/3 && Math.abs(v) < Math.PI/2) {
          lobeZ += 0.3 * Math.sin(u * 3);
        }
        
        // Occipital lobe (back)
        if (u > 2*Math.PI/3 && Math.abs(v - Math.PI) < Math.PI/3) {
          lobeZ -= 0.2 * Math.sin((u - 2*Math.PI/3) * 3);
        }
        
        // Temporal lobe (sides)
        if (u > Math.PI/3 && u < 2*Math.PI/3 && Math.abs(v - Math.PI/2) < Math.PI/4) {
          lobeX += side * 0.4 * Math.sin((u - Math.PI/3) * 3);
        }
        
        vertices.push(lobeX, lobeY, lobeZ);
        
        // Simple normal calculation
        const normal = new THREE.Vector3(lobeX, lobeY, lobeZ).normalize();
        normals.push(normal.x, normal.y, normal.z);
      }
    }
  }
  
  // Generate indices
  for (let hemisphere = 0; hemisphere < 2; hemisphere++) {
    const offset = hemisphere * totalDetail * totalDetail;
    
    for (let i = 0; i < detail; i++) {
      for (let j = 0; j < detail; j++) {
        const a = offset + i * totalDetail + j;
        const b = offset + i * totalDetail + (j + 1);
        const c = offset + (i + 1) * totalDetail + j;
        const d = offset + (i + 1) * totalDetail + (j + 1);
        
        indices.push(a, b, c);
        indices.push(b, d, c);
      }
    }
  }
  
  // Create geometry
  const geometry = new THREE.BufferGeometry();
  geometry.setAttribute('position', new THREE.BufferAttribute(new Float32Array(vertices), 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(new Float32Array(normals), 3));
  geometry.setIndex(new THREE.BufferAttribute(new Uint32Array(indices), 1));
  
  geometry.computeVertexNormals();
  
  return geometry;
}

// Brain regions data
const brainRegionsSimple = {
  frontal: {
    center: [-0.3, 0.1, 0.8],
    radius: 0.4,
    color: 0x4285F4
  },
  parietal: {
    center: [-0.2, 0.3, 0.2],
    radius: 0.35,
    color: 0x34A853
  },
  temporal: {
    center: [-0.5, -0.1, 0.1],
    radius: 0.3,
    color: 0xFBBC05
  },
  occipital: {
    center: [-0.1, 0.2, -0.6],
    radius: 0.25,
    color: 0xEA4335
  }
};

// Create a simple brain scene
function createSimpleBrainScene(detail = 32) {
  const scene = new THREE.Scene();
  
  // Create brain
  const brainGeometry = createSimpleBrainGeometry(detail);
  const brainMaterial = new THREE.MeshPhongMaterial({
    color: 0x6666FF,
    shininess: 30,
    transparent: true,
    opacity: 0.7
  });
  
  const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial);
  scene.add(brainMesh);
  
  // Add region markers
  const regionMeshes = {};
  for (const [name, region] of Object.entries(brainRegionsSimple)) {
    const geometry = new THREE.SphereGeometry(region.radius * 0.5, 8, 8);
    const material = new THREE.MeshBasicMaterial({
      color: region.color,
      transparent: true,
      opacity: 0.3,
      wireframe: true
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...region.center);
    scene.add(mesh);
    regionMeshes[name] = mesh;
  }
  
  return {
    scene,
    brainMesh,
    regionMeshes,
    brainGeometry
  };
}

// Export for use in HTML
if (typeof window !== 'undefined') {
  window.BrainGeometry = {
    createSimpleBrainGeometry,
    createSimpleBrainScene,
    brainRegionsSimple
  };
}