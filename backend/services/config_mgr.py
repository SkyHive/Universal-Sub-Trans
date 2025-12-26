import json
import os
import logging
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
        self._apply_log_level()

    def _apply_log_level(self) -> None:
        """Applies the log level from config to the global logger."""
        level_str = self.config.app.log_level.upper()
        level = getattr(logging, level_str, logging.INFO)
        logger.setLevel(level)
        # Also update handlers
        for handler in logger.handlers:
            handler.setLevel(level)
        logger.info(f"log_level_set_to: {level_str}")

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
        logger.info(f"incoming_config_update_keys: {list(updates.keys())}")
        
        config_dict = self.config.model_dump()
        
        def deep_update(d: dict, u: dict) -> dict:
            for k, v in u.items():
                if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                    d[k] = deep_update(d[k], v)
                else:
                    d[k] = v
            return d

        updated_dict = deep_update(config_dict, updates)
        
        # Explicitly ensure language is preserved during merge from updates
        if 'app' in updates and isinstance(updates['app'], dict) and 'language' in updates['app']:
            new_lang = updates['app']['language']
            if 'app' not in updated_dict: updated_dict['app'] = {}
            updated_dict['app']['language'] = new_lang
            logger.info(f"forcing_language_update_to: {new_lang}")

        try:
            self.config = GlobalConfig(**updated_dict)
            logger.info("config_object_updated_successfully")
            self._apply_log_level()
            self.save_config()
        except Exception as e:
            logger.error(f"config_validation_failed: {e}")
            raise

# Global config manager instance
config_mgr = ConfigManager()
