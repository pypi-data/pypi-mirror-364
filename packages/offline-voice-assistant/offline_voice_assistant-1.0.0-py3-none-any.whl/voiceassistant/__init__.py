import sys
import os
import requests
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit,
    QLabel, QSlider, QComboBox, QFileDialog, QMessageBox, QHBoxLayout
)
from PyQt5.QtCore import Qt
from TTS.api import TTS
import tempfile
import subprocess

# Initialize TTS
tts = TTS("tts_models/en/vctk/vits", gpu=False)
speakers = tts.speakers

class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline Voice Assistant")
        self.setGeometry(300, 200, 550, 500)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("🔤 Text Input (Highest Priority):"))
        self.text_input = QTextEdit()
        self.text_input.setFixedHeight(120)
        layout.addWidget(self.text_input)

        layout.addWidget(QLabel("🌐 URL to Scrape:"))
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.file_label = QLabel("📄 No file selected.")
        self.file_button = QPushButton("Choose Text File")
        self.file_button.clicked.connect(self.pick_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_button)
        file_layout.addWidget(self.file_label)
        layout.addLayout(file_layout)

        layout.addWidget(QLabel("🎙 Select Speaker:"))
        self.speaker_dropdown = QComboBox()
        self.speaker_dropdown.addItems(speakers)
        layout.addWidget(self.speaker_dropdown)

        layout.addWidget(QLabel("⏩ Speed (%):"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(50)
        self.speed_slider.setMaximum(200)
        self.speed_slider.setValue(100)
        layout.addWidget(self.speed_slider)

        # Buttons
        button_layout = QHBoxLayout()

        self.play_button = QPushButton("🗣 Play Voice")
        self.play_button.clicked.connect(self.play_speech)
        button_layout.addWidget(self.play_button)

        self.save_button = QPushButton("💾 Save to File")
        self.save_button.clicked.connect(self.save_speech)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.file_path = None

    def pick_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "", "Text Files (*.txt)")
        if file_path:
            self.file_path = file_path
            self.file_label.setText(os.path.basename(file_path))
        else:
            self.file_label.setText("📄 No file selected.")
            self.file_path = None

    def extract_text_from_url(self, url):
        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            return " ".join([p.get_text() for p in paragraphs])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch URL:\n{e}")
            return ""

    def read_text_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reading file:\n{e}")
            return ""

    def get_input_text(self):
        text = self.text_input.toPlainText().strip()

        if not text:
            url = self.url_input.text().strip()
            if url:
                text = self.extract_text_from_url(url)
            elif self.file_path:
                text = self.read_text_file(self.file_path)

        return text

    def play_speech(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "No Input", "Please provide text, URL, or file.")
            return

        selected_speaker = self.speaker_dropdown.currentText()
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                temp_path = f.name
                tts.tts_to_file(
                    text=text,
                    speaker=selected_speaker,
                    file_path=temp_path,
                )
            subprocess.run(["aplay", temp_path])
        except Exception as e:
            QMessageBox.critical(self, "TTS Error", f"Speech synthesis failed:\n{e}")

    def save_speech(self):
        text = self.get_input_text()
        if not text:
            QMessageBox.warning(self, "No Input", "Please provide text, URL, or file.")
            return

        selected_speaker = self.speaker_dropdown.currentText()
        save_path, _ = QFileDialog.getSaveFileName(self, "Save Audio File", "", "WAV Files (*.wav)")
        if not save_path:
            return

        if not save_path.endswith(".wav"):
            save_path += ".wav"

        try:
            tts.tts_to_file(
                text=text,
                speaker=selected_speaker,
                file_path=save_path,
            )
            QMessageBox.information(self, "Saved", f"Audio saved to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "TTS Error", f"Saving speech failed:\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceAssistant()
    window.show()
    sys.exit(app.exec_())

