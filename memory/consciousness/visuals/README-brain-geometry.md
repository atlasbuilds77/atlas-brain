# Brain Geometry for Three.js

This module provides anatomical brain shape geometry for Three.js visualizations, featuring realistic brain topology with hemispheres, cortical folds, and major brain regions.

## Files

1. **`brain-geometry.js`** - Main module with comprehensive brain geometry generation
2. **`brain-geometry-simple.js`** - Simplified version for easy integration
3. **`brain-demo.html`** - Interactive demo with controls
4. **`test-brain-geometry.html`** - Basic test page

## Features

### 1. Anatomical Accuracy
- Left and right hemisphere separation
- Realistic cortical folds (sulci and gyri)
- Major brain regions: frontal, parietal, temporal, occipital lobes
- Natural asymmetry between hemispheres
- Cerebellum and brainstem representation

### 2. Technical Implementation
- Parametric equations for brain surface generation
- Customizable detail level (16-64 subdivisions)
- Optimized vertex count (5000-10000 vertices)
- Pre-calculated surface normals for smooth shading
- Three.js BufferGeometry compatible

### 3. Interactive Features
- Region detection on mouse hover
- Wireframe and transparency toggles
- Detail level adjustment
- Rotation and zoom controls
- Region highlighting with descriptions

## Usage

### Basic Integration

```javascript
// Import the module (ES6)
import { createBrainGeometry, brainRegions } from './brain-geometry.js';

// Or use the simple version (global)
<script src="./brain-geometry-simple.js"></script>
<script>
  const brainScene = BrainGeometry.createSimpleBrainScene(32);
  scene.add(brainScene.scene);
</script>
```

### Creating Brain Geometry

```javascript
// Create brain geometry with options
const geometry = createBrainGeometry({
  detail: 32,          // Mesh resolution
  scale: 1.0,          // Overall scale
  hemisphereSplit: 0.1, // Gap between hemispheres
  foldDepth: 0.15,     // Depth of cortical folds
  asymmetry: 0.05      // Natural asymmetry
});

// Create material
const material = new THREE.MeshPhongMaterial({
  color: 0x6666FF,
  shininess: 30,
  transparent: true,
  opacity: 0.7
});

// Create mesh
const brainMesh = new THREE.Mesh(geometry, material);
scene.add(brainMesh);
```

### Brain Regions Data

```javascript
// Access region information
const regions = brainRegions; // or brainRegionsSimple

// Example region structure
{
  frontal: {
    center: [-0.3, 0.1, 0.8],  // 3D coordinates
    radius: 0.4,               // Approximate size
    color: 0x4285F4,           // Blue
    description: "Frontal lobe - executive functions, decision making"
  },
  // ... other regions
}

// Create region markers
const regionMeshes = createRegionMeshes();
Object.values(regionMeshes).forEach(mesh => scene.add(mesh));
```

## API Reference

### Main Functions

#### `createBrainGeometry(options)`
Creates a Three.js BufferGeometry for the brain.

**Options:**
- `detail` (number): Mesh resolution (default: 32)
- `scale` (number): Overall scale (default: 1.0)
- `hemisphereSplit` (number): Gap between hemispheres (default: 0.1)
- `foldDepth` (number): Depth of cortical folds (default: 0.15)
- `asymmetry` (number): Natural asymmetry (default: 0.05)

#### `createBrainScene(options)`
Creates a complete Three.js scene with brain and region markers.

#### `createRegionMeshes()`
Creates sphere meshes for each brain region.

#### `getRegionAtPosition(position, threshold)`
Returns the brain region at a given 3D position.

### Simple Version (Global)

#### `BrainGeometry.createSimpleBrainGeometry(detail)`
Simplified brain geometry creation.

#### `BrainGeometry.createSimpleBrainScene(detail)`
Creates a simple brain scene.

#### `BrainGeometry.brainRegionsSimple`
Simplified region data.

## Parametric Equations

The brain shape is generated using modified spherical harmonics:

```javascript
// Base equation
radius(u, v) = base_radius + lobe_perturbations + fold_pattern

// Cartesian coordinates
x = radius * sin(u) * cos(v) + hemisphere_offset
y = radius * sin(u) * sin(v)
z = radius * cos(u)

// Where:
// u ∈ [0, π] (latitude)
// v ∈ [0, 2π] (longitude)
```

### Lobe-specific Shaping

Each brain region has custom perturbations:
- **Frontal lobe**: Anterior bulge for forehead shape
- **Parietal lobe**: Superior expansion
- **Temporal lobe**: Lateral extensions
- **Occipital lobe**: Posterior protrusion

### Cortical Folds

Multiple frequency sine waves create realistic sulci and gyri:
```javascript
fold_pattern = Σ amplitude * sin(frequency_u * u) * cos(frequency_v * v)
```

## Performance

- **Low detail (16)**: ~2,000 vertices, ~4,000 faces
- **Medium detail (32)**: ~8,000 vertices, ~16,000 faces  
- **High detail (64)**: ~32,000 vertices, ~64,000 faces

Recommended: Use detail level 32 for optimal balance of quality and performance.

## Demo Features

The `brain-demo.html` includes:

1. **Interactive Controls**
   - Rotate, zoom, and pan
   - Toggle wireframe view
   - Adjust transparency
   - Change detail level
   - Toggle region markers

2. **Region Detection**
   - Mouse hover shows region information
   - Color-coded region highlighting
   - Anatomical descriptions

3. **Visual Effects**
   - Smooth rotation animation
   - Subtle pulsing effect
   - Realistic lighting
   - Shadow support

## Integration with Existing Projects

### As a Standalone Visualization

```html
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="./brain-geometry-simple.js"></script>
</head>
<body>
    <script>
        // Quick setup
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer();
        
        const brain = BrainGeometry.createSimpleBrainScene(32);
        scene.add(brain.scene);
        
        // ... render loop
    </script>
</body>
</html>
```

### As a Module in Larger Application

```javascript
// ES6 module
import { createBrainGeometry, brainRegions } from './brain-geometry.js';

class BrainVisualizer {
  constructor(scene, options) {
    this.geometry = createBrainGeometry(options);
    this.material = new THREE.MeshPhongMaterial({/* ... */});
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    scene.add(this.mesh);
    
    this.setupRegions(scene);
  }
  
  setupRegions(scene) {
    for (const [name, region] of Object.entries(brainRegions)) {
      // Create interactive region markers
    }
  }
}
```

## Customization

### Changing Colors

```javascript
// Brain material
brainMesh.material.color.setHex(0xYourColor);

// Region colors
const customRegions = {
  ...brainRegions,
  frontal: { ...brainRegions.frontal, color: 0xYourColor }
};
```

### Adding Custom Regions

```javascript
const extendedRegions = {
  ...brainRegions,
  hippocampus: {
    center: [-0.4, -0.2, 0.3],
    radius: 0.15,
    color: 0xFF69B4,
    description: "Hippocampus - memory formation"
  }
};
```

### Adjusting Shape Parameters

```javascript
// More pronounced folds
const geometry = createBrainGeometry({
  foldDepth: 0.25,
  asymmetry: 0.1
});

// More separated hemispheres  
const geometry = createBrainGeometry({
  hemisphereSplit: 0.2
});
```

## References

### Brain Anatomy
- Frontal lobe: Executive functions, decision making
- Parietal lobe: Sensory integration, spatial awareness  
- Temporal lobe: Auditory processing, memory
- Occipital lobe: Visual processing
- Cerebellum: Motor coordination, balance
- Brainstem: Autonomic functions

### Technical References
- Three.js Documentation: https://threejs.org/docs/
- Parametric Surfaces: Mathematical modeling of complex shapes
- Spherical Harmonics: Basis for organic shape generation
- Computational Neuroanatomy: Brain surface modeling techniques

## License

This code is provided for educational and visualization purposes. Modify and use as needed for your projects.

## Future Enhancements

Potential improvements:
1. **MRI Data Integration**: Load real brain scan data
2. **Neural Pathways**: Add white matter tract visualization
3. **Interactive Labels**: Clickable region annotations
4. **Animation**: Blood flow or neural activity simulations
5. **VR/AR Support**: Immersive brain exploration
6. **Export Options**: OBJ, GLTF, STL formats
7. **Educational Content**: Integrated learning modules

## Support

For issues or questions:
1. Check the demo examples first
2. Review the parametric equations section
3. Adjust detail level for performance issues
4. Modify region coordinates for your specific use case