import sys
import os
import pygame
import json


# Add the src directory to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import load_config
from game import Game
from score import Score


def load_chart(chart_path):
    with open(chart_path, 'r') as file:
        return json.load(file)

# Load configuration
config = load_config('config/config.json')

import sys
import os
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, QStackedWidget
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt

class ChartDisplay(QWidget):
    def __init__(self, chart_data, parent=None):
        super().__init__(parent)
        self.chart_data = chart_data
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Illustration
        illustration_path = self.chart_data['illustration_path']
        pixmap = QPixmap(illustration_path)
        self.illustration_label = QLabel(self)
        self.illustration_label.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio))
        layout.addWidget(self.illustration_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Chart Name
        self.name_label = QLabel(self.chart_data['name'], self)
        self.name_label.setFont(QFont('Arial', 14))
        layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # Highest Score
        self.score_label = QLabel(f"Highest Score: {self.chart_data['previous_highscore']}", self)
        self.score_label.setFont(QFont('Arial', 12))
        layout.addWidget(self.score_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

class ChartPicker(QMainWindow):
    def __init__(self, charts_folder):
        super().__init__()
        self.charts_folder = charts_folder
        self.charts_data = self.load_charts_data()
        self.current_index = 0
        self.autoplay = False
        self.initUI()

    def load_charts_data(self):
        charts_data = []
        for filename in os.listdir(self.charts_folder):
            if filename.endswith('.json'):
                with open(os.path.join(self.charts_folder, filename), 'r') as file:
                    chart_data = json.load(file)
                    chart_data['filename'] = filename  # Add filename to chart data
                    charts_data.append(chart_data)
        return charts_data

    def initUI(self):
        self.setWindowTitle('Chart Picker')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()

        self.focus_display = ChartDisplay(self.charts_data[self.current_index], self)
        main_layout.addWidget(self.focus_display, alignment=Qt.AlignmentFlag.AlignCenter)

        nav_layout = QHBoxLayout()

        prev_button = QPushButton('Previous')
        prev_button.clicked.connect(self.show_previous_chart)
        nav_layout.addWidget(prev_button)

        next_button = QPushButton('Next')
        next_button.clicked.connect(self.show_next_chart)
        nav_layout.addWidget(next_button)

        self.chart_info_label = QLabel(self.get_chart_info_text())
        main_layout.addWidget(self.chart_info_label, alignment=Qt.AlignmentFlag.AlignCenter)

        main_layout.addLayout(nav_layout)

        autoplay_toggle = QPushButton('Toggle Autoplay')
        autoplay_toggle.setCheckable(True)
        autoplay_toggle.toggled.connect(self.toggle_autoplay)
        main_layout.addWidget(autoplay_toggle)

        play_button = QPushButton('Play')
        play_button.clicked.connect(self.play_chart)
        main_layout.addWidget(play_button)

        widget = QWidget()
        widget.setLayout(main_layout)
        self.setCentralWidget(widget)

    def get_chart_info_text(self):
        return f"Chart {self.current_index + 1} of {len(self.charts_data)}"

    def update_chart_info(self):
        self.chart_info_label.setText(self.get_chart_info_text())

    def show_previous_chart(self):
        self.current_index = (self.current_index - 1) % len(self.charts_data)
        self.update_chart_info()
        self.initUI()

    def show_next_chart(self):
        self.current_index = (self.current_index + 1) % len(self.charts_data)
        self.update_chart_info()
        self.initUI()
    
    def toggle_autoplay(self, checked):
        self.autoplay = checked

    def play_chart(self):
        chart_path = os.path.join(self.charts_folder, self.charts_data[self.current_index]['filename'])
        
        # Load configuration
        config = load_config('config/config.json')

        # Initialize Pygame 
        pygame.init()
        screen = pygame.display.set_mode((config['screen_width'], config['screen_height']), pygame.NOFRAME)

        # Initialize and run the game
        game = Game(screen, chart_path, config, self.autoplay)
        score = game.run()
        self.show_score(screen, score, chart_path, config)


    def update_focus_display(self):
        self.focus_display.chart_data = self.charts_data[self.current_index]
        self.initUI()

    def show_score(self, screen, score, chart_path, config):
        chart = load_chart(chart_path)
        screen_width, screen_height = config['screen_width'], config['screen_height']
        screen = pygame.display.set_mode((screen_width, screen_height))
        illustration_path = chart['illustration_path']
        background_path = config['score_image']

        font = pygame.font.Font('assets/fonts/exo-regular.ttf', 36)
        currscore_font = pygame.font.Font('assets/fonts/exo-light.ttf', 74)
        prevscore_font = pygame.font.Font('assets/fonts/exo-regular.ttf', 24)
        addedscore_font = pygame.font.Font('assets/fonts/exo-regular.ttf', 24)

        # Colors
        background = pygame.image.load(background_path)
        background = pygame.transform.scale(background, (config['screen_width'], config['screen_height']))

        text_color = (0, 0, 0)  # Green text
        score_color = (255,255,255)

        # Load illustration and scale it
        illustration = pygame.image.load(illustration_path)
        illustration = pygame.transform.scale(illustration, (360, 360))

        scoreval = int(score.score)
        prevscore = chart['previous_highscore']
        addedscore = scoreval - prevscore

        # Main loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            
            screen.blit(background, (0, 0))

            # Draw the illustration
            screen.blit(illustration, (216, 77))

            # Rank and score information
            ranks = config['rank_paths']
            if score.score >= 10000000:
                rank_label_path = ranks['Pure_Memory']
            elif score.score >= 92000000:
                rank_label_path = ranks['S']
            elif score.score >= 82000000:
                rank_label_path = ranks['A']
            elif score.score >= 65000000:
                rank_label_path = ranks['B']
            else:
                rank_label_path = ranks['F']

            rank_label = pygame.image.load(rank_label_path)
            rank_label = pygame.transform.scale(rank_label, (452, 360))
            screen.blit(rank_label, (216, 524))


            res_background_path = config['result_bg']
            res_background = rank_label = pygame.image.load(res_background_path)
            res_background = pygame.transform.scale(res_background, (595, 293))
            screen.blit(res_background, (818, 171))

            formatted_score = f"{scoreval:08d}"  # Ensure score is at least 8 digits with leading zeros
            # Add apostrophes as thousands separators
            parts = [formatted_score[max(i - 3, 0):i] for i in range(len(formatted_score), 0, -3)]
            formatted_score_with_apostrophes = "'".join(reversed(parts))
            score_text = currscore_font.render(f"{formatted_score_with_apostrophes}", True, (score_color))
            screen.blit(score_text, (900, 180))

            formatted_score = f"{prevscore:08d}"  # Ensure score is at least 8 digits with leading zeros
            # Add apostrophes as thousands separators
            parts = [formatted_score[max(i - 3, 0):i] for i in range(len(formatted_score), 0, -3)]
            formatted_score_with_apostrophes = "'".join(reversed(parts))
            score_text = prevscore_font.render(f"{formatted_score_with_apostrophes}", True, (score_color))
            screen.blit(score_text, (1070, 287))

            if addedscore > 0:
                formatted_score = f"{addedscore}"  # Ensure score is at least 8 digits with leading zeros
                # Add apostrophes as thousands separators
                parts = [formatted_score[max(i - 3, 0):i] for i in range(len(formatted_score), 0, -3)]
                formatted_score_with_apostrophes = "'".join(reversed(parts))
                score_text = addedscore_font.render(f" +{formatted_score_with_apostrophes}", True, score_color)
                screen.blit(score_text, (1200, 287))

                if not self.autoplay:
                    chart['previous_highscore'] = scoreval
                    with open(chart_path, 'w') as file:
                        json.dump(chart, file, indent=4)

            # Pure, Far, and Lost count
            pure_count_label = font.render("Pure", True, text_color)
            pure_count_value = font.render(f"{score.pure_cnt+score.extra_pure_cnt} + {score.extra_pure_cnt}", True, text_color)
            screen.blit(pure_count_label, (900, 600))
            screen.blit(pure_count_value, (1000, 600))

            far_count_label = font.render("Far", True, text_color)
            far_count_value = font.render(f"{score.far_cnt}", True, text_color)
            screen.blit(far_count_label, (900, 650))
            screen.blit(far_count_value, (1000, 650))

            lost_count_label = font.render("bad", True, text_color)
            lost_count_value = font.render(f"{score.bad_cnt}", True, text_color)
            screen.blit(lost_count_label, (900, 700))
            screen.blit(lost_count_value, (1000, 700))

            lost_count_label = font.render("miss", True, text_color)
            lost_count_value = font.render(f"{score.miss_cnt}", True, text_color)
            screen.blit(lost_count_label, (900, 750))
            screen.blit(lost_count_value, (1000, 750))

            pygame.display.flip()
        
        pygame.quit()


def main():
    app = QApplication(sys.argv)
    charts_folder = 'assets/charts'  # Replace with the path to your charts folder
    window = ChartPicker(charts_folder)
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()



# Initialize Pygame 
screen = pygame.display.set_mode((config['screen_width'], config['screen_height']), pygame.NOFRAME)

pygame.init()

#game = Game(screen, chart_path, config, 0) 
#score = game.run()

#score = Score(chart, None)

#show_score(screen, score, chart, config)

pygame.quit()
sys.exit()
