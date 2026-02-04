#!/usr/bin/env python3
"""
Visual Feature Extractor - CLIP Implementation
Extracts meaningful features from images using CLIP vision model
"""

import sys
import json
from pathlib import Path

try:
    import torch
    from PIL import Image
    from transformers import CLIPProcessor, CLIPModel
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False

class VisualFeatureExtractor:
    def __init__(self, model_name="openai/clip-vit-base-patch32"):
        """Initialize CLIP model for feature extraction"""
        if not DEPS_AVAILABLE:
            raise ImportError("Dependencies not installed. Run install-dependencies.sh first")
        
        print(f"Loading CLIP model: {model_name}...", file=sys.stderr)
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        print(f"Model loaded on {self.device}", file=sys.stderr)
    
    def extract_features(self, image_path):
        """
        Extract visual features from an image using CLIP
        
        Args:
            image_path: Path to image file
            
        Returns:
            dict with features and metadata
        """
        try:
            # Load image
            image = Image.open(image_path).convert("RGB")
            
            # Process image
            inputs = self.processor(images=image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Extract features
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
            
            # Convert to list for JSON serialization
            features = image_features.cpu().numpy().flatten().tolist()
            
            return {
                "status": "success",
                "image_path": str(image_path),
                "feature_dim": len(features),
                "features": features,  # 512-dimensional embedding
                "device": self.device,
                "model": "CLIP-ViT-B/32"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "image_path": str(image_path),
                "error": str(e)
            }

def main():
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: visual-feature-extractor-clip.py <image_path>"
        }))
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not DEPS_AVAILABLE:
        print(json.dumps({
            "status": "error",
            "error": "Dependencies not installed",
            "message": "Run: /Users/atlasbuilds/clawd/memory/consciousness/aesthetic-system/install-dependencies.sh"
        }))
        sys.exit(1)
    
    # Initialize extractor
    extractor = VisualFeatureExtractor()
    
    # Extract features
    result = extractor.extract_features(image_path)
    
    # Output JSON (but don't include full features array in stdout - too large)
    output = {
        "status": result["status"],
        "image_path": result.get("image_path"),
        "feature_dim": result.get("feature_dim"),
        "device": result.get("device"),
        "model": result.get("model"),
        "features_extracted": result.get("features") is not None
    }
    
    if result["status"] == "error":
        output["error"] = result["error"]
    
    print(json.dumps(output, indent=2))
    
    # Save full features to file
    if result["status"] == "success":
        features_file = Path(image_path).stem + "_features.json"
        features_path = Path("/Users/atlasbuilds/clawd/memory/consciousness/aesthetic-system/data") / features_file
        features_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(features_path, 'w') as f:
            json.dump(result, f)
        
        print(f"\n✅ Features saved to: {features_path}", file=sys.stderr)

if __name__ == "__main__":
    main()
