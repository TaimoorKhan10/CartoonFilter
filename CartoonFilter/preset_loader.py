import os
import json
from cartoon_filter import CartoonFilter

class PresetLoader:
    """
    Utility class to load and apply preset configurations
    """
    def __init__(self):
        self.presets = {}
        self.preset_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "presets.json")
        self.load_presets()
    
    def load_presets(self):
        """Load presets from the presets.json file"""
        try:
            if os.path.exists(self.preset_file):
                with open(self.preset_file, 'r') as f:
                    data = json.load(f)
                    if 'presets' in data:
                        self.presets = data['presets']
                        return True
        except Exception as e:
            print(f"Error loading presets: {e}")
        
        # Load default presets if file doesn't exist or has an error
        self.presets = {
            "default": {
                "edge_detection_method": "canny",
                "canny_threshold1": 100,
                "canny_threshold2": 200,
                "edge_blur": 5,
                "line_size": 7,
                "edge_preserve": True,
                "bilateral_d": 9,
                "bilateral_sigma_color": 75,
                "bilateral_sigma_space": 75,
                "quantization_method": "kmeans",
                "num_colors": 8,
                "saturation_factor": 1.5
            }
        }
        return False
    
    def save_preset(self, name, config):
        """Save a new preset configuration"""
        self.presets[name] = config
        
        try:
            with open(self.preset_file, 'w') as f:
                json.dump({'presets': self.presets}, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving preset: {e}")
            return False
    
    def get_preset_names(self):
        """Get list of available preset names"""
        return list(self.presets.keys())
    
    def get_preset(self, name):
        """Get a specific preset configuration"""
        if name in self.presets:
            return self.presets[name]
        return None
    
    def apply_preset(self, cartoon_filter, name):
        """Apply a preset configuration to a CartoonFilter instance"""
        if name not in self.presets:
            return False
        
        preset = self.presets[name]
        
        for key, value in preset.items():
            if hasattr(cartoon_filter, key):
                setattr(cartoon_filter, key, value)
        
        return True
    
    def delete_preset(self, name):
        """Delete a preset configuration"""
        if name in self.presets:
            del self.presets[name]
            
            try:
                with open(self.preset_file, 'w') as f:
                    json.dump({'presets': self.presets}, f, indent=4)
                return True
            except Exception as e:
                print(f"Error saving presets after deletion: {e}")
        
        return False

def create_preset_from_filter(cartoon_filter):
    """Create a preset configuration from a CartoonFilter instance"""
    preset = {
        "edge_detection_method": cartoon_filter.edge_detection_method,
        "canny_threshold1": cartoon_filter.canny_threshold1,
        "canny_threshold2": cartoon_filter.canny_threshold2,
        "edge_blur": cartoon_filter.edge_blur,
        "line_size": cartoon_filter.line_size,
        "edge_preserve": cartoon_filter.edge_preserve,
        "bilateral_d": cartoon_filter.bilateral_d,
        "bilateral_sigma_color": cartoon_filter.bilateral_sigma_color,
        "bilateral_sigma_space": cartoon_filter.bilateral_sigma_space,
        "quantization_method": cartoon_filter.quantization_method,
        "num_colors": cartoon_filter.num_colors,
        "saturation_factor": cartoon_filter.saturation_factor
    }
    
    return preset 