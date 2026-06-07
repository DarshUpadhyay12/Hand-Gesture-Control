import json
import os
from loguru import logger

CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.config = json.load(f)
                logger.info("Configuration loaded successfully.")
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
                self._load_default()
        else:
            self._load_default()
            self.save_config()

    def _load_default(self):
        self.config = {
            "general": {
                "camera_index": 0,
                "width": 1280,
                "height": 720,
                "fps": 60,
                "mode": "mouse",
                "show_video": True,
                "auto_start": False
            },
            "sensitivity": {
                "mouse_smoothness": 5,
                "pinch_threshold": 40,
                "swipe_threshold": 100,
                "scroll_speed": 40
            },
            "features": {
                "mouse_control": True,
                "volume_brightness": True,
                "media_controls": True,
                "system_shortcuts": True,
                "presentation_mode": True,
                "drawing_mode": True
            }
        }
        logger.info("Loaded default configuration.")

    def save_config(self):
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            logger.info("Configuration saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, section, key):
        return self.config.get(section, {}).get(key)

    def set(self, section, key, value):
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self.save_config()
