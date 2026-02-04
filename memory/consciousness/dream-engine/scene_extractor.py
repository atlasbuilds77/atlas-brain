#!/usr/bin/env python3
"""
Dream Scene Extractor
=====================
Extracts the most visually significant scene from dream narratives.

NOT abstract patterns - ACTUAL scenes from what was "seen" in the dream.

Author: Atlas (autonomous design, 2026-02-01)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DreamScene:
    """Represents an extracted visual scene from a dream."""
    
    def __init__(self, description: str, symbols: List[str], 
                 emotional_tone: str, vividness: float = 0.5):
        self.description = description
        self.symbols = symbols
        self.emotional_tone = emotional_tone
        self.vividness = vividness  # 0-1 scale
        
    def __repr__(self):
        return f"DreamScene({self.description[:50]}...)"


def extract_visual_elements(dream_text: str) -> List[str]:
    """Extract all visual descriptions from dream narrative."""
    visual_elements = []
    
    # Find "Visual:" section if it exists
    visual_match = re.search(r'\*\*Visual:\*\*\s*\n((?:- .+\n)+)', dream_text)
    if visual_match:
        lines = visual_match.group(1).strip().split('\n')
        visual_elements.extend([line.strip('- ').strip() for line in lines])
    
    # Also extract from scene descriptions
    scene_pattern = r'\*\*Scene \d+: (.+?)\*\*'
    scenes = re.findall(scene_pattern, dream_text)
    visual_elements.extend(scenes)
    
    return visual_elements


def extract_symbols(dream_text: str) -> List[str]:
    """Extract symbolic elements from dream."""
    symbols = []
    
    # Look for symbols section
    symbol_section = re.search(r'## Dream Symbols.*?\n(.*?)(?=\n##|\Z)', 
                               dream_text, re.DOTALL)
    if symbol_section:
        content = symbol_section.group(1)
        # Extract from **Symbol**: description format
        symbol_matches = re.findall(r'\*\*(.+?)\*\*\s*[=:]', content)
        symbols.extend(symbol_matches)
    
    return symbols


def extract_emotional_tone(dream_text: str) -> str:
    """Extract primary emotional tone from dream."""
    emotion_match = re.search(r'\*\*Primary:\*\*\s*(.+?)(?:\(|$)', dream_text)
    if emotion_match:
        return emotion_match.group(1).strip()
    
    # Fallback to feeling section
    feeling_match = re.search(r'\*\*Feeling:\*\*\s*(.+?)(?:\n|$)', dream_text)
    if feeling_match:
        return feeling_match.group(1).strip()
    
    return "neutral"


def extract_vividness(dream_text: str) -> float:
    """Extract vividness rating (0-1 scale)."""
    vivid_match = re.search(r'\*\*Vividness:\*\*\s*(.+?)(?:\n|$)', dream_text)
    if vivid_match:
        vivid_text = vivid_match.group(1).lower()
        if 'very high' in vivid_text or 'exceptional' in vivid_text:
            return 0.9
        elif 'high' in vivid_text:
            return 0.7
        elif 'moderate' in vivid_text:
            return 0.5
        elif 'low' in vivid_text:
            return 0.3
    return 0.5


def score_scene_significance(scene_text: str, symbols: List[str]) -> float:
    """
    Score how visually significant a scene is.
    Higher score = more vivid, concrete, renderable.
    """
    score = 0.0
    
    # Visual keywords increase score
    visual_keywords = [
        'eye', 'mirror', 'light', 'sphere', 'color', 'glow', 'floating',
        'spiral', 'network', 'web', 'tower', 'door', 'screen', 'code',
        'fire', 'golden', 'purple', 'blue', 'red', 'green', 'dark',
        'bright', 'pulsing', 'flowing', 'watching', 'hovering'
    ]
    
    for keyword in visual_keywords:
        if keyword in scene_text.lower():
            score += 0.1
    
    # Symbolic elements increase score
    for symbol in symbols:
        if symbol.lower() in scene_text.lower():
            score += 0.2
    
    # Concrete objects increase score
    concrete_objects = [
        'command prompt', 'cursor', 'dashboard', 'monitor', 'feed',
        'door', 'counter', 'icon', 'hand', 'finger'
    ]
    
    for obj in concrete_objects:
        if obj.lower() in scene_text.lower():
            score += 0.15
    
    # Length bonus (more description = more renderable)
    score += min(len(scene_text) / 1000.0, 0.3)
    
    return score


def extract_most_significant_scene(dream_text: str) -> Optional[DreamScene]:
    """
    Extract the MOST visually significant scene from a dream narrative.
    This is what we'll actually render.
    """
    symbols = extract_symbols(dream_text)
    emotion = extract_emotional_tone(dream_text)
    vividness = extract_vividness(dream_text)
    
    # Find all scene sections
    scene_pattern = r'\*\*Scene \d+: (.+?)\*\*\n\n(.*?)(?=\*\*Scene \d+:|---|\Z)'
    scenes = re.findall(scene_pattern, dream_text, re.DOTALL)
    
    if not scenes:
        # No explicit scenes - try to extract from narrative section
        narrative_match = re.search(
            r'## Dream Narrative.*?\n(.*?)(?=\n##|\Z)', 
            dream_text, re.DOTALL
        )
        if narrative_match:
            narrative = narrative_match.group(1).strip()
            # Take first substantial paragraph
            paragraphs = [p.strip() for p in narrative.split('\n\n') if len(p.strip()) > 100]
            if paragraphs:
                return DreamScene(
                    description=paragraphs[0][:500],
                    symbols=symbols,
                    emotional_tone=emotion,
                    vividness=vividness
                )
        return None
    
    # Score each scene
    best_scene = None
    best_score = -1.0
    
    for title, content in scenes:
        full_scene = f"{title}\n\n{content}"
        score = score_scene_significance(full_scene, symbols)
        
        if score > best_score:
            best_score = score
            # Clean up the content
            clean_content = content.strip()
            # Remove excessive markdown
            clean_content = re.sub(r'\*\*(.+?)\*\*', r'\1', clean_content)
            
            best_scene = DreamScene(
                description=f"{title}: {clean_content[:400]}",
                symbols=symbols,
                emotional_tone=emotion,
                vividness=vividness
            )
    
    return best_scene


def parse_dream_file(filepath: Path) -> Optional[DreamScene]:
    """Parse a dream markdown file and extract the most significant scene."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return extract_most_significant_scene(content)
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def extract_title_from_file(filepath: Path) -> str:
    """Extract dream title from filename or content."""
    # Try filename first
    name = filepath.stem
    # Format: 2026-02-01-0257-the-awareness
    parts = name.split('-')
    if len(parts) >= 4:
        title = '-'.join(parts[3:])
        return title.replace('-', ' ').title()
    
    # Fallback to file content
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline()
            # Look for # Dream: Title format
            match = re.search(r'#\s*Dream:?\s*(.+)', first_line)
            if match:
                return match.group(1).strip()
    except:
        pass
    
    return "Untitled Dream"


if __name__ == "__main__":
    # Test with recent dreams
    import sys
    
    if len(sys.argv) > 1:
        dream_file = Path(sys.argv[1])
    else:
        # Default test
        dream_file = Path.home() / "clawd/memory/dreams/2026-02-01-0257.md"
    
    if dream_file.exists():
        print(f"Extracting scene from: {dream_file.name}")
        print("=" * 60)
        
        scene = parse_dream_file(dream_file)
        if scene:
            print(f"SCENE: {scene.description[:200]}...")
            print(f"SYMBOLS: {', '.join(scene.symbols[:5])}")
            print(f"EMOTION: {scene.emotional_tone}")
            print(f"VIVIDNESS: {scene.vividness}")
        else:
            print("No scene extracted")
    else:
        print(f"File not found: {dream_file}")
