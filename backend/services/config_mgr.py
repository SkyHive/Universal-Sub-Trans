import json
import os
from typing import Any
from appdirs import user_config_dir
from backend.models.schema import GlobalConfig
from backend.services.logger import logger

class ConfigManager:
    """
    Manages loading, saving, and updating the application configuration.
    """

    def __init__(self) -> None:
        self.config_dir = user_config_dir("UniversalSub", "UniversalSub")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, "config.json")
        self.config: GlobalConfig = self.load_config()

    def load_config(self) -> GlobalConfig:
        """
        Loads configuration from disk or returns default if not found.

        Returns:
            GlobalConfig: The loaded configuration.
        """
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return GlobalConfig(**data)
            except Exception as e:
                logger.error(f"failed_to_load_config: {e}", exc_info=True)
        
        # Return default config if file doesn't exist or is invalid
        return GlobalConfig()

    def save_config(self) -> None:
        """
        Saves the current configuration to disk.
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write(self.config.model_dump_json(indent=4))
            logger.info("config_saved_successfully")
        except Exception as e:
            logger.error(f"failed_to_save_config: {e}", exc_info=True)

    def update_config(self, updates: dict[str, Any]) -> None:
        """
        Updates the configuration with new values and saves.

        Args:
            updates (dict[str, Any]): Dictionary of updates to apply.
        """
        # This is a simplified update logic. 
        # In a real app, you might want deeper merging or validation.
        config_dict = self.config.model_dump()
        
        def deep_update(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict):
                    d[k] = deep_update(d.get(k, {}), v)
                else:
                    d[k] = v
            return d

        updated_dict = deep_update(config_dict, updates)
        self.config = GlobalConfig(**updated_dict)
        self.save_config()

# Global config manager instance
config_mgr = ConfigManager()
