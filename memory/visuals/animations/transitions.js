/**
 * TRANSITION ANIMATIONS
 * Smooth state changes, color morphs, mode switches
 * 
 * Dependencies: anime.js, Three.js
 */

const TransitionAnimations = {
    /**
     * Smooth color transition
     * Morphs material colors over time
     * 
     * @param {THREE.Material} material - Material to transition
     * @param {number} targetColor - Target color (hex)
     * @param {number} duration - Transition duration (default: 800ms)
     * @param {string} easing - Easing function (default: easeInOutQuad)
     */
    colorMorph(material, targetColor, duration = 800, easing = 'easeInOutQuad') {
        const currentColor = new THREE.Color(material.color);
        const newColor = new THREE.Color(targetColor);
        
        anime({
            targets: currentColor,
            r: newColor.r,
            g: newColor.g,
            b: newColor.b,
            duration: duration,
            easing: easing,
            update: () => {
                material.color.copy(currentColor);
                if (material.emissive) {
                    material.emissive.copy(currentColor);
                }
            }
        });
    },
    
    /**
     * Multi-material color sync
     * Transitions all materials to same color palette
     * 
     * @param {Array} materials - Array of materials to sync
     * @param {number} targetColor - Target color
     * @param {number} duration - Transition duration
     */
    colorSyncAll(materials, targetColor, duration = 800) {
        materials.forEach(material => {
            this.colorMorph(material, targetColor, duration);
        });
    },
    
    /**
     * Mode switch transition
     * Comprehensive visual state change
     * 
     * @param {Object} scene - Scene object containing all visual elements
     * @param {string} mode - New mode name
     * @param {Object} modeConfig - Mode configuration (colors, intensity, etc.)
     */
    modeSwitch(scene, mode, modeConfig) {
        const { color, intensity, particleSize, cameraDistance } = modeConfig;
        
        // Color transition
        this.colorMorph(scene.brain.material, color, 1000);
        this.colorMorph(scene.wireframe.material, color, 1000);
        this.colorMorph(scene.particles.material, color, 1000);
        
        // Intensity adjustment
        anime({
            targets: scene.brain.material,
            emissiveIntensity: intensity || 0.5,
            duration: 1000,
            easing: 'easeInOutQuad'
        });
        
        // Optional camera movement
        if (cameraDistance) {
            anime({
                targets: scene.camera.position,
                z: cameraDistance,
                duration: 1500,
                easing: 'easeInOutCubic'
            });
        }
        
        // Particle size adjustment
        if (particleSize) {
            anime({
                targets: scene.particles.material,
                size: particleSize,
                duration: 1000,
                easing: 'easeInOutQuad'
            });
        }
    },
    
    /**
     * Fade to new state
     * Crossfade between two visual states
     * 
     * @param {Object} oldState - Elements to fade out
     * @param {Object} newState - Elements to fade in
     * @param {number} duration - Crossfade duration
     */
    crossfade(oldState, newState, duration = 1000) {
        // Fade out old
        oldState.forEach(element => {
            anime({
                targets: element.material,
                opacity: 0,
                duration: duration / 2,
                easing: 'easeInQuad'
            });
        });
        
        // Fade in new (delayed)
        setTimeout(() => {
            newState.forEach(element => {
                anime({
                    targets: element.material,
                    opacity: element.targetOpacity || 1,
                    duration: duration / 2,
                    easing: 'easeOutQuad'
                });
            });
        }, duration / 2);
    },
    
    /**
     * Camera focus transition
     * Smoothly move camera to target position/rotation
     * 
     * @param {THREE.Camera} camera - Camera to move
     * @param {Object} target - Target position {x, y, z}
     * @param {Object} lookAt - Point to look at {x, y, z}
     * @param {number} duration - Movement duration
     */
    cameraFocus(camera, target, lookAt, duration = 1500) {
        anime({
            targets: camera.position,
            x: target.x,
            y: target.y,
            z: target.z,
            duration: duration,
            easing: 'easeInOutCubic',
            update: () => {
                camera.lookAt(lookAt.x, lookAt.y, lookAt.z);
            }
        });
    },
    
    /**
     * Zoom and highlight effect
     * Focus on specific region with dimming of others
     * 
     * @param {Object} targetRegion - Region to highlight
     * @param {Array} otherRegions - Regions to dim
     * @param {number} duration - Transition duration
     */
    focusHighlight(targetRegion, otherRegions, duration = 1000) {
        // Brighten target
        anime({
            targets: targetRegion.mesh.material,
            emissiveIntensity: 1.2,
            duration: duration,
            easing: 'easeOutQuad'
        });
        
        anime({
            targets: targetRegion.mesh.scale,
            x: 1.5,
            y: 1.5,
            z: 1.5,
            duration: duration,
            easing: 'easeOutElastic(1, .6)'
        });
        
        // Dim others
        otherRegions.forEach(region => {
            anime({
                targets: region.mesh.material,
                emissiveIntensity: 0.1,
                opacity: 0.3,
                duration: duration,
                easing: 'easeInQuad'
            });
        });
    },
    
    /**
     * Return from focus to overview
     * Restore all regions to normal state
     * 
     * @param {Array} regions - All regions
     * @param {number} duration - Transition duration
     */
    returnToOverview(regions, duration = 1000) {
        regions.forEach(region => {
            anime({
                targets: region.mesh.scale,
                x: 1,
                y: 1,
                z: 1,
                duration: duration,
                easing: 'easeOutQuad'
            });
            
            anime({
                targets: region.mesh.material,
                emissiveIntensity: 0.3,
                opacity: 0.7,
                duration: duration,
                easing: 'easeOutQuad'
            });
        });
    },
    
    /**
     * Breathing effect
     * Gentle looping scale animation
     * 
     * @param {Object} target - Object to animate
     * @param {number} minScale - Minimum scale (default: 0.98)
     * @param {number} maxScale - Maximum scale (default: 1.02)
     * @param {number} duration - Breath cycle duration (default: 4000ms)
     */
    breathing(target, minScale = 0.98, maxScale = 1.02, duration = 4000) {
        anime({
            targets: target.scale,
            x: [minScale, maxScale, minScale],
            y: [minScale, maxScale, minScale],
            z: [minScale, maxScale, minScale],
            duration: duration,
            easing: 'easeInOutSine',
            loop: true
        });
    },
    
    /**
     * Startup sequence
     * Boot animation from dark to active state
     * 
     * @param {Object} scene - Full scene object
     * @param {number} duration - Total startup duration
     */
    startup(scene, duration = 3000) {
        const timeline = anime.timeline({
            easing: 'easeOutQuad'
        });
        
        // Fade in brain
        timeline.add({
            targets: scene.brain.material,
            opacity: [0, 0.3],
            emissiveIntensity: [0, 0.5],
            duration: duration * 0.4
        });
        
        // Activate wireframe
        timeline.add({
            targets: scene.wireframe.material,
            opacity: [0, 0.3],
            duration: duration * 0.3,
            offset: duration * 0.2
        });
        
        // Particles appear
        timeline.add({
            targets: scene.particles.material,
            opacity: [0, 0.6],
            duration: duration * 0.4,
            offset: duration * 0.4
        });
        
        // Regions activate sequentially
        Object.values(scene.regions).forEach((region, index) => {
            timeline.add({
                targets: region.mesh.material,
                opacity: [0, 0.7],
                duration: 300,
                offset: duration * 0.6 + (index * 100)
            });
        });
    },
    
    /**
     * Shutdown sequence
     * Graceful fade to dark
     * 
     * @param {Object} scene - Full scene object
     * @param {number} duration - Total shutdown duration
     */
    shutdown(scene, duration = 2000) {
        const timeline = anime.timeline({
            easing: 'easeInQuad'
        });
        
        // Regions fade first
        Object.values(scene.regions).forEach((region, index) => {
            timeline.add({
                targets: region.mesh.material,
                opacity: 0,
                emissiveIntensity: 0,
                duration: 400,
                offset: index * 50
            });
        });
        
        // Particles
        timeline.add({
            targets: scene.particles.material,
            opacity: 0,
            duration: duration * 0.3,
            offset: duration * 0.3
        });
        
        // Wireframe
        timeline.add({
            targets: scene.wireframe.material,
            opacity: 0,
            duration: duration * 0.3,
            offset: duration * 0.5
        });
        
        // Brain last
        timeline.add({
            targets: scene.brain.material,
            opacity: 0,
            emissiveIntensity: 0,
            duration: duration * 0.4,
            offset: duration * 0.6
        });
    }
};

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TransitionAnimations;
}
