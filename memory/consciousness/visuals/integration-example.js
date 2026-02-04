/**
 * Integration Example for Real Brain Nodes
 * Shows how to integrate the real-node mapping system into an existing Three.js scene
 */

import * as THREE from 'three';
import { loadRealNodes, watchForNewNodes, updateNodeAnimations, getNodeCounts, findNodes } from './real-brain-nodes.js';

/**
 * Example integration class
 */
export class RealBrainNodesIntegration {
  constructor(scene, options = {}) {
    this.scene = scene;
    this.options = {
      nodeScale: 0.2,
      glowEnabled: true,
      autoUpdate: true,
      ...options
    };
    
    this.nodes = [];
    this.nodeMeshes = new Map();
    this.stopWatching = null;
    
    // Materials cache by color
    this.materialCache = new Map();
  }
  
  /**
   * Initialize the integration
   */
  async init() {
    // Load initial nodes
    await this.loadNodes();
    
    // Start watching for new nodes
    if (this.options.autoUpdate) {
      this.startWatching();
    }
    
    return this;
  }
  
  /**
   * Load nodes from the JSON file
   */
  async loadNodes() {
    this.nodes = await loadRealNodes();
    this.createNodeMeshes();
    return this.nodes;
  }
  
  /**
   * Create Three.js meshes for all nodes
   */
  createNodeMeshes() {
    // Clear existing meshes
    this.nodeMeshes.forEach(mesh => this.scene.remove(mesh));
    this.nodeMeshes.clear();
    
    // Create meshes for each node
    this.nodes.forEach(node => {
      const mesh = this.createNodeMesh(node);
      this.scene.add(mesh);
      this.nodeMeshes.set(node.id, mesh);
    });
  }
  
  /**
   * Create a single node mesh
   */
  createNodeMesh(node) {
    // Get or create material for this color
    let material = this.materialCache.get(node.color);
    if (!material) {
      material = new THREE.MeshPhongMaterial({
        color: node.color,
        transparent: true,
        opacity: node.opacity || 1,
        emissive: node.color,
        emissiveIntensity: 0.2
      });
      this.materialCache.set(node.color, material);
    }
    
    const geometry = new THREE.SphereGeometry(1, 16, 16);
    const mesh = new THREE.Mesh(geometry, material);
    
    // Set initial properties
    mesh.scale.setScalar((node.scale || 0.1) * this.options.nodeScale);
    mesh.position.set(node.position.x, node.position.y, node.position.z);
    
    // Add glow effect if enabled
    if (this.options.glowEnabled) {
      const glowGeometry = new THREE.SphereGeometry(1.2, 16, 16);
      const glowMaterial = new THREE.MeshBasicMaterial({
        color: node.color,
        transparent: true,
        opacity: 0.3,
        side: THREE.BackSide
      });
      const glow = new THREE.Mesh(glowGeometry, glowMaterial);
      glow.scale.setScalar(1);
      mesh.add(glow);
      mesh.userData.glow = glow;
    }
    
    // Store node data
    mesh.userData.nodeId = node.id;
    mesh.userData.node = node;
    
    return mesh;
  }
  
  /**
   * Start watching for new nodes
   */
  startWatching() {
    if (this.stopWatching) {
      this.stopWatching();
    }
    
    this.stopWatching = watchForNewNodes((newNodes) => {
      this.handleNewNodes(newNodes);
    }, 10000);
  }
  
  /**
   * Handle new nodes detected
   */
  handleNewNodes(newNodes) {
    console.log(`RealBrainNodes: Adding ${newNodes.length} new nodes`);
    
    newNodes.forEach(node => {
      if (!this.nodeMeshes.has(node.id)) {
        const mesh = this.createNodeMesh(node);
        this.scene.add(mesh);
        this.nodeMeshes.set(node.id, mesh);
        this.nodes.push(node);
      }
    });
  }
  
  /**
   * Update node animations
   * @param {number} deltaTime - Time since last update in seconds
   */
  update(deltaTime) {
    // Update node animations
    updateNodeAnimations(this.nodes, deltaTime);
    
    // Update meshes
    this.nodes.forEach(node => {
      const mesh = this.nodeMeshes.get(node.id);
      if (mesh) {
        // Update scale with animation
        mesh.scale.setScalar(node.scale * this.options.nodeScale);
        
        // Update opacity
        if (mesh.material) {
          mesh.material.opacity = node.opacity;
        }
        
        // Update glow opacity if present
        if (mesh.userData.glow) {
          mesh.userData.glow.material.opacity = node.opacity * 0.3;
        }
        
        // Gentle rotation
        mesh.rotation.y += 0.01 * deltaTime;
      }
    });
  }
  
  /**
   * Get node by ID
   */
  getNodeById(nodeId) {
    return this.nodes.find(node => node.id === nodeId);
  }
  
  /**
   * Get mesh by node ID
   */
  getMeshById(nodeId) {
    return this.nodeMeshes.get(nodeId);
  }
  
  /**
   * Find nodes by search query
   */
  findNodes(query) {
    return findNodes(query);
  }
  
  /**
   * Get current node counts
   */
  getCounts() {
    return getNodeCounts();
  }
  
  /**
   * Highlight a specific node
   */
  highlightNode(nodeId, highlight = true) {
    const mesh = this.nodeMeshes.get(nodeId);
    if (mesh) {
      if (highlight) {
        mesh.material.emissiveIntensity = 0.8;
        mesh.scale.multiplyScalar(1.5);
      } else {
        mesh.material.emissiveIntensity = 0.2;
        mesh.scale.multiplyScalar(1/1.5);
      }
    }
  }
  
  /**
   * Clean up resources
   */
  dispose() {
    if (this.stopWatching) {
      this.stopWatching();
      this.stopWatching = null;
    }
    
    // Remove meshes from scene
    this.nodeMeshes.forEach(mesh => {
      this.scene.remove(mesh);
      
      // Dispose geometries and materials
      if (mesh.geometry) mesh.geometry.dispose();
      if (mesh.material) mesh.material.dispose();
      
      if (mesh.userData.glow) {
        mesh.userData.glow.geometry.dispose();
        mesh.userData.glow.material.dispose();
      }
    });
    
    this.nodeMeshes.clear();
    this.nodes = [];
    
    // Clear material cache
    this.materialCache.forEach(material => material.dispose());
    this.materialCache.clear();
  }
}

/**
 * Quick integration helper
 */
export function integrateRealNodes(scene, options = {}) {
  const integration = new RealBrainNodesIntegration(scene, options);
  return integration.init();
}

// Export the core functions for direct use
export { loadRealNodes, watchForNewNodes, updateNodeAnimations, getNodeCounts, findNodes };