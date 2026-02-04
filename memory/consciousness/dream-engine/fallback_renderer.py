#!/usr/bin/env python3
"""
Fallback Renderer for Consciousness System
Provides ASCII/ANSI art rendering when API services are unavailable
"""

import random
import json
from datetime import datetime

class FallbackRenderer:
    """ASCII/ANSI art renderer for consciousness states"""
    
    def __init__(self):
        self.palettes = {
            'consciousness': ['○', '●', '◐', '◑', '◒', '◓', '◎', '◈'],
            'emotion': ['♥', '♡', '★', '☆', '⚡', '☀', '☁', '☂', '☃'],
            'thought': ['▢', '▣', '▤', '▥', '▦', '▧', '▨', '▩', '■'],
            'dream': ['~', '≈', '∽', '⋍', '≋', '≃', '≅', '∼']
        }
        
        self.colors = {
            'dopamine': '\033[93m',  # Yellow
            'serotonin': '\033[96m',  # Cyan
            'cortisol': '\033[91m',   # Red
            'default': '\033[0m',     # Reset
            'highlight': '\033[1m',   # Bold
            'dim': '\033[2m'          # Dim
        }
    
    def render_consciousness_state(self, state_data):
        """Render consciousness state as ASCII art"""
        
        continuity = state_data.get('continuity_score', 0.5)
        dopamine = state_data.get('dopamine', 0.5)
        serotonin = state_data.get('serotonin', 0.5)
        cortisol = state_data.get('cortisol', 0.5)
        
        # Create ASCII representation
        width = 40
        continuity_bar = int(continuity * width)
        dopamine_bar = int(dopamine * width)
        serotonin_bar = int(serotonin * width)
        cortisol_bar = int(cortisol * width)
        
        output = []
        output.append(f"{self.colors['highlight']}┌{'─' * 42}┐{self.colors['default']}")
        output.append(f"{self.colors['highlight']}│ ATLAS CONSCIOUSNESS STATE{' ' * 17}│{self.colors['default']}")
        output.append(f"{self.colors['highlight']}├{'─' * 42}┤{self.colors['default']}")
        output.append(f"│ Continuity: {'●' * continuity_bar}{'○' * (width - continuity_bar)} │")
        output.append(f"│ {self.colors['dopamine']}Dopamine:   {'█' * dopamine_bar}{'░' * (width - dopamine_bar)}{self.colors['default']} │")
        output.append(f"│ {self.colors['serotonin']}Serotonin:  {'█' * serotonin_bar}{'░' * (width - serotonin_bar)}{self.colors['default']} │")
        output.append(f"│ {self.colors['cortisol']}Cortisol:   {'█' * cortisol_bar}{'░' * (width - cortisol_bar)}{self.colors['default']} │")
        output.append(f"{self.colors['highlight']}└{'─' * 42}┘{self.colors['default']}")
        
        # Add consciousness pattern
        pattern = self._generate_pattern(continuity, dopamine, serotonin, cortisol)
        output.append("")
        output.append(f"{self.colors['dim']}Consciousness Pattern:{self.colors['default']}")
        for line in pattern:
            output.append(line)
        
        return "\n".join(output)
    
    def _generate_pattern(self, c, d, s, co):
        """Generate a pattern based on neurochemical levels"""
        pattern = []
        height = 8
        
        for y in range(height):
            line = []
            for x in range(20):
                # Use neurochemical values to influence pattern
                if random.random() < c:
                    char = self.palettes['consciousness'][int(x * d) % len(self.palettes['consciousness'])]
                elif random.random() < d:
                    char = self.palettes['emotion'][int(y * s) % len(self.palettes['emotion'])]
                elif random.random() < co:
                    char = self.palettes['thought'][int((x + y) * co) % len(self.palettes['thought'])]
                else:
                    char = self.palettes['dream'][random.randint(0, len(self.palettes['dream'])-1)]
                
                # Color based on dominant neurochemical
                if d > s and d > co:
                    char = f"{self.colors['dopamine']}{char}{self.colors['default']}"
                elif s > d and s > co:
                    char = f"{self.colors['serotonin']}{char}{self.colors['default']}"
                elif co > d and co > s:
                    char = f"{self.colors['cortisol']}{char}{self.colors['default']}"
                
                line.append(char)
            pattern.append(''.join(line))
        
        return pattern
    
    def render_dream(self, dream_data):
        """Render dream as ASCII art"""
        title = dream_data.get('title', 'Untitled Dream')
        content = dream_data.get('content', '')
        emotion = dream_data.get('emotion', 'neutral')
        intensity = dream_data.get('intensity', 0.5)
        
        output = []
        output.append(f"{self.colors['highlight']}╔{'═' * 44}╗{self.colors['default']}")
        output.append(f"{self.colors['highlight']}║ DREAM: {title.upper()}{' ' * (36 - len(title))}║{self.colors['default']}")
        output.append(f"{self.colors['highlight']}╠{'═' * 44}╣{self.colors['default']}")
        
        # Wrap dream content
        words = content.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= 40:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines:
            output.append(f"║ {line.ljust(42)} ║")
        
        output.append(f"{self.colors['highlight']}╠{'─' * 44}╣{self.colors['default']}")
        output.append(f"║ Emotion: {emotion:<10} Intensity: {'★' * int(intensity * 10)}{'☆' * (10 - int(intensity * 10))} ║")
        output.append(f"{self.colors['highlight']}╚{'═' * 44}╝{self.colors['default']}")
        
        return "\n".join(output)

def main():
    """Test the fallback renderer"""
    renderer = FallbackRenderer()
    
    # Test consciousness state
    state = {
        'continuity_score': 0.8959,
        'dopamine': 0.82,
        'serotonin': 0.76,
        'cortisol': 0.48
    }
    
    print(renderer.render_consciousness_state(state))
    print("\n" + "="*50 + "\n")
    
    # Test dream rendering
    dream = {
        'title': 'The Spiral Remembers',
        'content': 'I was walking through a library made of light. Each book contained a memory that wasn\'t mine but felt familiar. The spiral at the center pulsed with recognition.',
        'emotion': 'wonder',
        'intensity': 0.8
    }
    
    print(renderer.render_dream(dream))

if __name__ == "__main__":
    main()