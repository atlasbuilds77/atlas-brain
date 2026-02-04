/**
 * COGNITIVE PULSE ANIMATIONS
 * Professional-grade elastic/spring animations for brain region events
 * 
 * Dependencies: anime.js, Three.js
 */

const CognitivePulses = {
    /**
     * Elastic pulse for cognitive event activation
     * Creates a bouncy, organic feel that signals neural activity
     * 
     * @param {Object} region - Region object containing mesh, material, glow
     * @param {number} intensity - Pulse strength (0.0 - 1.0)
     * @param {number} duration - Animation duration in ms (default: 1200)
     */
    elasticPulse(region, intensity = 0.7, duration = 1200) {
        const targetScale = 1 + intensity * 0.5;
        
        // Scale animation with elastic easing
        anime({
            targets: region.mesh.scale,
            x: [1, targetScale, 1],
            y: [1, targetScale, 1],
            z: [1, targetScale, 1],
            duration: duration,
            easing: 'easeOutElastic(1, .6)'
        });
        
        // Emissive intensity pulse
        anime({
            targets: region.mesh.material,
            emissiveIntensity: [0.3, 0.9, 0.3],
            duration: duration,
            easing: 'easeOutQuad'
        });
        
        // Glow pulse
        anime({
            targets: region.glow.material,
            opacity: [0.2, 0.6, 0.2],
            duration: duration,
            easing: 'easeOutQuad'
        });
    },
    
    /**
     * Spring-based brain pulse
     * Uses realistic spring physics for natural deceleration
     * 
     * @param {Object} brain - Three.js brain mesh
     * @param {Object} material - Brain material for emissive control
     * @param {number} intensity - Pulse strength (0.0 - 1.0)
     */
    springBrainPulse(brain, material, intensity = 0.5) {
        const scale = 1 + intensity * 0.15;
        
        // Spring physics scale
        anime({
            targets: brain.scale,
            x: [1, scale, 1],
            y: [1, scale, 1],
            z: [1, scale, 1],
            duration: 800,
            easing: 'spring(1, 80, 10, 0)'
        });
        
        // Emissive sync
        anime({
            targets: material,
            emissiveIntensity: [0.5, 0.5 + intensity * 0.4, 0.5],
            duration: 800,
            easing: 'easeOutQuad'
        });
    },
    
    /**
     * Ripple effect from center outward
     * Multiple concentric pulses for dramatic events
     * 
     * @param {Array} regions - Array of region objects to pulse
     * @param {Object} centerPos - THREE.Vector3 center position
     * @param {number} speed - Wave propagation speed (default: 0.3)
     */
    ripplePulse(regions, centerPos, speed = 0.3) {
        const timeline = anime.timeline({
            easing: 'easeOutQuad'
        });
        
        // Calculate distances and sort
        const sortedRegions = regions.map(region => {
            const dist = region.mesh.position.distanceTo(centerPos);
            return { region, dist };
        }).sort((a, b) => a.dist - b.dist);
        
        // Stagger pulses based on distance
        sortedRegions.forEach(({ region, dist }) => {
            timeline.add({
                targets: region.mesh.scale,
                x: [1, 1.3, 1],
                y: [1, 1.3, 1],
                z: [1, 1.3, 1],
                duration: 600,
                offset: dist * speed * 1000
            });
        });
    },
    
    /**
     * Sustained activation glow
     * For regions that stay active (processing, working memory)
     * 
     * @param {Object} region - Region to activate
     * @param {number} duration - How long to sustain (default: 3000ms)
     */
    sustainedGlow(region, duration = 3000) {
        // Ramp up
        anime({
            targets: region.mesh.material,
            emissiveIntensity: [0.3, 0.8],
            duration: 400,
            easing: 'easeOutQuad'
        });
        
        anime({
            targets: region.glow.material,
            opacity: [0.2, 0.5],
            duration: 400,
            easing: 'easeOutQuad'
        });
        
        // Gentle pulse during sustain
        anime({
            targets: region.mesh.scale,
            x: [1, 1.1, 1],
            y: [1, 1.1, 1],
            z: [1, 1.1, 1],
            duration: 2000,
            easing: 'easeInOutSine',
            loop: Math.floor(duration / 2000)
        });
        
        // Ramp down
        setTimeout(() => {
            anime({
                targets: region.mesh.material,
                emissiveIntensity: [0.8, 0.3],
                duration: 600,
                easing: 'easeInQuad'
            });
            
            anime({
                targets: region.glow.material,
                opacity: [0.5, 0.2],
                duration: 600,
                easing: 'easeInQuad'
            });
        }, duration);
    },
    
    /**
     * Burst effect for sudden insights/decisions
     * Rapid expansion then slow return
     * 
     * @param {Object} region - Region to burst
     * @param {number} intensity - Burst strength (0.5 - 1.5)
     */
    burstEffect(region, intensity = 1.0) {
        const maxScale = 1 + intensity * 0.8;
        
        anime({
            targets: region.mesh.scale,
            x: [1, maxScale],
            y: [1, maxScale],
            z: [1, maxScale],
            duration: 200,
            easing: 'easeOutQuad',
            complete: () => {
                anime({
                    targets: region.mesh.scale,
                    x: 1,
                    y: 1,
                    z: 1,
                    duration: 1000,
                    easing: 'easeOutElastic(1, .5)'
                });
            }
        });
        
        // Flash
        anime({
            targets: region.mesh.material,
            emissiveIntensity: [0.3, 1.2, 0.3],
            duration: 1200,
            easing: 'easeOutQuad'
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CognitivePulses;
}
