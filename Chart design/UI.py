from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QComboBox, QVBoxLayout, QWidget
import sys
import librosa

def detect_bpm(file_path):
    y, sr = librosa.load(file_path)
    tempo, _ = librosa.beat.beat_track(y, sr=sr)
    return tempo

class ChartDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Chart Designer')
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        self.import_button = QPushButton('Import Song')
        self.import_button.clicked.connect(self.import_song)
        layout.addWidget(self.import_button)

        self.bpm_label = QLabel('BPM:')
        layout.addWidget(self.bpm_label)

        self.note_fraction_combo = QComboBox()
        self.note_fraction_combo.addItems(['1/4', '1/8', '1/16', '1/24'])
        layout.addWidget(self.note_fraction_combo)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def import_song(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Song File', '', 'Audio Files (*.ogg *.mp3 *.wav)', options=options)
        if file_path:
            bpm = detect_bpm(file_path)
            self.bpm_label.setText(f'BPM: {bpm}')

app = QApplication(sys.argv)
window = ChartDesigner()
window.show()
sys.exit(app.exec_())
