/**
 * Brain Geometry for Three.js
 * Creates anatomical brain shape with hemispheres and major lobes
 * Uses parametric equations based on modified spherical harmonics
 */

export function createBrainGeometry(options = {}) {
  const {
    detail = 32,          // Resolution of the mesh (higher = more vertices)
    scale = 1.0,          // Overall scale
    hemisphereSplit = 0.1, // Gap between hemispheres
    foldDepth = 0.15,     // Depth of cortical folds
    asymmetry = 0.05      // Natural asymmetry between hemispheres
  } = options;

  // Create vertices for brain surface using parametric equations
  const vertices = [];
  const indices = [];
  const normals = [];
  
  // Major brain regions with their parametric coordinates
  const regions = {
    frontal: { uRange: [0, Math.PI/3], vRange: [0, Math.PI] },
    parietal: { uRange: [Math.PI/3, 2*Math.PI/3], vRange: [0, Math.PI] },
    temporal: { uRange: [2*Math.PI/3, Math.PI], vRange: [Math.PI/4, 3*Math.PI/4] },
    occipital: { uRange: [2*Math.PI/3, Math.PI], vRange: [0, Math.PI/4] }
  };

  // Generate vertices for left and right hemispheres
  for (let hemisphere = 0; hemisphere < 2; hemisphere++) {
    const side = hemisphere === 0 ? -1 : 1; // -1 for left, 1 for right
    const hemisphereOffset = side * hemisphereSplit * 0.5;
    const hemisphereAsymmetry = side * asymmetry;

    for (let i = 0; i <= detail; i++) {
      const u = i / detail * Math.PI; // 0 to PI
      
      for (let j = 0; j <= detail; j++) {
        const v = j / detail * Math.PI * 2; // 0 to 2PI
        
        // Base spherical coordinates
        const radius = getBrainRadius(u, v, side);
        
        // Convert to Cartesian coordinates with brain-specific shaping
        const x = (radius * Math.sin(u) * Math.cos(v) + hemisphereOffset + 
                  getLobePerturbation(u, v, 'x', side) + hemisphereAsymmetry) * scale;
        const y = (radius * Math.sin(u) * Math.sin(v) + 
                  getLobePerturbation(u, v, 'y', side)) * scale;
        const z = (radius * Math.cos(u) + 
                  getLobePerturbation(u, v, 'z', side)) * scale;
        
        // Add cortical folds (sulci and gyri)
        const foldFactor = getFoldPattern(u, v, side);
        const foldX = x * (1 + foldDepth * foldFactor);
        const foldY = y * (1 + foldDepth * foldFactor);
        const foldZ = z * (1 + foldDepth * foldFactor);
        
        vertices.push(foldX, foldY, foldZ);
        
        // Calculate approximate normal (will be refined later)
        const normal = calculateNormal(u, v, side);
        normals.push(normal.x, normal.y, normal.z);
      }
    }
  }

  // Generate indices for triangle faces
  const totalDetail = detail + 1;
  for (let hemisphere = 0; hemisphere < 2; hemisphere++) {
    const offset = hemisphere * totalDetail * totalDetail;
    
    for (let i = 0; i < detail; i++) {
      for (let j = 0; j < detail; j++) {
        const a = offset + i * totalDetail + j;
        const b = offset + i * totalDetail + (j + 1);
        const c = offset + (i + 1) * totalDetail + j;
        const d = offset + (i + 1) * totalDetail + (j + 1);
        
        // Two triangles per quad
        indices.push(a, b, c);
        indices.push(b, d, c);
      }
    }
  }

  // Create Three.js BufferGeometry
  const geometry = new THREE.BufferGeometry();
  
  const verticesArray = new Float32Array(vertices);
  const indicesArray = new Uint32Array(indices);
  const normalsArray = new Float32Array(normals);
  
  geometry.setAttribute('position', new THREE.BufferAttribute(verticesArray, 3));
  geometry.setAttribute('normal', new THREE.BufferAttribute(normalsArray, 3));
  geometry.setIndex(new THREE.BufferAttribute(indicesArray, 1));
  
  // Compute vertex normals for smooth shading
  geometry.computeVertexNormals();
  
  return geometry;
}

/**
 * Get brain radius with lobe-specific shaping
 */
function getBrainRadius(u, v, side) {
  // Base ellipsoid shape
  const a = 1.0; // x-radius
  const b = 0.8; // y-radius (flattened)
  const c = 1.2; // z-radius (elongated)
  
  // Lobe-specific modifications
  let lobeFactor = 1.0;
  
  // Frontal lobe bulge
  if (u < Math.PI/3) {
    lobeFactor += 0.1 * Math.sin(u * 3) * Math.cos(v * 2);
  }
  
  // Occipital lobe protrusion
  if (u > 2*Math.PI/3 && Math.abs(v - Math.PI) < Math.PI/4) {
    lobeFactor += 0.15 * Math.sin((u - 2*Math.PI/3) * 3);
  }
  
  // Temporal lobe extension
  if (u > Math.PI/2 && u < 3*Math.PI/4 && Math.abs(v - Math.PI/2) < Math.PI/3) {
    lobeFactor += 0.2 * Math.sin((u - Math.PI/2) * 4) * Math.cos(v * 3);
  }
  
  // Hemisphere asymmetry
  const asymmetry = side * 0.05 * Math.sin(u * 2) * Math.cos(v);
  
  return (a * b * c) / Math.sqrt(
    (b * c * Math.sin(u) * Math.cos(v))**2 +
    (a * c * Math.sin(u) * Math.sin(v))**2 +
    (a * b * Math.cos(u))**2
  ) * lobeFactor + asymmetry;
}

/**
 * Get lobe-specific perturbations for more anatomical detail
 */
function getLobePerturbation(u, v, axis, side) {
  let perturbation = 0;
  
  // Identify which lobe this point belongs to
  if (u < Math.PI/3) {
    // Frontal lobe
    perturbation = getFrontalLobePerturbation(u, v, axis, side);
  } else if (u < 2*Math.PI/3) {
    // Parietal lobe
    perturbation = getParietalLobePerturbation(u, v, axis, side);
  } else if (Math.abs(v - Math.PI/2) < Math.PI/3) {
    // Temporal lobe
    perturbation = getTemporalLobePerturbation(u, v, axis, side);
  } else {
    // Occipital lobe
    perturbation = getOccipitalLobePerturbation(u, v, axis, side);
  }
  
  return perturbation;
}

function getFrontalLobePerturbation(u, v, axis, side) {
  const normalizedU = u / (Math.PI/3);
  switch(axis) {
    case 'x':
      return 0.1 * side * Math.sin(normalizedU * Math.PI) * Math.cos(v * 2);
    case 'y':
      return 0.05 * Math.sin(normalizedU * Math.PI * 2) * Math.sin(v);
    case 'z':
      return 0.08 * (1 - normalizedU) * Math.cos(v);
    default:
      return 0;
  }
}

function getParietalLobePerturbation(u, v, axis, side) {
  const normalizedU = (u - Math.PI/3) / (Math.PI/3);
  switch(axis) {
    case 'x':
      return 0.05 * side * Math.sin(normalizedU * Math.PI) * Math.cos(v * 3);
    case 'y':
      return 0.03 * Math.cos(normalizedU * Math.PI) * Math.sin(v * 2);
    case 'z':
      return 0.04 * Math.sin(normalizedU * Math.PI * 2) * Math.cos(v);
    default:
      return 0;
  }
}

function getTemporalLobePerturbation(u, v, axis, side) {
  const normalizedU = (u - 2*Math.PI/3) / (Math.PI/3);
  const normalizedV = (v - Math.PI/2) / (Math.PI/3);
  switch(axis) {
    case 'x':
      return 0.15 * side * Math.sin(normalizedU * Math.PI) * Math.cos(normalizedV * Math.PI);
    case 'y':
      return 0.1 * Math.cos(normalizedU * Math.PI) * Math.sin(normalizedV * Math.PI * 2);
    case 'z':
      return -0.1 * normalizedU * Math.cos(normalizedV * Math.PI);
    default:
      return 0;
  }
}

function getOccipitalLobePerturbation(u, v, axis, side) {
  const normalizedU = (u - 2*Math.PI/3) / (Math.PI/3);
  switch(axis) {
    case 'x':
      return 0.08 * side * Math.sin(normalizedU * Math.PI) * Math.cos(v);
    case 'y':
      return 0.04 * Math.cos(normalizedU * Math.PI) * Math.sin(v * 2);
    case 'z':
      return 0.12 * normalizedU * Math.cos(v * 3);
    default:
      return 0;
  }
}

/**
 * Generate cortical fold pattern (sulci and gyri)
 */
function getFoldPattern(u, v, side) {
  // Multiple frequencies for realistic folding
  const fold1 = 0.3 * Math.sin(u * 8 + side * 0.5) * Math.cos(v * 6);
  const fold2 = 0.2 * Math.sin(u * 12) * Math.cos(v * 8 + side * 0.3);
  const fold3 = 0.15 * Math.sin(u * 16 + side * 0.7) * Math.cos(v * 10);
  
  // Regional variation
  let regionalFactor = 1.0;
  if (u < Math.PI/3) {
    // More folds in frontal lobe
    regionalFactor = 1.2;
  } else if (u > 2*Math.PI/3) {
    // Different pattern in occipital lobe
    regionalFactor = 0.8;
  }
  
  return (fold1 + fold2 + fold3) * regionalFactor;
}

/**
 * Calculate surface normal at parametric coordinates
 */
function calculateNormal(u, v, side) {
  // Approximate normal using partial derivatives
  const epsilon = 0.001;
  
  // Get points around (u, v)
  const p0 = getCartesian(u, v, side);
  const p1 = getCartesian(u + epsilon, v, side);
  const p2 = getCartesian(u, v + epsilon, side);
  
  // Calculate tangent vectors
  const du = new THREE.Vector3().subVectors(p1, p0);
  const dv = new THREE.Vector3().subVectors(p2, p0);
  
  // Cross product gives normal
  const normal = new THREE.Vector3().crossVectors(du, dv).normalize();
  
  // Ensure normal points outward
  const center = new THREE.Vector3(side * 0.1, 0, 0);
  const toCenter = new THREE.Vector3().subVectors(center, p0);
  if (normal.dot(toCenter) > 0) {
    normal.negate();
  }
  
  return normal;
}

/**
 * Convert parametric coordinates to Cartesian with all shaping applied
 */
function getCartesian(u, v, side) {
  const radius = getBrainRadius(u, v, side);
  const hemisphereOffset = side * 0.05;
  
  const x = radius * Math.sin(u) * Math.cos(v) + hemisphereOffset + 
           getLobePerturbation(u, v, 'x', side);
  const y = radius * Math.sin(u) * Math.sin(v) + 
           getLobePerturbation(u, v, 'y', side);
  const z = radius * Math.cos(u) + 
           getLobePerturbation(u, v, 'z', side);
  
  return new THREE.Vector3(x, y, z);
}

/**
 * Brain region definitions with approximate centers and radii
 */
export const brainRegions = {
  frontal: {
    center: [-0.3, 0.1, 0.8],
    radius: 0.4,
    color: 0x4285F4, // Blue
    description: "Frontal lobe - executive functions, decision making"
  },
  parietal: {
    center: [-0.2, 0.3, 0.2],
    radius: 0.35,
    color: 0x34A853, // Green
    description: "Parietal lobe - sensory integration, spatial awareness"
  },
  temporal: {
    center: [-0.5, -0.1, 0.1],
    radius: 0.3,
    color: 0xFBBC05, // Yellow
    description: "Temporal lobe - auditory processing, memory"
  },
  occipital: {
    center: [-0.1, 0.2, -0.6],
    radius: 0.25,
    color: 0xEA4335, // Red
    description: "Occipital lobe - visual processing"
  },
  cerebellum: {
    center: [-0.05, -0.4, -0.1],
    radius: 0.2,
    color: 0x8A2BE2, // Purple
    description: "Cerebellum - motor coordination, balance"
  },
  brainstem: {
    center: [-0.02, -0.6, 0.3],
    radius: 0.15,
    color: 0xFF69B4, // Pink
    description: "Brainstem - autonomic functions, reflexes"
  }
};

/**
 * Create region meshes for visualization
 */
export function createRegionMeshes() {
  const meshes = {};
  
  for (const [regionName, region] of Object.entries(brainRegions)) {
    const geometry = new THREE.SphereGeometry(region.radius * 0.5, 16, 16);
    const material = new THREE.MeshBasicMaterial({
      color: region.color,
      transparent: true,
      opacity: 0.3,
      wireframe: true
    });
    
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(...region.center);
    mesh.userData = { region: regionName, ...region };
    
    meshes[regionName] = mesh;
  }
  
  return meshes;
}

/**
 * Create a complete brain scene with regions highlighted
 */
export function createBrainScene(options = {}) {
  const scene = new THREE.Scene();
  
  // Create brain geometry
  const brainGeometry = createBrainGeometry(options);
  const brainMaterial = new THREE.MeshPhongMaterial({
    color: 0x6666FF,
    shininess: 30,
    transparent: true,
    opacity: 0.7,
    side: THREE.DoubleSide
  });
  
  const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial);
  scene.add(brainMesh);
  
  // Add region markers
  const regionMeshes = createRegionMeshes();
  Object.values(regionMeshes).forEach(mesh => scene.add(mesh));
  
  // Add coordinate system helper
  const axesHelper = new THREE.AxesHelper(1);
  scene.add(axesHelper);
  
  return {
    scene,
    brainMesh,
    regionMeshes,
    brainGeometry
  };
}

/**
 * Utility function to get region at a specific position
 */
export function getRegionAtPosition(position, threshold = 0.5) {
  const { x, y, z } = position;
  let closestRegion = null;
  let minDistance = Infinity;
  
  for (const [regionName, region] of Object.entries(brainRegions)) {
    const [rx, ry, rz] = region.center;
    const distance = Math.sqrt(
      (x - rx) ** 2 + (y - ry) ** 2 + (z - rz) ** 2
    );
    
    if (distance < region.radius * threshold && distance < minDistance) {
      minDistance = distance;
      closestRegion = regionName;
    }
  }
  
  return closestRegion;
}

// Export THREE for convenience if not already defined
if (typeof THREE === 'undefined') {
  console.warn('THREE is not defined. Make sure to include Three.js before using brain-geometry.js');
}

export default {
  createBrainGeometry,
  createBrainScene,
  createRegionMeshes,
  brainRegions,
  getRegionAtPosition
};