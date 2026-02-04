/**
 * CONNECTION ANIMATIONS
 * Pulse effects along neural pathways/connections
 * 
 * Dependencies: anime.js, Three.js
 */

const ConnectionAnimations = {
    /**
     * Simple pulse along connection line
     * Opacity fade in/out with position tracking
     * 
     * @param {Object} connection - Connection object with line, start, end
     * @param {number} duration - Pulse duration (default: 1500ms)
     */
    simplePulse(connection, duration = 1500) {
        const material = connection.line.material;
        
        // Opacity pulse
        anime({
            targets: material,
            opacity: [0, 0.6, 0],
            duration: duration,
            easing: 'easeInOutQuad'
        });
        
        // Track pulse progress for particle effects
        anime({
            targets: connection,
            pulseProgress: [0, 1],
            duration: duration,
            easing: 'easeInOutCubic'
        });
    },
    
    /**
     * Bidirectional pulse (both directions simultaneously)
     * For mutual activation or feedback loops
     * 
     * @param {Object} connection - Connection object
     * @param {number} duration - Pulse duration
     */
    bidirectionalPulse(connection, duration = 1200) {
        const material = connection.line.material;
        
        anime({
            targets: material,
            opacity: [0, 0.8, 0],
            duration: duration,
            easing: 'easeInOutQuad'
        });
        
        // Two pulses traveling in opposite directions
        anime({
            targets: connection,
            pulseProgress1: [0, 1],
            pulseProgress2: [1, 0],
            duration: duration,
            easing: 'linear'
        });
    },
    
    /**
     * Strengthening connection animation
     * Line becomes thicker and brighter (for learning/memory)
     * 
     * @param {Object} connection - Connection object
     * @param {number} newStrength - Target strength (0.0 - 1.0)
     * @param {number} duration - Transition duration
     */
    strengthen(connection, newStrength = 0.8, duration = 2000) {
        const material = connection.line.material;
        
        // Increase opacity permanently
        anime({
            targets: material,
            opacity: newStrength * 0.6,
            duration: duration,
            easing: 'easeInOutQuad'
        });
        
        // Flash to indicate change
        anime({
            targets: connection,
            flashIntensity: [0, 1, 0],
            duration: 800,
            easing: 'easeOutQuad'
        });
    },
    
    /**
     * Weakening connection animation
     * Line fades and dims (for forgetting)
     * 
     * @param {Object} connection - Connection object
     * @param {number} newStrength - Target strength (0.0 - 1.0)
     * @param {number} duration - Transition duration
     */
    weaken(connection, newStrength = 0.2, duration = 2000) {
        const material = connection.line.material;
        
        anime({
            targets: material,
            opacity: newStrength * 0.6,
            duration: duration,
            easing: 'easeInOutQuad'
        });
    },
    
    /**
     * Cascade pulse through network
     * Multiple connections pulse in sequence
     * 
     * @param {Array} connections - Array of connection objects
     * @param {number} staggerDelay - Delay between each pulse (ms)
     */
    cascade(connections, staggerDelay = 100) {
        const timeline = anime.timeline({
            easing: 'easeInOutQuad'
        });
        
        connections.forEach((connection, index) => {
            timeline.add({
                targets: connection.line.material,
                opacity: [0, 0.7, 0],
                duration: 1200,
                offset: index * staggerDelay
            });
        });
    },
    
    /**
     * High-priority urgent pulse
     * Fast, bright, attention-grabbing
     * 
     * @param {Object} connection - Connection object
     */
    urgent(connection) {
        const material = connection.line.material;
        
        // Rapid triple pulse
        const timeline = anime.timeline({});
        
        for (let i = 0; i < 3; i++) {
            timeline.add({
                targets: material,
                opacity: [0, 0.9, 0],
                duration: 400,
                easing: 'easeInOutQuad',
                offset: i * 500
            });
        }
    },
    
    /**
     * Information flow visualization
     * Particle/glow travels along connection path
     * 
     * @param {Object} connection - Connection object
     * @param {THREE.Color} color - Particle color
     * @param {number} duration - Travel time
     */
    flowParticle(connection, color = 0xffff00, duration = 1000) {
        const material = connection.line.material;
        
        // Line brightens as particle passes
        anime({
            targets: material,
            opacity: [0.2, 0.6, 0.2],
            duration: duration,
            easing: 'linear'
        });
        
        // Track particle position for rendering
        anime({
            targets: connection,
            particleProgress: [0, 1],
            particleOpacity: [0, 1, 0],
            duration: duration,
            easing: 'easeInOutQuad'
        });
    },
    
    /**
     * Synaptic firing animation
     * Mimics actual neuron spike behavior
     * 
     * @param {Object} connection - Connection object
     */
    synapticFire(connection) {
        const material = connection.line.material;
        
        // Fast spike
        anime({
            targets: material,
            opacity: [0, 1],
            duration: 50,
            easing: 'easeOutQuad',
            complete: () => {
                // Slower decay
                anime({
                    targets: material,
                    opacity: [1, 0],
                    duration: 400,
                    easing: 'easeInQuad'
                });
            }
        });
        
        // Refractory period prevents immediate re-fire
        connection.refractoryUntil = Date.now() + 500;
    },
    
    /**
     * Network-wide activation wave
     * All connections pulse in coordinated pattern
     * 
     * @param {Array} connections - All connection objects
     * @param {Object} epicenter - THREE.Vector3 starting point
     */
    networkWave(connections, epicenter) {
        const timeline = anime.timeline({
            easing: 'easeOutQuad'
        });
        
        // Sort by distance from epicenter
        const sorted = connections.map(conn => {
            const midpoint = new THREE.Vector3()
                .addVectors(conn.start, conn.end)
                .multiplyScalar(0.5);
            const dist = midpoint.distanceTo(epicenter);
            return { conn, dist };
        }).sort((a, b) => a.dist - b.dist);
        
        // Stagger based on distance
        sorted.forEach(({ conn, dist }) => {
            timeline.add({
                targets: conn.line.material,
                opacity: [0, 0.6, 0],
                duration: 800,
                offset: dist * 200
            });
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectionAnimations;
}
