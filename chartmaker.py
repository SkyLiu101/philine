from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QLineEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QDoubleValidator, QPainter, QPen, QBrush
import os
import pygame
import threading
import sys
import json

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from config import load_config
from game import Game

config = load_config('config/config.json')

def save_chart(file_path, chart_data):
    with open(file_path, 'w') as file:
        json.dump(chart_data, file, indent=4)

def load_chart(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

class SharedState:
    def __init__(self):
        self.current_time = 0
        self.is_paused = True

class VisualizationWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Line Visualization')
        self.setGeometry(300, 100, 600, 600)
        self.lines = []
        self.current_time = 0
        self.bpm = 120  # Default BPM, will be updated
        self.fraction = 1
        self.hold_start = None
        self.chart = None

    def update_visualization(self, lines, current_time, bpm, fraction, chart):
        self.lines = lines
        self.current_time = current_time
        self.bpm = bpm
        self.fraction = fraction/4
        self.update()
        self.chart = chart

    def paintEvent(self, event):
        painter = QPainter(self)

        # Fixed grid spacing
        beat_spacing = 200  # pixels per beat
        ms_per_beat = 60000 / self.bpm  # milliseconds per beat

        # Calculate the total number of beats to display
        total_height = self.height() - 100
        total_beats = int(total_height / beat_spacing) + 1

        # Calculate the total number of grid lines to display
        total_grid_lines = total_beats * self.fraction
        grid_spacing = beat_spacing / self.fraction

        # Draw beat lines
        painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        for i in range(total_beats + 1):
            y_pos = int(50 + i * beat_spacing - (self.current_time % ms_per_beat) / ms_per_beat * beat_spacing)
            if y_pos < 50:
                continue
            past_beat = self.current_time // ms_per_beat
            painter.drawLine(50, self.height() - y_pos, self.width() - 20, self.height() - y_pos)
            painter.drawText(10, self.height() - y_pos, f'{i+past_beat}')

        # Draw grid lines
        painter.setPen(QPen(Qt.GlobalColor.green, 1, Qt.PenStyle.SolidLine))
        for i in range(int(total_grid_lines) + 1):
            y_pos = int(50 + i * grid_spacing - (self.current_time % (ms_per_beat / self.fraction)) / (ms_per_beat / self.fraction) * grid_spacing)
            if y_pos < 50:
                continue
            painter.drawLine(80, self.height() - y_pos, self.width() - 50, self.height() - y_pos)

        # Draw lines vertically
        for idx, line in enumerate(self.lines):
            x_pos = 100 + idx * 50
            y_start = 0
            y_end = self.height() - 50
            painter.drawLine(x_pos, y_start, x_pos, y_end)

            # Draw key bindings
            key_bindings = line['key_binding']
            key_text = ", ".join(key_bindings)
            painter.drawText(x_pos - 10, self.height() - 30, key_text)


            # Draw hold notes
            for hold_note in self.chart['hold_notes']:
                if hold_note['line'] == idx:
                    start_time = hold_note['hit_time']
                    end_time = hold_note['end_time']
                    y_start = int(self.height() - 50 - ((start_time - self.current_time) / ms_per_beat) * beat_spacing)
                    y_end = int(self.height() - 50 - ((end_time - self.current_time) / ms_per_beat) * beat_spacing)
                    painter.setBrush(Qt.GlobalColor.blue)
                    painter.drawRect(x_pos-5, y_end, 10, y_start-y_end)
                    painter.drawText(x_pos - 10, y_start - 10, str(start_time))
                    painter.drawText(x_pos - 10, y_end - 10, str(end_time))

            # Draw notes
            for note in self.chart['notes']:
                if note['line'] == idx:
                    note_time = note['hit_time']
                    y_pos = int(self.height() - 50 - ((note_time - self.current_time) / ms_per_beat) * beat_spacing)
                    painter.setBrush(Qt.GlobalColor.white)
                    painter.drawEllipse(x_pos - 5, y_pos - 5, 10, 10)
                    painter.drawText(x_pos - 10, y_pos - 10, str(note_time))

    def mousePressEvent(self, event):
        x = event.position().x()
        y = event.position().y()

        # Calculate the time based on the y position
        beat_spacing = 200  # pixels per beat
        ms_per_beat = 60000 / self.bpm  # milliseconds per beat
        y_relative = self.height() - y
        
        # Adjust y_relative to consider the offset within the current beat
        y_relative_adjusted = self.current_time + y_relative*ms_per_beat/beat_spacing - 75

        # Find the closest grid line y position
        grid_spacing = ms_per_beat / self.fraction
        closest_grid_line = round(y_relative_adjusted / grid_spacing) * grid_spacing

        for idx, line in enumerate(self.lines):

            x_pos = 100 + idx * 50
            if x_pos - 10 <= x <= x_pos + 10:
                note_time = int(y_relative_adjusted)
                if event.button() == Qt.MouseButton.RightButton:
                    # Check if there is a note at the objective time and remove it
                    self.chart['notes'] = [note for note in self.chart['notes'] if not (note['line'] == idx and abs(note['hit_time'] - note_time) < 5*ms_per_beat/200)]
                    self.chart['hold_notes'] = [hold_note for hold_note in self.chart['hold_notes'] if not (hold_note['line'] == idx and (hold_note['hit_time'] <= note_time <= hold_note['end_time']))]

                    self.update()
                    break

        if abs(y_relative_adjusted - closest_grid_line) > 20:
            return

        # Determine which line was clicked
        for idx, line in enumerate(self.lines):
            x_pos = 100 + idx * 50
            
            if x_pos - 10 <= x <= x_pos + 10:

                # Calculate the note time
                note_time = int(closest_grid_line)

                # Add the note to the chart
                note_exists = any(note['line'] == idx and note['hit_time'] == note_time for note in self.chart['notes'])

                if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                    if self.hold_start is None:
                        self.hold_start = (idx, note_time)
                    else:
                        hold_end = (idx, note_time)
                        self.hold_start, hold_end = min(self.hold_start, hold_end), max(self.hold_start, hold_end)

                        checkpoints = []
                        checkpoints.append({'time': self.hold_start})
                        current_checkpoint = self.hold_start[1] + ms_per_beat
                        while current_checkpoint < hold_end[1]:
                            checkpoints.append({'time': current_checkpoint})
                            current_checkpoint += ms_per_beat

                        # Check for intersection with existing hold notes
                        for hold_note in self.chart['hold_notes']:
                            if hold_note['line'] == idx:
                                existing_start = hold_note['hit_time']
                                existing_end = hold_note['end_time']
                                if not (hold_end[1] <= existing_start or self.hold_start[1] >= existing_end):
                                    self.hold_start = None
                                    break
                        if not self.hold_start:
                            continue
                        if self.hold_start[0] == hold_end[0] and self.hold_start[1] != hold_end[1]:
                            self.chart['hold_notes'].append({
                                'line': idx,
                                'hit_time': min(self.hold_start[1], hold_end[1]),
                                'end_time': max(self.hold_start[1], hold_end[1]),
                                'type': "blue",
                                'speed': 10,
                                'checkpoints': checkpoints  # Add empty checkpoints or you can define your logic
                            })
                        self.hold_start = None

                elif event.button() == Qt.MouseButton.LeftButton:
                    # Check if a note already exists at the objective time
                    note_exists = any(note['line'] == idx and note['hit_time'] == note_time for note in self.chart['notes'])

                    if not note_exists:
                        # Add the note to the chart
                        self.chart['notes'].append({
                            'line': idx,
                            'hit_time': note_time,
                            'speed': 10
                        })
                self.update()
                break







class GameWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.game_screen = pygame.display.set_mode((config['screen_width'], config['screen_height']))
        self.game = None

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
        self.illustration_path = None
        self.bpm = 120
        self.offset = 0
        self.timer = QTimer(self)
        self.update_timer = QTimer(self)
        self.is_paused = True
        self.fraction = 4
        self.multiplier = 1
        self.current_time = 0
        self.game_window = GameWindow()
        self.visualization_window = VisualizationWindow(self)
        self.update_timer.timeout.connect(self.update_current_time)
        self.chart_path = None
        self.chart = None
        
        self.setMouseTracking(True)
        self.installEventFilter(self)


    def initUI(self):
        self.setWindowTitle('Chart Designer')
        self.setGeometry(100, 100, 800, 150)

        main_layout = QVBoxLayout()

        file_layout = QHBoxLayout()

        self.load_button = QPushButton('Load Chart')
        self.load_button.clicked.connect(self.load_chart_file)
        file_layout.addWidget(self.load_button)

        self.import_button = QPushButton('Load Song')
        self.import_button.clicked.connect(self.import_song)
        file_layout.addWidget(self.import_button)

        self.load_button = QPushButton('Load Illustration')
        self.load_button.clicked.connect(self.import_illustration)
        file_layout.addWidget(self.load_button)

        self.save_button = QPushButton('Save Chart')
        self.save_button.clicked.connect(self.save_chart)
        file_layout.addWidget(self.save_button)

        parameter_layout = QHBoxLayout()

        self.bpm_input = QLineEdit('')
        self.bpm_input.setValidator(QDoubleValidator(0.00, 999.99, 2))
        self.bpm_input.setPlaceholderText('Enter BPM')
        parameter_layout.addWidget(self.bpm_input)

        self.offset_input = QLineEdit('')
        self.offset_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        self.offset_input.setPlaceholderText('Enter Offset (ms)')
        parameter_layout.addWidget(self.offset_input)

        self.note_fraction_input = QLineEdit('')
        self.note_fraction_input.setValidator(QDoubleValidator(1, 32, 0))
        self.note_fraction_input.setPlaceholderText('Enter Increment Fraction from 1 to 32(e.g., 4 for 1/4)')
        parameter_layout.addWidget(self.note_fraction_input)

        self.current_time_input = QLineEdit('')
        self.current_time_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        parameter_layout.addWidget(self.current_time_input)

        control_layout = QHBoxLayout()

        self.backward_button = QPushButton('<<')
        self.backward_button.clicked.connect(self.move_backward)
        control_layout.addWidget(self.backward_button)

        self.play_pause_button = QPushButton('Play')
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        control_layout.addWidget(self.play_pause_button)

        self.visualize_button = QPushButton('Visualize Lines')
        self.visualize_button.clicked.connect(self.visualize_lines)
        control_layout.addWidget(self.visualize_button)

        self.forward_button = QPushButton('>>')
        self.forward_button.clicked.connect(self.move_forward)
        control_layout.addWidget(self.forward_button)

        main_layout.addLayout(file_layout)
        main_layout.addLayout(parameter_layout)
        main_layout.addLayout(control_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
    
    def save_chart(self):
        with open(self.chart_path, 'w') as file:
            json.dump(self.chart, file, indent=4)
        self.load_chart()

    def load_chart(self):
        with open(self.chart_path, 'r') as file:
            self.chart = json.load(file)
        self.update_visualization()
    
    def load_chart_file(self):
        self.chart_path, _ = QFileDialog.getOpenFileName(self, 'Load/Create Chart File', '', 'JSON Files (*.json)')
        if self.chart_path:
            with open(self.chart_path, 'r') as file:
                self.chart = json.load(file)
        self.load_chart()

    def import_song(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Song File', '', 'Audio Files (*.ogg *.mp3 *.wav)')
        if file_path:
            self.song_path = file_path
            self.load_song(file_path)

    def import_illustration(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open illustraion File', '', 'Picture Files (*.jpg *.png)')
        if file_path:
            self.illustration_path = file_path
            self.chart['illustration_path'] = file_path
    
    def load_song(self, file_path):
        pygame.mixer.music.load(file_path)
        self.song_loaded = True
        self.current_time_input.setText('0')
        self.chart['audio_path'] = file_path

    def update_current_time(self):
        if not self.is_paused:
            self.current_time = self.game_window.game.get_current_time() * 1000  # Update current time in milliseconds
            self.current_time_input.setText(f'{self.current_time:.2f}')
            self.update_visualization()

    def update_information(self):
        try:
            self.bpm = float(self.bpm_input.text())
        except ValueError:
            self.bpm = 120
        try:
            self.offset = float(self.offset_input.text())
        except ValueError:
            self.offset = 0
        try:
            self.fraction = int(self.note_fraction_input.text())
            self.multiplier = 4 / self.fraction
        except ValueError:
            self.multiplier = 1  # Default to 1/4

    def eventFilter(self, source, event):
        if event.type() == QEvent.Type.Wheel:
            delta = event.angleDelta().y()
            self.current_time -= delta
            if self.current_time < 0:
                self.current_time = 0
            self.current_time_input.setText(f'{self.current_time:.2f}')
            self.update_visualization()
            self.update()
            return True
        return super().eventFilter(source, event)

    def toggle_play_pause(self):
        self.update_information()
        if self.song_loaded:
            start_pos = (self.current_time - self.offset)
            if self.is_paused:
                self.update_timer.start()
                self.timer.start(int(start_pos))
                self.play_pause_button.setText('Pause')
                self.game_window.game = Game(self.game_window.game_screen, self.chart_path, config, start_pos/1000.0)
                self.is_paused = False
                self.game_window.game.run()
                threading.Thread(target=self.game_window.game.run).start()
            else:
                self.is_paused = True
                self.timer.stop()
                self.play_pause_button.setText('Play')
                self.game_window.game.pause()
        self.update_visualization()

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
        self.update_visualization()

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
        self.update_visualization()

    def snap_to_grid(self, value, grid_size):
        return round(value / grid_size) * grid_size

    def visualize_lines(self):
        self.visualization_window.show()
        self.update_visualization()
    
    def update_visualization(self):
        self.update_information()
        self.visualization_window.update_visualization(
            self.chart['lines'], self.current_time, self.bpm, self.fraction, self.chart
        )

pygame.init()
app = QApplication(sys.argv)
window = ChartDesigner()
window.show()
gameWindow = GameWindow()
sys.exit(app.exec())
