import pygame

class Score:
    def __init__(self, chart):
        self.chart = chart
        self.total_notes = self.calculate_total_notes()
        self.max_score = 10000000
        self.score = 0
        self.score_per_note = self.max_score / self.total_notes
        self.extra_pure_bonus = 1
        self.far_penalty = 0.65

    def calculate_total_notes(self):
        total_notes = 0
        total_notes += len(self.chart['notes'])
        for hold_note in self.chart['hold_notes']:
            total_notes += len(hold_note['checkpoints'])
        return total_notes

    def update_score(self, judgment):
        if judgment == 'pure':
            self.score += self.score_per_note
        elif judgment == 'far':
            self.score += self.score_per_note * self.far_penalty
        elif judgment == 'extra_pure':
            self.score += self.score_per_note + self.extra_pure_bonus

    def get_score(self):
        return int(self.score)
