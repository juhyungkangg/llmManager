import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout,
    QTextEdit, QLabel, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt
PROMPTS_STORAGE_PATH = "data/prompts.json"
MODELS_STORAGE_PATH = "data/models.json"
API_KEYS_STORAGE_PATH = "data/api_keys.json"
SECRET_KEY_PATH = "secret.key"
CHAIN_STORAGE_PATH = "data/chains.json"


class AbstractWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__()

    def load_prompts(self):
        """Load prompts from the JSON file."""
        if not os.path.exists(PROMPTS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "Prompts storage file not found.")
            self.prompts = {}
            return

        try:
            with open(PROMPTS_STORAGE_PATH, 'r') as f:
                prompts_data = json.load(f)
                self.prompts = prompts_data
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load prompts: {e}")
            self.prompts = {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.prompts = {}

    def load_models(self):
        """Load models from the JSON file."""
        if not os.path.exists(MODELS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "Models storage file not found.")
            self.models = {}
            return

        try:
            with open(MODELS_STORAGE_PATH, 'r') as f:
                models_data = json.load(f)
                self.models = models_data
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load models: {e}")
            self.models = {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.models = {}

    def load_api_keys(self):
        """Load API keys from the JSON file."""
        if not os.path.exists(API_KEYS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "API Keys storage file not found.")
            self.api_keys = {}
            return

        try:
            with open(API_KEYS_STORAGE_PATH, 'r') as f:
                api_keys_data = json.load(f)
                self.api_keys = api_keys_data
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load API keys: {e}")
            self.api_keys = {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.api_keys = {}