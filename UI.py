from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QDoubleValidator

import os
import pygame
import threading
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config import load_config
from game import Game

config = load_config('config/config.json')

class SharedState:
    def __init__(self):
        self.current_time = 0
        self.is_paused = True

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

pygame.init()
app = QApplication(sys.argv)
window = ChartDesigner()
window.show()
gameWindow = GameWindow()
gameWindow.show()
sys.exit(app.exec())
