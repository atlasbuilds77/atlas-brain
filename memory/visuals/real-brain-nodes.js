/**
 * Real Node Mapping System for Atlas Brain
 * Maps actual memory files to brain nodes with spatial positioning
 */

// Color mapping for node types
const COLOR_MAP = {
  cyan: 0x00ffff,     // Protocols
  blue: 0x0077ff,     // Trading
  yellow: 0xffff00,   // People
  purple: 0xaa00ff,   // Tools
  orange: 0xff8800,   // Cognitive systems - pattern
  red: 0xff4444,      // Cognitive systems - emotion
  green: 0x44ff44,    // Cognitive systems - meta
  pink: 0xff66cc      // Cognitive systems - bias
};

// Spatial positioning configuration
const POSITION_CONFIG = {
  // Front left hemisphere - Protocols (cyan)
  protocols: {
    center: { x: -2.5, y: 1.5, z: 1.5 },
    radius: 2.0,
    spread: 0.8
  },
  // Front right hemisphere - Trading (blue)
  trading: {
    center: { x: 2.5, y: 1.5, z: 1.5 },
    radius: 2.0,
    spread: 0.8
  },
  // Temporal lobes - People (yellow)
  people: {
    center: { x: 0, y: 0, z: -1.5 },
    radius: 1.5,
    spread: 0.6
  },
  // Motor cortex area - Tools (purple)
  tools: {
    center: { x: 0, y: -1.5, z: 0.5 },
    radius: 1.2,
    spread: 0.5
  },
  // Distributed cognitive systems
  cognitive: {
    pattern: { center: { x: -1.5, y: 2.0, z: 0 }, radius: 0.8 },
    emotion: { center: { x: 1.5, y: 2.0, z: 0 }, radius: 0.8 },
    meta: { center: { x: 0, y: 2.5, z: 0 }, radius: 0.8 },
    bias: { center: { x: 0, y: 1.8, z: 1.2 }, radius: 0.8 }
  }
};

// Node state tracking
let currentNodes = new Map(); // Map of file paths to node data
let animationState = new Map(); // Map of node IDs to animation state

/**
 * Load real nodes from the JSON file
 * @returns {Promise<Array>} Array of positioned node objects
 */
export async function loadRealNodes() {
  try {
    // Try to fetch the JSON file
    const response = await fetch('/tmp/real-brain-nodes.json');
    if (!response.ok) {
      console.warn('Could not load real-brain-nodes.json, using fallback');
      return generateFallbackNodes();
    }
    
    const data = await response.json();
    return processNodeData(data);
  } catch (error) {
    console.error('Error loading real nodes:', error);
    return generateFallbackNodes();
  }
}

/**
 * Process raw node data into positioned nodes
 * @param {Object} data - Raw node data from JSON
 * @returns {Array} Positioned nodes
 */
function processNodeData(data) {
  const nodes = [];
  currentNodes.clear();
  
  // Process memory nodes
  if (data.memoryNodes) {
    // Protocols (cyan) - front left hemisphere
    if (data.memoryNodes.protocols) {
      const config = POSITION_CONFIG.protocols;
      data.memoryNodes.protocols.forEach((node, index) => {
        const positionedNode = createPositionedNode(node, 'protocols', index, data.memoryNodes.protocols.length, config);
        nodes.push(positionedNode);
        currentNodes.set(node.file, positionedNode);
      });
    }
    
    // Trading (blue) - front right hemisphere
    if (data.memoryNodes.trading) {
      const config = POSITION_CONFIG.trading;
      data.memoryNodes.trading.forEach((node, index) => {
        const positionedNode = createPositionedNode(node, 'trading', index, data.memoryNodes.trading.length, config);
        nodes.push(positionedNode);
        currentNodes.set(node.file, positionedNode);
      });
    }
    
    // People (yellow) - temporal lobes
    if (data.memoryNodes.people) {
      const config = POSITION_CONFIG.people;
      data.memoryNodes.people.forEach((node, index) => {
        const positionedNode = createPositionedNode(node, 'people', index, data.memoryNodes.people.length, config);
        nodes.push(positionedNode);
        currentNodes.set(node.file, positionedNode);
      });
    }
  }
  
  // Tools (purple) - motor cortex area
  if (data.tools) {
    const config = POSITION_CONFIG.tools;
    data.tools.forEach((tool, index) => {
      const node = {
        name: tool.name,
        type: 'tool',
        color: tool.color,
        region: tool.region
      };
      const positionedNode = createPositionedNode(node, 'tools', index, data.tools.length, config);
      nodes.push(positionedNode);
      currentNodes.set(`tool:${tool.name}`, positionedNode);
    });
  }
  
  // Cognitive systems - distributed
  if (data.cognitiveSystem) {
    data.cognitiveSystem.forEach((system, index) => {
      const config = POSITION_CONFIG.cognitive[system.region] || POSITION_CONFIG.cognitive.pattern;
      const node = {
        name: system.name,
        type: 'cognitive',
        color: system.color,
        region: system.region
      };
      const positionedNode = createPositionedNode(node, 'cognitive', index, data.cognitiveSystem.length, config);
      nodes.push(positionedNode);
      currentNodes.set(`cognitive:${system.name}`, positionedNode);
    });
  }
  
  return nodes;
}

/**
 * Create a positioned node with spherical distribution
 * @param {Object} node - Raw node data
 * @param {string} category - Node category
 * @param {number} index - Node index within category
 * @param {number} total - Total nodes in category
 * @param {Object} config - Position configuration
 * @returns {Object} Positioned node
 */
function createPositionedNode(node, category, index, total, config) {
  // Calculate position on a sphere
  const phi = Math.acos(-1 + (2 * index) / total);
  const theta = Math.sqrt(total * Math.PI) * phi;
  
  const radius = config.radius || 1.0;
  const x = config.center.x + radius * Math.sin(phi) * Math.cos(theta) * (config.spread || 1.0);
  const y = config.center.y + radius * Math.sin(phi) * Math.sin(theta) * (config.spread || 1.0);
  const z = config.center.z + radius * Math.cos(phi) * (config.spread || 1.0);
  
  // Add some random variation
  const variation = 0.3;
  const finalX = x + (Math.random() - 0.5) * variation;
  const finalY = y + (Math.random() - 0.5) * variation;
  const finalZ = z + (Math.random() - 0.5) * variation;
  
  // Generate unique ID
  const id = `${category}-${node.name}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  
  return {
    id,
    name: node.name,
    type: category,
    color: COLOR_MAP[node.color] || 0xffffff,
    position: { x: finalX, y: finalY, z: finalZ },
    scale: 0.1, // Start small for animation
    opacity: 0, // Start invisible for fade-in
    animation: {
      birthTime: Date.now(),
      scalePulse: 0,
      fadeProgress: 0
    },
    metadata: {
      file: node.file,
      region: node.region,
      colorName: node.color
    }
  };
}

/**
 * Generate fallback nodes if JSON file is not available
 * @returns {Array} Fallback nodes
 */
function generateFallbackNodes() {
  console.log('Generating fallback nodes');
  const nodes = [];
  
  // Generate some example nodes for each category
  const categories = [
    { type: 'protocols', count: 10, color: 'cyan' },
    { type: 'trading', count: 15, color: 'blue' },
    { type: 'people', count: 5, color: 'yellow' },
    { type: 'tools', count: 6, color: 'purple' },
    { type: 'cognitive', count: 5, color: 'orange' }
  ];
  
  categories.forEach(category => {
    const config = POSITION_CONFIG[category.type] || POSITION_CONFIG.cognitive.pattern;
    for (let i = 0; i < category.count; i++) {
      const node = {
        name: `${category.type}-node-${i + 1}`,
        type: category.type,
        color: category.color
      };
      const positionedNode = createPositionedNode(node, category.type, i, category.count, config);
      nodes.push(positionedNode);
      currentNodes.set(`${category.type}-${i}`, positionedNode);
    }
  });
  
  return nodes;
}

/**
 * Watch for new nodes by polling the JSON file
 * @param {Function} callback - Callback function when new nodes are detected
 * @param {number} intervalMs - Polling interval in milliseconds (default: 10000)
 */
export function watchForNewNodes(callback, intervalMs = 10000) {
  let lastScanTime = Date.now();
  let scanInterval;
  
  async function scanForNewNodes() {
    try {
      const response = await fetch('/tmp/real-brain-nodes.json');
      if (!response.ok) return;
      
      const data = await response.json();
      const newNodes = [];
      
      // Check for new memory files
      const allMemoryFiles = [];
      if (data.memoryNodes) {
        Object.values(data.memoryNodes).forEach(category => {
          category.forEach(node => {
            if (node.file && !currentNodes.has(node.file)) {
              newNodes.push(node);
              allMemoryFiles.push(node.file);
            }
          });
        });
      }
      
      // Check for new tools
      if (data.tools) {
        data.tools.forEach(tool => {
          const key = `tool:${tool.name}`;
          if (!currentNodes.has(key)) {
            newNodes.push({ ...tool, type: 'tool' });
            allMemoryFiles.push(key);
          }
        });
      }
      
      // Check for new cognitive systems
      if (data.cognitiveSystem) {
        data.cognitiveSystem.forEach(system => {
          const key = `cognitive:${system.name}`;
          if (!currentNodes.has(key)) {
            newNodes.push({ ...system, type: 'cognitive' });
            allMemoryFiles.push(key);
          }
        });
      }
      
      // Process new nodes if any found
      if (newNodes.length > 0) {
        console.log(`Found ${newNodes.length} new nodes`);
        
        // Group new nodes by type for positioning
        const groupedNodes = {};
        newNodes.forEach(node => {
          const type = node.type || 'protocols';
          if (!groupedNodes[type]) groupedNodes[type] = [];
          groupedNodes[type].push(node);
        });
        
        // Create positioned nodes for each group
        const positionedNewNodes = [];
        Object.entries(groupedNodes).forEach(([type, typeNodes]) => {
          const config = POSITION_CONFIG[type] || POSITION_CONFIG.cognitive.pattern;
          typeNodes.forEach((node, index) => {
            const positionedNode = createPositionedNode(
              node,
              type,
              index + (currentNodes.size % 100), // Add offset for positioning
              typeNodes.length + 5, // Add buffer for spacing
              config
            );
            positionedNewNodes.push(positionedNode);
            currentNodes.set(node.file || `${type}:${node.name}`, positionedNode);
          });
        });
        
        // Call callback with new nodes
        if (callback && positionedNewNodes.length > 0) {
          callback(positionedNewNodes);
        }
      }
      
      lastScanTime = Date.now();
    } catch (error) {
      console.error('Error scanning for new nodes:', error);
    }
  }
  
  // Start polling
  scanInterval = setInterval(scanForNewNodes, intervalMs);
  
  // Return function to stop watching
  return () => {
    if (scanInterval) {
      clearInterval(scanInterval);
      scanInterval = null;
    }
  };
}

/**
 * Update node animations
 * @param {Array} nodes - Array of nodes to animate
 * @param {number} deltaTime - Time since last update in seconds
 */
export function updateNodeAnimations(nodes, deltaTime) {
  const now = Date.now();
  
  nodes.forEach(node => {
    if (!node.animation) return;
    
    const age = now - node.animation.birthTime;
    
    // Fade in animation (first 2 seconds)
    if (age < 2000) {
      node.opacity = age / 2000;
      node.animation.fadeProgress = node.opacity;
    } else {
      node.opacity = 1;
      node.animation.fadeProgress = 1;
    }
    
    // Scale pulse animation
    const pulseSpeed = 2; // pulses per second
    node.animation.scalePulse = Math.sin(now * 0.001 * Math.PI * 2 * pulseSpeed) * 0.05;
    
    // Apply scale with pulse
    node.scale = 0.1 + (node.opacity * 0.1) + node.animation.scalePulse;
    
    // Gentle floating animation
    const floatSpeed = 0.5;
    const floatAmount = 0.05;
    node.position.y += Math.sin(now * 0.001 * floatSpeed + node.id.length) * floatAmount * deltaTime;
  });
}

/**
 * Get current node count by type
 * @returns {Object} Counts by node type
 */
export function getNodeCounts() {
  const counts = {
    protocols: 0,
    trading: 0,
    people: 0,
    tools: 0,
    cognitive: 0,
    total: currentNodes.size
  };
  
  currentNodes.forEach(node => {
    if (counts[node.type] !== undefined) {
      counts[node.type]++;
    }
  });
  
  return counts;
}

/**
 * Find node by name or file path
 * @param {string} query - Search query
 * @returns {Array} Matching nodes
 */
export function findNodes(query) {
  const results = [];
  const lowerQuery = query.toLowerCase();
  
  currentNodes.forEach(node => {
    if (
      node.name.toLowerCase().includes(lowerQuery) ||
      (node.metadata?.file && node.metadata.file.toLowerCase().includes(lowerQuery))
    ) {
      results.push(node);
    }
  });
  
  return results;
}