import pygame

class Score:
    def __init__(self, chart, play_hit_sound_call_back):
        self.chart = chart
        self.total_notes = self.calculate_total_notes()
        self.max_score = 10000000
        self.score = 0
        self.score_per_note = self.max_score / self.total_notes
        self.extra_pure_bonus = 1
        self.far_penalty = 0.65
        self.play_hit_sound_call_back = play_hit_sound_call_back
        self.extra_pure_cnt=0
        self.pure_cnt=0
        self.far_cnt=0
        self.bad_cnt=0
        self.miss_cnt=0

    def calculate_total_notes(self):
        total_notes = 0
        total_notes += len(self.chart['notes'])
        if 'hold_notes' not in self.chart:
            return total_notes
        for hold_note in self.chart['hold_notes']:
            print(self.chart)
            total_notes +=  len(hold_note['checkpoints'])
        return total_notes

    def update_score(self, judgment):
        if judgment == 'pure':
            self.score += self.score_per_note
            self.play_hit_sound_call_back()
            self.pure_cnt += 1
        elif judgment == 'far':
            self.score += self.score_per_note * self.far_penalty
            self.play_hit_sound_call_back()
            self.far_cnt += 1
        elif judgment == 'extra_pure':
            self.score += self.score_per_note + self.extra_pure_bonus
            self.play_hit_sound_call_back()
            self.extra_pure_cnt += 1
        elif judgment == 'bad':
            self.bad_cnt += 1
        elif judgment == 'miss':
            self.miss_cnt += 1
            

    def get_score(self):
        return int(self.score)
