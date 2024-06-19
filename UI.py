from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QComboBox, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDoubleValidator, QPainter, QColor, QPen

import os
import pygame
import threading
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config import load_config
from game import Game

config = load_config('config/config.json')
chart = load_config('charts/chart.json')

class SharedState:
    def __init__(self):
        self.current_time = 0
        self.is_paused = True

class VisualizationWindow(QMainWindow):
    def __init__(self, lines, fraction_rate, bpm, current_time):
        super().__init__()
        self.lines = lines
        self.fraction_rate = fraction_rate
        self.bpm = bpm
        self.current_time = current_time
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Line Visualization')
        self.setGeometry(200, 100, 1000, 800)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Fixed grid spacing
        beat_spacing = 200  # pixels per beat
        ms_per_beat = 60000 / self.bpm  # milliseconds per beat
        total_height = self.height() - 100
        total_beats = int(total_height / beat_spacing) + 1

        total_grid_lines = total_beats * self.fraction_rate
        grid_spacing = 200 / self.fraction_rate

        # Draw beat lines
        painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        for i in range(total_beats + 1):
            y_pos = int(50 + i * beat_spacing + 200 * (self.current_time % ms_per_beat)/ms_per_beat )
            painter.drawLine(50, self.height() - y_pos, self.width() - 20, self.height() - y_pos)
            ms_time = i * ms_per_beat + (self.current_time//ms_per_beat) * ms_per_beat
            if self.current_time % self.bpm != 0:
                ms_time += self.bpm
            painter.drawText(10, self.height() - y_pos, f'{ms_time:.0f} ms')

        # Draw grid lines
        painter.setPen(QPen(Qt.GlobalColor.green, 1, Qt.PenStyle.SolidLine))
        for i in range(int(total_grid_lines) + 1):
            y_pos = int(50 + i * grid_spacing)
            painter.drawLine(80, self.height() - y_pos, self.width() - 50, self.height() - y_pos)

        # Draw lines vertically
        for idx, line in enumerate(self.lines):
            x_pos = 100 + idx * 100
            y_start = 50
            y_end = self.height() - 50
            painter.drawLine(x_pos, y_start, x_pos, y_end)

            # Draw key bindings
            key_bindings = line['key_binding']
            key_text = ", ".join(key_bindings)
            painter.drawText(x_pos - 10, self.height() - y_start + 20, key_text)




class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.game_screen = pygame.display.set_mode((config['screen_width'], config['screen_height']))
        self.game = Game(self.game_screen, 'charts/tutorial.json', config, 0)

    def initUI(self):
        self.setWindowTitle('Game Window')
        self.setGeometry(900, 100, 800, 600)

    def start_game(self, timestamp):
        self.timestamp = timestamp
        self.running = True
        self.run_game()
        self.game.resume()

    def pause_game(self):
        self.running = False
        self.game.pause()

class ChartDesigner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

        pygame.mixer.init()
        self.song_loaded = False
        self.song_path = None
        self.bpm = 0
        self.offset = 0
        self.timer = QTimer(self)
        self.is_paused = True
        self.fraction = 4
        self.multiplier = 1
        self.current_time = 0
        self.game_window = GameWindow()


    def initUI(self):
        self.setWindowTitle('Chart Designer')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        self.import_button = QPushButton('Import Song')
        self.import_button.clicked.connect(self.import_song)
        main_layout.addWidget(self.import_button)

        self.bpm_input = QLineEdit('')
        self.bpm_input.setValidator(QDoubleValidator(0.00, 999.99, 2))
        self.bpm_input.setPlaceholderText('Enter BPM')
        main_layout.addWidget(self.bpm_input)

        self.offset_input = QLineEdit('')
        self.offset_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.offset_input.setPlaceholderText('Enter Offset (ms)')
        main_layout.addWidget(self.offset_input)

        self.note_fraction_input = QLineEdit('')
        self.note_fraction_input.setValidator(QDoubleValidator(1, 32, 0))
        self.note_fraction_input.setPlaceholderText('Enter Increment Fraction from 1 to 32(e.g., 4 for 1/4)')
        main_layout.addWidget(self.note_fraction_input)

        self.current_time_input = QLineEdit('')
        self.current_time_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        main_layout.addWidget(self.current_time_input)

        control_layout = QHBoxLayout()

        self.backward_button = QPushButton('<<')
        self.backward_button.clicked.connect(self.move_backward)
        control_layout.addWidget(self.backward_button)

        self.play_pause_button = QPushButton('Play')
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        control_layout.addWidget(self.play_pause_button)

        self.forward_button = QPushButton('>>')
        self.forward_button.clicked.connect(self.move_forward)
        control_layout.addWidget(self.forward_button)

        self.visualize_button = QPushButton('Visualize Lines')
        self.visualize_button.clicked.connect(self.visualize_lines)
        main_layout.addWidget(self.visualize_button)

        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def import_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Song File', '', 'Audio Files (*.ogg *.mp3 *.wav)')
        if file_path:
            self.song_path = file_path
            self.load_song(file_path)

    def load_song(self, file_path):
        pygame.mixer.music.load(file_path)
        self.song_loaded = True
        self.current_time_input.setText('0')

    def update_information(self):
        try:
            self.bpm = float(self.bpm_input.text())
        except ValueError:
            self.bpm = 0
        try:
            self.offset = float(self.offset_input.text())
        except ValueError:
            self.offset = 0
        try:
            self.fraction = int(self.note_fraction_input.text())
            self.multiplier = 4 / self.fraction
        except ValueError:
            self.multiplier = 1  # Default to 1/4

    def toggle_play_pause(self):
        self.update_information()
        if self.song_loaded:
            start_pos = (self.current_time - self.offset) / 1000.0
            if self.is_paused == True:
                self.is_paused = False
                self.timer.start(self.current_time)
                self.play_pause_button.setText('Pause')
                self.game_window.game = Game(self.game_window.game_screen, 'charts/tutorial.json', config ,self.current_time/1000.0)
                self.game_window.game.run()
            else:
                self.is_paused = True
                self.timer.stop()
                self.play_pause_button.setText('Play')
                self.game_window.game.pause()

    def move_forward(self):
        self.update_information()
        if self.bpm == 0:
            return
        increment = (60 / self.bpm) * self.multiplier * 1000  # convert to milliseconds
        try:
            current_value = float(self.current_time_input.text().strip('[]'))
        except ValueError:
            current_value = 0
        max_length = float(pygame.mixer.Sound(self.song_path).get_length()) * 1000
        new_value = current_value + increment
        self.current_time = int(min(max_length, self.snap_to_grid(new_value, increment)))
        self.current_time_input.setText(f'{self.current_time:.2f}')

    def move_backward(self):
        self.update_information()
        if self.bpm == 0:
            return
        decrement = (60 / self.bpm) * self.multiplier * 1000  # convert to milliseconds
        try:
            current_value = float(self.current_time_input.text().strip('[]'))
        except ValueError:
            current_value = 0
        new_value = current_value - decrement
        self.current_time = int(max(0, self.snap_to_grid(new_value, decrement)))
        self.current_time_input.setText(f'{self.current_time:.2f}')

    def snap_to_grid(self, value, grid_size):
        return round(value / grid_size) * grid_size

    def visualize_lines(self):
        self.update_information()
        lines = chart['lines']
        fraction_rate = self.fraction / 4 
        self.visualization_window = VisualizationWindow(lines, fraction_rate, self.bpm, self.current_time)
        self.visualization_window.show()

pygame.init()
app = QApplication(sys.argv)
window = ChartDesigner()
window.show()
gameWindow = GameWindow()
sys.exit(app.exec())
