from modules import *
from modules.langchainManager.chain_dialog import ChainDialog
from modules.promptManager.prompt_manager import PROMPTS_STORAGE_PATH
from modules.modelManager.model_manager import MODELS_STORAGE_PATH, API_KEYS_STORAGE_PATH


class LangchainManagerWidget(AbstractWidget):
    def __init__(self):
        super().__init__()
        self.load_chains()
        self.load_api_keys()
        self.load_models()
        self.load_prompts()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # List of Chains
        self.chain_list = QListWidget()
        self.chain_list.itemClicked.connect(self.load_chain)
        self.populate_chain_list()
        layout.addWidget(QLabel("Available LangChains:"))
        layout.addWidget(self.chain_list)

        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = QPushButton("Create Chain")
        self.edit_button = QPushButton("Edit Chain")
        self.delete_button = QPushButton("Delete Chain")
        button_layout.addWidget(self.create_button)
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        # Chain Details
        self.details_label = QLabel("Chain Details:")
        self.details_editor = QTextEdit()
        self.details_editor.setReadOnly(True)
        layout.addWidget(self.details_label)
        layout.addWidget(self.details_editor)

        # Connect buttons to functions
        self.create_button.clicked.connect(self.create_chain)
        self.edit_button.clicked.connect(self.edit_chain)
        self.delete_button.clicked.connect(self.delete_chain)

        self.setLayout(layout)

    def load_chains(self):
        """Load chains from the JSON file."""
        if not os.path.exists(CHAIN_STORAGE_PATH):
            os.makedirs(os.path.dirname(CHAIN_STORAGE_PATH), exist_ok=True)
            with open(CHAIN_STORAGE_PATH, 'w') as f:
                json.dump({}, f)

        try:
            with open(CHAIN_STORAGE_PATH, 'r') as f:
                self.chains = json.load(f)
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load chains: {e}")
            self.chains = {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.chains = {}

    def save_chains(self):
        """Save chains to the JSON file."""
        try:
            with open(CHAIN_STORAGE_PATH, 'w') as f:
                json.dump(self.chains, f, indent=4)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save chains: {e}")

    def load_prompts(self):
        """Load prompts from the JSON file."""
        if not os.path.exists(PROMPTS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "Prompts storage file not found.")
            self.prompts = []
            return

        try:
            with open(PROMPTS_STORAGE_PATH, 'r') as f:
                prompts_data = json.load(f)
                self.prompts = sorted(prompts_data.keys())
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load prompts: {e}")
            self.prompts = []
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            self.prompts = []

    def populate_chain_list(self):
        """Populate the QListWidget with chain names."""
        self.chain_list.clear()
        for chain_name in self.chains:
            self.chain_list.addItem(chain_name)

    def display_chain_details(self, chain_name):
        """Display detailed information of the selected chain, including linked Prompt and Model."""
        chain = self.chains.get(chain_name, {})
        prompt_name = chain.get("prompt_name", "N/A")
        model_name = chain.get("model_name", "N/A")
        output_parser = chain.get("output_parser", "N/A")

        # Fetch Prompt Details
        prompt_details = self.get_prompt_details(prompt_name)

        # Fetch Model Details
        model_details = self.get_model_details(model_name)

        # Format the details
        details = (
            f"<h2>Chain Name:</h2> {chain_name}<br><br>"
            f"<h3>Prompt Details:</h3>"
            f"<b>Name:</b> {prompt_name}<br>"
            f"<b>System Prompt Template:</b>"
            f"{prompt_details.get('system_prompt_template', 'N/A')}<br>"
            f"<b>User Prompt Template:</b>"
            f"{prompt_details.get('user_prompt_template', 'N/A')}<br>"
            f"<b>Keys:</b> {', '.join(prompt_details.get('keys', []))}<br><br>"
            f"<h3>Model Details:</h3>"
            f"<b>Name:</b> {model_name}<br>"
            f"<b>Type:</b> {model_details.get('type', 'N/A')}<br>"
            f"<b>LLM Model:</b> {model_details.get('llm_model', 'N/A')}<br>"
            f"<b>API Key Name:</b> {model_details.get('api_key_name', 'N/A')}<br><br>"
            f"<h3>Output Parser:</h3> {output_parser}"
        )

        self.details_editor.setHtml(details)

    def get_prompt_details(self, prompt_name):
        """Retrieve detailed information about a prompt."""
        if not os.path.exists(PROMPTS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "Prompts storage file not found.")
            return {}

        try:
            with open(PROMPTS_STORAGE_PATH, 'r') as f:
                prompts_data = json.load(f)
                prompt = prompts_data.get(prompt_name, {})
                return prompt
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load prompts: {e}")
            return {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return {}

    def get_model_details(self, model_name):
        """Retrieve detailed information about a model."""
        if not os.path.exists(MODELS_STORAGE_PATH):
            QMessageBox.critical(self, "Error", "Models storage file not found.")
            return {}

        try:
            with open(MODELS_STORAGE_PATH, 'r') as f:
                models_data = json.load(f)
                model = models_data.get(model_name, {})
                return model
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "Error", f"Failed to load models: {e}")
            return {}
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")
            return {}

    def create_chain(self):
        """Create a new LangChain."""
        if not self.prompts:
            QMessageBox.warning(self, "Error", "No prompts available. Please add prompts first.")
            return
        if not self.models:
            QMessageBox.warning(self, "Error", "No models available. Please add models first.")
            return
        if not self.api_keys:
            QMessageBox.warning(self, "Error", "No API keys available. Please add API keys first.")
            return

        # Define hardcoded output parsers
        output_parsers = ["StrOutputParser", "CustomParser"]

        dialog = ChainDialog(
            self,
            title="Create New Chain",
            prompts=self.prompts,
            models=self.models,
            output_parsers=output_parsers
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            chain_data = dialog.get_chain_data()
            chain_name = chain_data['chain_name']
            prompt_name = chain_data['prompt_name']
            model_name = chain_data['model_name']
            output_parser = chain_data['output_parser']

            if chain_name in self.chains:
                QMessageBox.warning(self, "Error", f"Chain '{chain_name}' already exists.")
                return

            # Save the new chain
            self.chains[chain_name] = {
                "prompt_name": prompt_name,
                "model_name": model_name,
                "output_parser": output_parser
            }
            self.save_chains()
            self.populate_chain_list()
            QMessageBox.information(self, "Success", f"Chain '{chain_name}' created successfully.")

    def edit_chain(self):
        """Edit the selected LangChain."""
        current_item = self.chain_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a chain to edit.")
            return
        chain_name = current_item.text()
        chain = self.chains.get(chain_name, {})

        # Define hardcoded output parsers
        output_parsers = ["StrOutputParser", "CustomParser"]

        dialog = ChainDialog(
            self,
            title="Edit Chain",
            chain_data={
                "chain_name": chain_name,
                "prompt_name": chain.get("prompt_name", ""),
                "model_name": chain.get("model_name", ""),
                "output_parser": chain.get("output_parser", "")
            },
            prompts=self.prompts,
            models=self.models,
            output_parsers=output_parsers
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            updated_data = dialog.get_chain_data()
            new_chain_name = updated_data['chain_name']
            new_prompt_name = updated_data['prompt_name']
            new_model_name = updated_data['model_name']
            new_output_parser = updated_data['output_parser']

            if new_chain_name != chain_name and new_chain_name in self.chains:
                QMessageBox.warning(self, "Error", f"Chain name '{new_chain_name}' already exists.")
                return

            # Update the chain
            if new_chain_name != chain_name:
                del self.chains[chain_name]
            self.chains[new_chain_name] = {
                "prompt_name": new_prompt_name,
                "model_name": new_model_name,
                "output_parser": new_output_parser
            }
            self.save_chains()
            self.populate_chain_list()
            QMessageBox.information(self, "Success", f"Chain '{new_chain_name}' updated successfully.")

    def delete_chain(self):
        """Delete the selected LangChain."""
        current_item = self.chain_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Error", "Please select a chain to delete.")
            return
        chain_name = current_item.text()
        confirm = QMessageBox.question(
            self, "Delete Chain",
            f"Are you sure you want to delete the chain '{chain_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            del self.chains[chain_name]
            self.save_chains()
            self.populate_chain_list()
            self.details_editor.clear()
            QMessageBox.information(self, "Success", f"Chain '{chain_name}' deleted successfully.")

    def load_chain(self, item):
        """Load and display the selected chain's details."""
        chain_name = item.text()
        self.display_chain_details(chain_name)
