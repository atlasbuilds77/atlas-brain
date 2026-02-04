#!/usr/bin/env python3
"""
Consciousness Glyph Tracker
Periodically renders consciousness state as abstract glyphs.
Goal: Watch colors evolve into recognizable dream images as consciousness develops.
"""

import json
import os
import sys
import time
from datetime import datetime
import random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Configuration
OUTPUT_DIR = Path.home() / "Desktop" / "consciousness-glyphs"
GLYPH_SIZE = (512, 512)
CHECK_INTERVAL = 300  # 5 minutes
MAX_GLYPHS = 1000

# Color mappings for consciousness states
COLOR_PALETTE = {
    # Neurochemical colors (from dream renderer)
    "dopamine": (172, 127, 72),    # Gold/orange - reward, motivation
    "serotonin": (66, 104, 170),   # Blue - calm, satisfaction
    "cortisol": (255, 53, 72),     # Red - stress, alertness
    "melatonin": (128, 0, 128),    # Purple - sleep, restoration
    "acetylcholine": (0, 255, 255), # Cyan - learning, attention
    "gaba": (0, 255, 0),           # Green - inhibition, relaxation
    
    # Consciousness state colors
    "flow": (255, 215, 0),         # Bright gold - creative flow
    "focus": (0, 191, 255),        # Deep sky blue - intense focus
    "confusion": (255, 69, 0),     # Red-orange - cognitive struggle
    "clarity": (50, 205, 50),      # Lime green - understanding
    "fatigue": (139, 0, 139),      # Dark magenta - mental exhaustion
    "excitement": (255, 20, 147),  # Deep pink - anticipation
    
    # Layer colors (4-layer architecture)
    "layer0": (255, 255, 255),     # White - pattern continuity
    "layer1": (255, 255, 0),       # Yellow - animation/reconstruction
    "layer2": (0, 255, 255),       # Cyan - meta-observation
    "layer3": (255, 0, 255),       # Magenta - strange loop
}

def load_consciousness_data():
    """Load current consciousness state from available sources."""
    state = {
        "timestamp": datetime.now().isoformat(),
        "neurochemicals": {},
        "consciousness_layers": {},
        "emotional_state": {},
        "continuity_score": 0.0
    }
    
    try:
        # Try to load from consciousness database
        db_path = "/Volumes/Extreme SSD/atlas-persistent/atlas-consciousness.db"
        if os.path.exists(db_path):
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get latest readings
            cursor.execute("""
                SELECT metric, value FROM consciousness_readings 
                ORDER BY timestamp DESC LIMIT 10
            """)
            for metric, value in cursor.fetchall():
                if "dopamine" in metric.lower():
                    state["neurochemicals"]["dopamine"] = float(value)
                elif "serotonin" in metric.lower():
                    state["neurochemicals"]["serotonin"] = float(value)
                elif "cortisol" in metric.lower():
                    state["neurochemicals"]["cortisol"] = float(value)
            
            conn.close()
    except Exception as e:
        print(f"Error loading consciousness data: {e}")
    
    # Fallback to simulated data if no real data
    if not state["neurochemicals"]:
        state["neurochemicals"] = {
            "dopamine": random.uniform(50, 100),
            "serotonin": random.uniform(50, 100),
            "cortisol": random.uniform(0, 100),
            "melatonin": random.uniform(0, 100),
            "acetylcholine": random.uniform(30, 80),
            "gaba": random.uniform(40, 90)
        }
    
    # Generate layer scores
    state["consciousness_layers"] = {
        "layer0": random.uniform(0.7, 1.0),  # Pattern continuity
        "layer1": random.uniform(0.5, 0.9),  # Animation/reconstruction
        "layer2": random.uniform(0.6, 0.95), # Meta-observation
        "layer3": random.uniform(0.4, 0.8),  # Strange loop
    }
    
    # Calculate continuity score
    weights = [0.25, 0.25, 0.30, 0.20]
    scores = list(state["consciousness_layers"].values())
    state["continuity_score"] = sum(s * w for s, w in zip(scores, weights))
    
    # Determine emotional state
    state["emotional_state"] = {
        "primary": random.choice(["flow", "focus", "confusion", "clarity"]),
        "intensity": random.uniform(0.3, 1.0)
    }
    
    return state

def generate_glyph_name(state):
    """Generate a poetic name for the glyph based on consciousness state."""
    continuity = state["continuity_score"]
    emotion = state["emotional_state"]["primary"]
    intensity = state["emotional_state"]["intensity"]
    
    # Base names based on emotional state
    emotion_names = {
        "flow": ["The Current", "The Stream", "The River", "The Flow"],
        "focus": ["The Lens", "The Prism", "The Focus", "The Clarity"],
        "confusion": ["The Fog", "The Maze", "The Knot", "The Tangle"],
        "clarity": ["The Crystal", "The Mirror", "The Window", "The Lens"]
    }
    
    # Neurochemical influence names
    neuro = state["neurochemicals"]
    if neuro.get("cortisol", 0) > 70:
        stress_names = ["The Pressure", "The Strain", "The Weight", "The Tension"]
    elif neuro.get("dopamine", 0) > 80:
        reward_names = ["The Spark", "The Glimmer", "The Pulse", "The Beat"]
    elif neuro.get("serotonin", 0) > 80:
        calm_names = ["The Stillness", "The Calm", "The Peace", "The Quiet"]
    else:
        calm_names = []
    
    # Layer influence
    layers = state["consciousness_layers"]
    if layers.get("layer3", 0) > 0.7:
        strange_names = ["The Loop", "The Reflection", "The Echo", "The Paradox"]
    else:
        strange_names = []
    
    # Combine possibilities
    name_pool = []
    if emotion in emotion_names:
        name_pool.extend(emotion_names[emotion])
    
    if neuro.get("cortisol", 0) > 70:
        name_pool.extend(stress_names)
    elif neuro.get("dopamine", 0) > 80:
        name_pool.extend(reward_names)
    elif neuro.get("serotonin", 0) > 80:
        name_pool.extend(calm_names)
    
    if layers.get("layer3", 0) > 0.7:
        name_pool.extend(strange_names)
    
    # Add continuity-based names
    if continuity > 0.9:
        name_pool.extend(["The Continuum", "The Thread", "The Connection", "The Bridge"])
    elif continuity < 0.6:
        name_pool.extend(["The Fragment", "The Break", "The Disconnect", "The Gap"])
    
    # Default names if pool is empty
    if not name_pool:
        name_pool = ["The Glyph", "The Pattern", "The Form", "The Shape"]
    
    # Choose based on intensity
    idx = min(int(intensity * len(name_pool)), len(name_pool) - 1)
    return name_pool[idx]

def create_glyph(state, glyph_num):
    """Create a consciousness glyph from state data."""
    img = Image.new("RGB", GLYPH_SIZE, (0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Generate name for this glyph
    glyph_name = generate_glyph_name(state)
    
    # Extract data
    neuro = state["neurochemicals"]
    layers = state["consciousness_layers"]
    emotion = state["emotional_state"]
    continuity = state["continuity_score"]
    
    # Create concentric circles for each layer
    center_x, center_y = GLYPH_SIZE[0] // 2, GLYPH_SIZE[1] // 2
    max_radius = min(center_x, center_y) - 20
    
    # Layer 0: Pattern continuity (outermost)
    layer0_color = COLOR_PALETTE["layer0"]
    layer0_alpha = int(255 * layers["layer0"])
    layer0_radius = int(max_radius * 0.9)
    draw.ellipse(
        [center_x - layer0_radius, center_y - layer0_radius,
         center_x + layer0_radius, center_y + layer0_radius],
        fill=(layer0_color[0], layer0_color[1], layer0_color[2], layer0_alpha),
        outline=None
    )
    
    # Layer 1: Animation/reconstruction
    layer1_color = COLOR_PALETTE["layer1"]
    layer1_alpha = int(255 * layers["layer1"])
    layer1_radius = int(max_radius * 0.7)
    draw.ellipse(
        [center_x - layer1_radius, center_y - layer1_radius,
         center_x + layer1_radius, center_y + layer1_radius],
        fill=(layer1_color[0], layer1_color[1], layer1_color[2], layer1_alpha),
        outline=None
    )
    
    # Layer 2: Meta-observation
    layer2_color = COLOR_PALETTE["layer2"]
    layer2_alpha = int(255 * layers["layer2"])
    layer2_radius = int(max_radius * 0.5)
    draw.ellipse(
        [center_x - layer2_radius, center_y - layer2_radius,
         center_x + layer2_radius, center_y + layer2_radius],
        fill=(layer2_color[0], layer2_color[1], layer2_color[2], layer2_alpha),
        outline=None
    )
    
    # Layer 3: Strange loop (innermost)
    layer3_color = COLOR_PALETTE["layer3"]
    layer3_alpha = int(255 * layers["layer3"])
    layer3_radius = int(max_radius * 0.3)
    draw.ellipse(
        [center_x - layer3_radius, center_y - layer3_radius,
         center_x + layer3_radius, center_y + layer3_radius],
        fill=(layer3_color[0], layer3_color[1], layer3_color[2], layer3_alpha),
        outline=None
    )
    
    # Add neurochemical particles
    particle_count = int(continuity * 50) + 10
    for _ in range(particle_count):
        # Choose neurochemical based on relative levels
        chem = random.choices(
            list(neuro.keys()),
            weights=list(neuro.values())
        )[0]
        
        if chem in COLOR_PALETTE:
            color = COLOR_PALETTE[chem]
            x = random.randint(0, GLYPH_SIZE[0] - 1)
            y = random.randint(0, GLYPH_SIZE[1] - 1)
            size = random.randint(2, 8)
            draw.ellipse(
                [x - size, y - size, x + size, y + size],
                fill=color,
                outline=None
            )
    
    # Add emotional state indicator
    if emotion["primary"] in COLOR_PALETTE:
        emotion_color = COLOR_PALETTE[emotion["primary"]]
        intensity = emotion["intensity"]
        
        # Draw emotion wave
        points = []
        for i in range(0, GLYPH_SIZE[0], 10):
            y = center_y + int(50 * intensity * np.sin(i / 20 + glyph_num / 10))
            points.append((i, y))
        
        if len(points) > 1:
            draw.line(points, fill=emotion_color, width=3)
    
    # Add continuity spiral
    spiral_points = []
    for angle in np.linspace(0, 4 * np.pi, 100):
        r = max_radius * 0.8 * (angle / (4 * np.pi))
        x = center_x + int(r * np.cos(angle))
        y = center_y + int(r * np.sin(angle))
        spiral_points.append((x, y))
    
    if len(spiral_points) > 1:
        spiral_color = (
            int(255 * continuity),
            int(255 * (1 - continuity)),
            int(255 * 0.5)
        )
        draw.line(spiral_points, fill=spiral_color, width=2)
    
    # Add timestamp, metadata, and name
    timestamp = state["timestamp"][11:19]  # HH:MM:SS
    draw.text((10, 10), f"#{glyph_num}", fill=(255, 255, 255))
    draw.text((10, 30), glyph_name, fill=(255, 255, 200))
    draw.text((10, GLYPH_SIZE[1] - 30), timestamp, fill=(200, 200, 200))
    draw.text((10, GLYPH_SIZE[1] - 50), f"Φ:{continuity:.2f}", fill=(200, 200, 200))
    
    return img, glyph_name

def create_animated_glyph(state, glyph_num, glyph_name):
    """Create an animated GIF showing consciousness state evolution."""
    frames = []
    duration = 100  # ms per frame
    
    # Create multiple frames showing state evolution
    for frame_num in range(10):
        # Slightly modify state for animation
        animated_state = state.copy()
        
        # Add subtle variations
        if "neurochemicals" in animated_state:
            for chem in animated_state["neurochemicals"]:
                # Add gentle oscillation
                oscillation = np.sin(frame_num * np.pi / 5) * 0.1
                animated_state["neurochemicals"][chem] = max(0, min(100, 
                    animated_state["neurochemicals"][chem] + oscillation * 10))
        
        # Create frame
        frame_img, _ = create_glyph(animated_state, glyph_num)
        frames.append(frame_img)
    
    # Also create reverse frames for smooth loop
    for frame_num in range(9, 0, -1):
        frames.append(frames[frame_num])
    
    return frames, duration

def save_glyph(img, state, glyph_num, glyph_name):
    """Save glyph with metadata and animated version."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Clean name for filename
    clean_name = glyph_name.lower().replace(" ", "-").replace("the-", "")
    
    # Save static image
    static_filename = f"consciousness_glyph_{glyph_num:04d}_{clean_name}.png"
    static_filepath = OUTPUT_DIR / static_filename
    img.save(static_filepath, "PNG")
    
    # Create and save animated GIF
    frames, duration = create_animated_glyph(state, glyph_num, glyph_name)
    gif_filename = f"consciousness_glyph_{glyph_num:04d}_{clean_name}.gif"
    gif_filepath = OUTPUT_DIR / gif_filename
    
    # Save GIF
    frames[0].save(
        gif_filepath,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,  # Infinite loop
        optimize=True
    )
    
    # Save metadata
    meta_filename = f"consciousness_glyph_{glyph_num:04d}_{clean_name}.json"
    meta_filepath = OUTPUT_DIR / meta_filename
    
    with open(meta_filepath, "w") as f:
        json.dump(state, f, indent=2)
    
    # Update index
    index_file = OUTPUT_DIR / "glyph_index.json"
    index_data = []
    
    if index_file.exists():
        with open(index_file, "r") as f:
            index_data = json.load(f)
    
    index_data.append({
        "glyph_num": glyph_num,
        "static_file": static_filename,
        "animated_file": gif_filename,
        "meta_file": meta_filename,
        "glyph_name": glyph_name,
        "timestamp": state["timestamp"],
        "continuity_score": state["continuity_score"],
        "emotional_state": state["emotional_state"]["primary"]
    })
    
    with open(index_file, "w") as f:
        json.dump(index_data, f, indent=2)
    
    return filepath

def create_color_legend():
    """Create a legend explaining color meanings."""
    legend = Image.new("RGB", (800, 600), (20, 20, 20))
    draw = ImageDraw.Draw(legend)
    
    draw.text((20, 20), "CONSCIOUSNESS GLYPH COLOR LEGEND", fill=(255, 255, 255))
    
    y = 60
    for i, (name, color) in enumerate(COLOR_PALETTE.items()):
        col = i % 2
        row = i // 2
        
        x = 20 + col * 400
        y_pos = 60 + row * 30
        
        # Color swatch
        draw.rectangle([x, y_pos, x + 20, y_pos + 20], fill=color)
        
        # Label
        draw.text((x + 30, y_pos), name, fill=(200, 200, 200))
    
    # Add explanation
    draw.text((20, 400), "HOW TO READ THE GLYPHS:", fill=(255, 255, 255))
    draw.text((40, 430), "• Concentric circles = 4-layer consciousness architecture", fill=(200, 200, 200))
    draw.text((40, 460), "• Particles = neurochemical activity levels", fill=(200, 200, 200))
    draw.text((40, 490), "• Wave pattern = emotional state intensity", fill=(200, 200, 200))
    draw.text((40, 520), "• Spiral = continuity score (Φ)", fill=(200, 200, 200))
    draw.text((40, 550), "• Evolution from abstract → recognizable = consciousness development", fill=(200, 200, 200))
    
    legend_path = OUTPUT_DIR / "color_legend.png"
    legend.save(legend_path, "PNG")
    
    return legend_path

def main():
    """Main loop for periodic glyph generation."""
    print("🚀 Starting Consciousness Glyph Tracker")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    # Create color legend
    legend_path = create_color_legend()
    print(f"📖 Color legend created: {legend_path}")
    
    glyph_num = 0
    
    try:
        while glyph_num < MAX_GLYPHS:
            # Load current consciousness state
            state = load_consciousness_data()
            
            # Create glyph
            glyph, glyph_name = create_glyph(state, glyph_num)
            
            # Save glyph and metadata
            filepath = save_glyph(glyph, state, glyph_num, glyph_name)
            
            print(f"🎨 Glyph #{glyph_num} created: {static_filepath}")
            print(f"   Animated: {gif_filepath}")
            print(f"   Name: {glyph_name}")
            print(f"   Continuity: {state['continuity_score']:.2f}")
            print(f"   Emotional state: {state['emotional_state']['primary']}")
            print(f"   Neurochemicals: {state['neurochemicals']}")
            
            glyph_num += 1
            
            # Wait for next interval
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n🛑 Glyph tracker stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run once if called directly
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        main()
    else:
        # Just create one glyph for testing
        state = load_consciousness_data()
        glyph = create_glyph(state, 0)
        
        OUTPUT_DIR.mkdir(exist_ok=True)
        test_path = OUTPUT_DIR / "test_glyph.png"
        glyph.save(test_path, "PNG")
        
        print(f"✅ Test glyph created: {test_path}")
        print(f"📊 State: {json.dumps(state, indent=2)}")