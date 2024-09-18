from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pandas as pd
import ast
import time

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from cryptography.fernet import Fernet

from modules.langchainManager.langchain_manager import *
from modules import *


class LLMRunnerThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, chain_config, input_dir, output_dir, batch_size):
        super().__init__()
        self.chain_config = chain_config
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.is_running = True

        # Prompt
        with open(PROMPTS_STORAGE_PATH, 'r') as f:
            prompts_data = json.load(f)
            self.prompt = prompts_data[chain_config['prompt_name']]

        # Model
        with open(MODELS_STORAGE_PATH, 'r') as f:
            models_data = json.load(f)
            self.model = models_data[chain_config['model_name']]

        self.output_parser = chain_config['output_parser']

    def run(self):
        try:
            self.log.emit("Starting LLM Runner...")

            # Prompt template
            system_prompt_template = self.prompt['system_prompt_template']
            user_prompt_template = self.prompt['user_prompt_template']
            prompt_keys = self.prompt['keys']
            prompt_template = ChatPromptTemplate.from_messages(
                [("system", system_prompt_template), ("user", user_prompt_template)]
)
            # Model
            model_type = self.model['type']
            llm_model = self.model['llm_model']
            api_key_name = self.model['api_key_name']

            # API Key
            """Load or generate the encryption key."""
            if not os.path.exists(SECRET_KEY_PATH):
                print("")
            else:
                with open(SECRET_KEY_PATH, "rb") as key_file:
                    key = key_file.read()
            self.fernet = Fernet(key)


            with open(API_KEYS_STORAGE_PATH, 'r') as f:
                api_keys_data = json.load(f)
                encrypted_api_key = api_keys_data[api_key_name]['api_key']

            api_key = self.fernet.decrypt(encrypted_api_key.encode()).decode()

            # Model
            model = None
            if llm_model == 'ChatGPT':
                model = ChatOpenAI(model=model_type, api_key=api_key)
            else:
                print("Not yet developed for the provided model.")

            # Output Parser
            output_parser = None
            if self.output_parser == 'StrOutputParser':
                output_parser = StrOutputParser()

            # Process each CSV file in the input directory
            csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
            total_files = len(csv_files)
            for idx, file_name in enumerate(csv_files, start=1):
                if not self.is_running:
                    self.log.emit("LLM Runner stopped.")
                    break
                input_path = os.path.join(self.input_dir, file_name)


                self.log.emit(f"Processing file: {input_path}")
                df = pd.read_csv(input_path)

                total_rows = len(df)
                for i in range(0, total_rows, self.batch_size):
                    try:
                        if not self.is_running:
                            self.log.emit("LLM Runner stopped.")
                            break
                        batch = df.iloc[i:i + self.batch_size]
                        output_path = os.path.join(self.output_dir, f"{i}_processed_{file_name}")
                        self.log.emit(f"Processing rows {i} to {i + len(batch)}")

                        # Apply the LangChain to each row in the batch

                        message_batch = []
                        for _, row in batch.iterrows():
                            # Make Prompt
                            prompt = prompt_template.invoke({prompt_keys[i]: f"{row.get(prompt_keys[i])}"\
                                                             for i in range(len(prompt_keys))})

                            # Make messages
                            messages = prompt.to_messages()
                            message_batch.append(messages)

                        # Make chain
                        chain = model | output_parser

                        results = chain.batch(message_batch) # should be a list of dictionary

                        # Sample result
                        '''
                        {
                        'id' : 'id1'
                        'factor_id_1': 10,
                        'factor_id_2': 20,
                        }
                        '''

                        # Save the processed data to CSV
                        with open(f'{output_path}.txt', 'w') as file:
                            for result in results:
                                file.write(result + '\n')

                        # processed_results = [ast.literal_eval(result) for result in results]
                        # processed_df = pd.DataFrame(processed_results)
                        # processed_df.to_csv(output_path, index=False)
                        self.log.emit(f"Saved processed data to: {output_path}.txt")
                    except Exception as e:
                        self.log.emit(f"Error during execution: {str(e)}")
                        self.log.emit(f"Problem with: {file_name} at {i * self.batch_size} row")

                    progress_percent = int((idx - 1 + (i + len(batch)) / total_rows) / total_files * 100)
                    self.progress.emit(progress_percent)

                    time.sleep(120)

            self.log.emit("LLM Runner completed successfully.")
            self.finished_signal.emit()

        except Exception as e:
            self.log.emit(f"Error during execution: {str(e)}")
            self.finished_signal.emit()

    def stop(self):
        self.is_running = False