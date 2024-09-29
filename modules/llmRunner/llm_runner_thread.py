import os
import json
import time
import logging

# Disable all loggin messages
logging.disable(logging.WARNING)

import pandas as pd
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from cryptography.fernet import Fernet
from typing import List, Dict, Any
import ast
import csv
import sys

# Step 1: Increase the field size limit to handle large fields in the CSV file
max_int = sys.maxsize
try:
    csv.field_size_limit(max_int)
except OverflowError:
    # Fallback if sys.maxsize is too large
    csv.field_size_limit(2147483647)  # 2^31 - 1

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from modules.langchainManager.langchain_manager import *
from modules import *

# Configure logging
logging.basicConfig(
    filename='llm_runner.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

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

        # Load prompts
        with open(PROMPTS_STORAGE_PATH, 'r') as f:
            prompts_data = json.load(f)
            self.prompt = prompts_data[chain_config['prompt_name']]

        # Load model configurations
        with open(MODELS_STORAGE_PATH, 'r') as f:
            models_data = json.load(f)
            self.model_config = models_data[chain_config['model_name']]

        self.output_parser_type = chain_config['output_parser']

    def run(self):
        try:
            self.log.emit("Starting LLM Runner...")
            logging.info("LLM Runner started.")

            # Initialize prompt template
            prompt_template = self.initialize_prompt_template()

            # Initialize LLM model
            model = self.initialize_model()

            # Initialize output parser
            output_parser = self.initialize_output_parser()

            # Process CSV files
            csv_files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv')]
            total_files = len(csv_files)

            for idx, file_name in enumerate(csv_files, start=1):
                if not self.is_running:
                    self.log.emit("LLM Runner stopped.")
                    logging.info("LLM Runner stopped by user.")
                    break

                # input_path = os.path.join(self.input_dir, file_name)
                input_path = self.input_dir + '/' + file_name
                self.log.emit(f"Processing file: {input_path}")
                logging.info(f"Processing file: {input_path}")

                try:
                    # Read CSV in chunks
                    chunksize = self.batch_size  # Define chunk size
                    csv_iterator = pd.read_csv(
                        input_path,
                        chunksize=chunksize,
                        encoding='utf-8',
                        engine='python',  # Switch to Python engine
                        # on_bad_lines='skip'  # Skip lines with errors
                    )

                    # Count total rows
                    total_rows = 0
                    for chunk in pd.read_csv(input_path, chunksize=1000):
                        total_rows += chunk.shape[0]
                except Exception as e:
                    self.log.emit(f"Failed to read {input_path}: {str(e)}")
                    logging.error(f"Failed to read {input_path}: {str(e)}")
                    continue  # Skip to the next file

                chunk_number = 0
                processed_rows = 0
                for chunk in csv_iterator:
                    if not self.is_running:
                        self.log.emit("LLM Runner stopped.")
                        logging.info("LLM Runner stopped by user.")
                        break

                    self.log.emit(f"Processing rows {chunk_number * chunksize} to {(chunk_number + 1) * chunksize}")
                    logging.info(f"Processing rows {chunk_number * chunksize} to {(chunk_number + 1) * chunksize}")
                    chunk_number += 1

                    # Save processed results to output directory
                    output_file_name = os.path.splitext(file_name)[0] + f'_{chunk_number:05d}' + '_processed.csv'
                    output_path = os.path.join(self.output_dir, output_file_name)

                    # Check if the file already exists and pass the chunk
                    if os.path.exists(output_path):
                        self.log.emit(f"Skipped {output_path}. Already processed.")
                        continue
                    # Prepare messages for the batch
                    message_batch = self.prepare_message_batch(chunk, prompt_template)

                    # Process the batch with retries
                    results = self.process_batch_with_retries(model, output_parser, message_batch, retries=3)

                    # Update progress
                    processed_rows += len(chunk)
                    progress_percent = int((idx - 1) / total_files * 100 + (processed_rows / total_rows) / total_files * 100)
                    self.progress.emit(progress_percent)

                    # Save processed results to output directory
                    output_df = pd.DataFrame(results)
                    output_file_name = os.path.splitext(file_name)[0] + f'_{chunk_number:05}' + '_processed.csv'
                    output_path = os.path.join(self.output_dir, output_file_name)

                    try:
                        output_df.to_csv(output_path, index=False)
                        self.log.emit(f"Saved processed data to: {output_path}")
                        logging.info(f"Saved processed data to: {output_path}")
                    except Exception as e:
                        self.log.emit(f"Failed to save {output_path}: {str(e)}")
                        logging.error(f"Failed to save {output_path}: {str(e)}")

            self.log.emit("LLM Runner completed successfully.")
            logging.info("LLM Runner completed successfully.")
            self.finished_signal.emit()

        except Exception as e:
            self.log.emit(f"Critical error: {str(e)}")
            logging.exception(f"Critical error: {str(e)}")
            self.finished_signal.emit()

    def stop(self):
        self.is_running = False
        self.log.emit("Stopping LLM Runner...")
        logging.info("LLM Runner stopping...")

    def initialize_prompt_template(self) -> ChatPromptTemplate:
        system_prompt_template = self.prompt['system_prompt_template']
        user_prompt_template = self.prompt['user_prompt_template']
        prompt_keys = self.prompt['keys']
        prompt_template = ChatPromptTemplate.from_messages(
            [("system", system_prompt_template), ("user", user_prompt_template)]
        )
        return prompt_template

    def initialize_model(self) -> ChatOpenAI:
        llm_model = self.model_config['llm_model']
        model_type = self.model_config['type']
        api_key_name = self.model_config['api_key_name']

        # Load or generate the encryption key
        if not os.path.exists(SECRET_KEY_PATH):
            self.log.emit(f"Secret key not found at {SECRET_KEY_PATH}.")
            logging.error(f"Secret key not found at {SECRET_KEY_PATH}.")
            raise FileNotFoundError("Secret key file is missing.")
        else:
            with open(SECRET_KEY_PATH, "rb") as key_file:
                key = key_file.read()
        fernet = Fernet(key)

        # Load and decrypt API key
        try:
            with open(API_KEYS_STORAGE_PATH, 'r') as f:
                api_keys_data = json.load(f)
                encrypted_api_key = api_keys_data[api_key_name]['api_key']
            api_key = fernet.decrypt(encrypted_api_key.encode()).decode()
        except Exception as e:
            self.log.emit(f"Failed to load or decrypt API key: {str(e)}")
            logging.error(f"Failed to load or decrypt API key: {str(e)}")
            raise e

        # Initialize the model
        if llm_model == 'ChatGPT':
            try:
                model = ChatOpenAI(model=model_type, api_key=api_key)
                logging.info(f"Initialized ChatOpenAI model: {model_type}")
                return model
            except Exception as e:
                self.log.emit(f"Failed to initialize ChatOpenAI model: {str(e)}")
                logging.error(f"Failed to initialize ChatOpenAI model: {str(e)}")
                raise e
        else:
            self.log.emit(f"Model type '{llm_model}' not supported.")
            logging.error(f"Model type '{llm_model}' not supported.")
            raise NotImplementedError("Provided model type is not supported.")

    def initialize_output_parser(self) -> StrOutputParser:
        if self.output_parser_type == 'StrOutputParser':
            return StrOutputParser()
        else:
            self.log.emit(f"Output parser '{self.output_parser_type}' not supported.")
            logging.error(f"Output parser '{self.output_parser_type}' not supported.")
            raise NotImplementedError("Provided output parser type is not supported.")

    def prepare_message_batch(self, batch: pd.DataFrame, prompt_template: ChatPromptTemplate) -> List[List[Dict[str, str]]]:
        message_batch = []
        prompt_keys = self.prompt['keys']
        for _, row in batch.iterrows():
            # Create prompt for each row
            prompt_data = {key: str(row.get(key, '')) for key in prompt_keys}
            prompt = prompt_template.invoke(prompt_data)
            messages = prompt.to_messages()
            message_batch.append(messages)
        return message_batch

    def process_batch_with_retries(self, model: ChatOpenAI, parser: StrOutputParser, message_batch: List[List[Dict[str, str]]], retries: int = 3) -> List[Dict[str, Any]]:
        attempt = 0
        delay = 2  # Initial delay in seconds
        parsed_results = []

        while attempt < retries and self.is_running:
            try:
                # Process the batch through the model and parser
                chain = model | parser
                results = chain.batch(message_batch)  # Expected to return a list of JSON strings

                # Parse the results

                for i, result in enumerate(results):
                    try:
                        data_dict = ast.literal_eval(result)
                        parsed_results.append(data_dict)
                    except Exception as e:
                        logging.info(f"result: {result}")
                        logging.error(f"Response parsing error: {str(e)}")
                        logging.info(f"Retrying for the problematic data.")
                        self.log.emit(f"Retrying for the problematic data.")

                        # Retry the specific error twice more
                        specific_attempt = 0
                        while specific_attempt < retries and self.is_running:
                            re_result = chain.invoke(message_batch[i])
                            try:
                                specific_data_dict = ast.literal_eval(re_result)
                                parsed_results.append(specific_data_dict)
                                break
                            except Exception as e:
                                logging.info(f"result: {re_result}")
                                logging.error(f"Response parsing error: {str(e)}")
                                logging.info(f"Retrying for the problematic data {specific_attempt + 1} times.")
                                self.log.emit(f"Retrying for the problematic data {specific_attempt + 1} times.")
                            specific_attempt += 1
                        if specific_attempt >= retries:
                            logging.info(f"Failed to retrieve correct data format.")
                            self.log.emit(f"Failed to retrieve correct data format.")

                return parsed_results

            except Exception as e:
                attempt += 1
                self.log.emit(f"Batch processing failed on attempt {attempt}: {str(e)}")
                logging.warning(f"Batch processing failed on attempt {attempt}: {str(e)}")

                if "rate limit" in str(e).lower():
                    # Specific handling for rate limits
                    wait_time = delay * (2 ** (attempt - 1))
                    self.log.emit(f"Rate limit encountered. Waiting for {wait_time} seconds before retrying...")
                    logging.warning(f"Rate limit encountered. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                else:
                    # General exponential backoff
                    self.log.emit(f"Retrying in {delay} seconds...")
                    logging.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff

        self.log.emit("All retry attempts failed for the current batch.")
        logging.error("All retry attempts failed for the current batch.")
        return []

