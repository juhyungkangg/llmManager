from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QProgressBar, QHBoxLayout, QSpinBox, QLineEdit, QApplication
)
import zstandard as zstd
import pandas as pd
from tqdm import tqdm
import os
from json import JSONDecoder


class DecompressorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Input Directory Selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel("Select Input Directory:")
        self.input_path = QLineEdit()
        self.input_path.setText('/Users/juhyung/Desktop/data/original/reddit/subreddits23/')
        self.input_browse_button = QPushButton("Browse")
        self.input_browse_button.clicked.connect(self.browse_input_dir)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_path)
        input_layout.addWidget(self.input_browse_button)

        # Output Directory Selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Select Output Directory:")
        self.output_path = QLineEdit()
        self.output_path.setText('/Users/juhyung/Desktop/data/processed/reddit')
        self.output_browse_button = QPushButton("Browse")
        self.output_browse_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_browse_button)

        # Chunk Size
        chunk_layout = QHBoxLayout()
        self.chunk_label = QLabel("Chunk Size (MB):")
        self.chunk_size = QSpinBox()
        self.chunk_size.setRange(1, 1000)
        self.chunk_size.setValue(60)
        chunk_layout.addWidget(self.chunk_label)
        chunk_layout.addWidget(self.chunk_size)

        # Start Button and Progress Bar
        action_layout = QHBoxLayout()
        self.start_button = QPushButton("Start Decompression")
        self.start_button.clicked.connect(self.start_decompression)
        self.progress_bar = QProgressBar()
        action_layout.addWidget(self.start_button)
        action_layout.addWidget(self.progress_bar)

        # Log/Output
        self.log_label = QLabel("Status: Waiting to start.")

        # Add all layouts to main layout
        layout.addLayout(input_layout)
        layout.addLayout(output_layout)
        layout.addLayout(chunk_layout)
        layout.addLayout(action_layout)
        layout.addWidget(self.log_label)

        self.setLayout(layout)
        self.setWindowTitle("ZST Decompressor")

    def browse_input_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if dir_path:
            self.input_path.setText(dir_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_path.setText(dir_path)

    def separate_json_objects(self, text, decoder=JSONDecoder()):
        pos = 0
        json_li = []
        while True:
            match = text.find('{', pos)
            if match == -1:
                break
            try:
                result, index = decoder.raw_decode(text[match:])
                json_li.append(result)
                pos = match + index
            except ValueError:
                pos = match + 1

        remainder = text[pos - 1:]

        return json_li, remainder

    def zst_to_df(self, from_path, data_type, to_path_parent, chunksize):
        j = 0

        # Set columns
        if data_type == 'submission':
            cols = ['subreddit', 'title', 'selftext', 'created_utc', 'score', 'num_comments', 'id']
        elif data_type == 'comment':
            cols = ['body', 'created_utc', 'score', 'subreddit', 'link_id']

        with open(from_path, 'rb') as fh:
            dctx = zstd.ZstdDecompressor()
            reader = dctx.stream_reader(fh)

            while True:
                chunk = reader.read(chunksize)
                if not chunk:
                    break
                j += 1

        with open(from_path, 'rb') as fh:
            dctx = zstd.ZstdDecompressor()
            reader = dctx.stream_reader(fh)
            complete_jsons, incomplete_json = "", ""
            i = 1

            if not os.path.exists(os.path.join(to_path_parent, data_type)):
                os.makedirs(os.path.join(to_path_parent, data_type))

            for _ in tqdm(range(j), desc=f"Decompressing {os.path.basename(from_path)}"):
                chunk = reader.read(chunksize).decode('utf-8', errors='ignore')
                file_name = os.path.splitext(os.path.basename(from_path))[0]
                to_path = os.path.join(
                    to_path_parent,
                    data_type,
                    f"{file_name}_{i:06d}.csv"
                )

                if os.path.exists(to_path):
                    i += 1
                    continue

                if not chunk:
                    break

                if incomplete_json:
                    chunk = incomplete_json + chunk
                    incomplete_json = ""

                complete_jsons, incomplete_json = self.separate_json_objects(chunk)

                data_list = complete_jsons

                if data_list:
                    df = pd.DataFrame(data_list)
                    try:
                        df = df[cols]
                    except KeyError:
                        # Column mismatch. Skip this chunk.
                        continue

                    df = df.replace("", None).dropna(how='all')

                    df.to_csv(to_path, index=False)
                    i += 1


    def start_decompression(self):
        input_dir = self.input_path.text()
        output_dir = self.output_path.text()
        chunk_mb = self.chunk_size.value()
        data_type = ""

        if not input_dir:
            self.log_label.setText("Status: Please select an input directory.")
            return

        if not output_dir:
            self.log_label.setText("Status: Please select an output directory.")
            return

        # Convert chunk size from MB to bytes
        chunksize = chunk_mb * 1024 * 1024

        # Find all .zst files in input directory
        zst_files = [
            os.path.join(input_dir, f)
            for f in os.listdir(input_dir)
            if f.lower().endswith('.zst') and os.path.isfile(os.path.join(input_dir, f))
        ]

        if not zst_files:
            self.log_label.setText("Status: No .zst files found in the input directory.")
            return

        total_files = len(zst_files)
        self.progress_bar.setMaximum(total_files)
        self.progress_bar.setValue(0)

        self.log_label.setText("Status: Starting decompression...")
        QApplication.processEvents()

        for zst_file in zst_files:
            try:
                title = os.path.basename(zst_file)
                self.log_label.setText(f"Status: Working on {title}")
                self.log_label.repaint()
                QApplication.processEvents()

                # Set data type
                if 'submission' in title:
                    data_type = 'submission'
                elif 'comment' in title:
                    data_type = 'comment'

                # Run by zst file
                self.zst_to_df(zst_file, data_type, output_dir, chunksize)

                self.progress_bar.setValue(total_files)
                self.log_label.setText("Status: Decompression completed successfully.")
            except Exception as e:
                self.log_label.setText(f"Status: An error occurred - {str(e)}")
                print(f"Error during decompression: {e}")

        QApplication.processEvents()
