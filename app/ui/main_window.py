from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QApplication,
    QScrollArea,
    QLabel,
    QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, QObject, Signal, QThread
from file_handling.file_open import open_file
from search.filename_search import search_files
from pathlib import Path
from search import loader
from PySide6.QtGui import QIcon

# ----- Worker for threaded search -----
class SearchWorker(QObject):
    finished = Signal(list)

    def __init__(self, text):
        super().__init__()
        self.text = text

    def run(self):
        results = search_files(self.text)
        self.finished.emit(results)


class MainWindow(QWidget):
    ROW_HEIGHT = 30
    MAX_VISIBLE = 5

    def __init__(self):
        super().__init__()

        # ---- window flags ----
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)

        self.base_width = 600

        # ---- global background ----
        self.setStyleSheet("""
            QWidget {
                background-color: #202020;
            }
        """)

        # ---- main layout ----
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(24, 18, 24, 18)
        self.main_layout.setSpacing(6)

        # ---- search row ----
        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        search_row.setContentsMargins(0, 0, 0, 0)

        # ---- input ----
        self.input = QLineEdit()
        self.input.setPlaceholderText("Search files...")
        self.input.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 16px;
            }
        """)
        search_row.addWidget(self.input, stretch=1)

        # ---- filter button ----
        self.filter_btn = QPushButton()
        project_root = Path(__file__).parent.parent  # File_Search/
        filter_icon_path = project_root / "icons" / "filter.png"
        self.filter_btn.setIcon(QIcon(str(filter_icon_path)))  # path to icon
        self.filter_btn.setFixedSize(28, 28)
        self.filter_btn.setStyleSheet("""
            QPushButton {
                background: #4A4A4A;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.10);
                border-radius: 6px;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """)
        search_row.addWidget(self.filter_btn)

        # ---- settings button ----
        self.settings_btn = QPushButton()
        setting_icon_path = project_root / "icons" / "settings.png"
        self.settings_btn.setIcon(QIcon(str(setting_icon_path)))
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: #4A4A4A;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.10);
                border-radius: 6px;
            }
            QPushButton:pressed {
                background-color: #616161;
            }
        """)
        search_row.addWidget(self.settings_btn)

        # ---- add row to main layout ----
        self.main_layout.addLayout(search_row)


        # ---- scroll area ----
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll.hide()

        self.scroll.setStyleSheet("""
            QScrollArea { border: none; }
            QScrollBar:vertical { width: 6px; background: transparent; }
            QScrollBar::handle:vertical { background: rgba(255,255,255,0.35); border-radius:3px; }
            QScrollBar::add-line, QScrollBar::sub-line { height:0px; }
        """)

        # ---- results container ----
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(6)

        self.scroll.setWidget(self.results_widget)
        self.main_layout.addWidget(self.scroll)

        # ---- timer for debouncing ----
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)

        self.input.textChanged.connect(lambda _: self.search_timer.start(200))  # debounce

        # ---- initial size ----
        self.update_window_size(0)
        self.input.setFocus()

        # ---- thread holder ----
        self.thread = None
        self.worker = None

    # ---------------- search ----------------
    def perform_search(self):
        text = self.input.text().strip()
        if not text:
            self.clear_results()
            self.scroll.hide()
            self.update_window_size(0)
            return

        # ---- start threaded search ----
        self.thread = QThread()
        self.worker = SearchWorker(text)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_results)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    # ---------------- display results ----------------
    def display_results(self, results):
        self.clear_results()

        if not results:
            self.scroll.hide()
            self.update_window_size(0)
            return

        HOME = str(Path.home())  # for compacting paths

        for path in results:
            p = Path(path)
            filename = p.name

            # Compact parent path
            parent_path = str(p.parent)
            if parent_path.startswith(HOME):
                parent_path = "~" + parent_path[len(HOME):]

            # ---- Container widget for a single result ----
            result_widget = QWidget()
            result_layout = QVBoxLayout(result_widget)
            result_layout.setContentsMargins(6, 0, 6, 0)
            result_layout.setSpacing(0)

            # ---- Filename label ----
            filename_label = QLabel(filename)
            filename_label.setStyleSheet("color: white; font-size: 16px;")
            result_layout.addWidget(filename_label)

            # ---- Path label (smaller, faded) ----
            path_label = QLabel(parent_path)
            path_label.setStyleSheet("color: rgba(255,255,255,0.5); font-size: 12px;")
            result_layout.addWidget(path_label)

            # ---- Wrap in a clickable button ----
            btn = QPushButton()
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.12);
                    border-radius: 6px;
                }
            """)
            # Actual row height = filename + path + spacing
            btn.setFixedHeight(self.ROW_HEIGHT + 18 + 6)  # 18 = path label, 6 = spacing
            btn.setLayout(result_layout)
            btn.clicked.connect(lambda _, p=path: open_file(p))

            self.results_layout.addWidget(btn)

        self.scroll.show()

        # Calculate scroll height for up to MAX_VISIBLE results
        visible = min(len(results), self.MAX_VISIBLE)
        self.scroll.setFixedHeight(visible * (self.ROW_HEIGHT + 18 + 6) +
                                (visible - 1) * self.results_layout.spacing())

        self.update_window_size(len(results))


    # ---------------- update window size ----------------
    def update_window_size(self, result_count):
        input_h = self.input.sizeHint().height()
        margin = 18 * 2

        if result_count == 0:
            height = margin + input_h + 4
        else:
            visible = min(result_count, self.MAX_VISIBLE)
            results_h = visible * (self.ROW_HEIGHT + 18 + 6) + (visible - 1) * self.results_layout.spacing()
            self.scroll.setFixedHeight(results_h)
            height = margin + input_h + results_h + 6

        self.setFixedWidth(self.base_width)
        self.resize(self.base_width, height)
        self.adjustSize()


    def clear_results(self):
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

  
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            QApplication.quit()
