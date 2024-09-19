# main_window.py
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QWidget, QVBoxLayout
from PyQt6.QtGui import QIcon, QAction
from modules.langchainManager.langchain_manager import *
from modules.llmRunner.llm_runner import *
from modules.promptManager.prompt_manager import *
from modules.redditZstDecompressor.reddit_zst_decompressor_widget import *
from modules.textViewer.text_view import *
from modules.modelManager.model_manager import *
from modules.apiKeyManagement.api_key_management import *
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Data Processing Program")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon('resources/icons/app_icon.png'))  # Set your app icon

        # Initialize UI components
        # self.init_menu()
        self.init_toolbar()
        self.init_tabs()
        self.init_status_bar()

    def init_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Help Menu
        help_menu = menubar.addMenu('Help')

        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def init_toolbar(self):
        toolbar = self.addToolBar('MainToolbar')

        # open_icon = QIcon('resources/icons/open.png')
        # open_action = QAction(open_icon, 'Open', self)
        # open_action.setShortcut('Ctrl+O')
        # open_action.triggered.connect(self.open_file)
        # toolbar.addAction(open_action)
        #
        # save_icon = QIcon('resources/icons/save.png')
        # save_action = QAction(save_icon, 'Save', self)
        # save_action.setShortcut('Ctrl+S')
        # save_action.triggered.connect(self.save_file)
        # toolbar.addAction(save_action)

        # Add Refresh Button
        refresh_icon = QIcon('resources/icons/refresh.png')  # Ensure you have a refresh icon
        refresh_action = QAction(refresh_icon, 'Refresh', self)
        refresh_action.setShortcut('F5')
        refresh_action.triggered.connect(self.refresh_app)
        toolbar.addAction(refresh_action)

    def init_tabs(self):
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Initialize modules
        # self.decompressor = DecompressorWidget()
        # self.text_viewer = TextViewerWidget()
        self.prompt_manager = PromptManagerWidget()
        self.langchain_manager = LangchainManagerWidget()
        self.llm_runner = LLMRunnerWidget()
        self.model_manager = ModelManagerWidget()
        self.api_key_management = ApiKeyManagerWidget()

        # Add modules as tabs
        # self.tab_widget.addTab(self.decompressor, "Decompressor")
        # self.tab_widget.addTab(self.text_viewer, "Text Viewer")
        self.tab_widget.addTab(self.prompt_manager, "Prompt Manager")
        self.tab_widget.addTab(self.model_manager, "Model Manager")
        self.tab_widget.addTab(self.langchain_manager, "Langchain Manager")
        self.tab_widget.addTab(self.llm_runner, "LLM Runner")
        self.tab_widget.addTab(self.api_key_management, "API Key Manager")

    def init_status_bar(self):
        self.status = self.statusBar()
        self.status.showMessage("Ready")

    def open_file(self):
        options = QFileDialog.Option.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;", options=options)
        if file_path:
            self.status.showMessage(f"Opened file: {file_path}")
            # Implement file handling logic based on active tab
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, DecompressorWidget):
                current_tab.dir_path.setText(file_path)
            elif isinstance(current_tab, TextViewerWidget):
                current_tab.load_file(file_path)
            # Add similar conditions for other modules if necessary

    def save_file(self):
        options = QFileDialog.Option.ShowDirsOnly
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv);;All Files (*)",
                                                   options=options)
        if save_path:
            self.status.showMessage(f"Saved file: {save_path}")
            # Implement save logic based on active tab
            current_tab = self.tab_widget.currentWidget()
            if isinstance(current_tab, DecompressorWidget):
                # Maybe save decompression settings or logs
                pass
            elif isinstance(current_tab, TextViewerWidget):
                # Implement save functionality for text viewer if applicable
                pass
            # Add similar conditions for other modules if necessary

    def show_about(self):
        QMessageBox.about(self, "About Data Processing Program",
                          "Data Processing Program\nVersion 1.0\nDeveloped with PyQt6")

    def refresh_app(self):
        self.status.showMessage("Restarting application...")
        QApplication.instance().quit()  # Quit the current application

        # Restart the application
        python = sys.executable
        os.execl(python, python, *sys.argv)