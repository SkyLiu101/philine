import math

def lerp(start, end, t):
    return start + t * (end - start)

class SmoothMovement:
    def __init__(self, positions):
        self.positions = positions
        self.current_index = 0
        self.start_time = positions[0]['time']
        self.end_time = positions[1]['time']
        self.start_pos = positions[0]['new_pos']
        self.start_angle = positions[0]['new_angle']
        self.end_pos = positions[1]['new_pos']
        self.end_angle = positions[1]['new_angle']

    def update(self, current_time):
        if self.current_index < len(self.positions) - 1:
            if current_time >= self.end_time:
                self.current_index += 1
                if self.current_index < len(self.positions) - 1:
                    self.start_time = self.positions[self.current_index]['time']
                    self.end_time = self.positions[self.current_index + 1]['time']
                    self.start_pos = self.positions[self.current_index]['new_pos']
                    self.start_angle = self.positions[self.current_index]['new_angle']
                    self.end_pos = self.positions[self.current_index + 1]['new_pos']
                    self.end_angle = self.positions[self.current_index + 1]['new_angle']
            t = (current_time - self.start_time) / (self.end_time - self.start_time)
            new_pos = [lerp(self.start_pos[0], self.end_pos[0], t), lerp(self.start_pos[1], self.end_pos[1], t)]
            new_angle = lerp(self.start_angle, self.end_angle, t)
            return new_pos, new_angle
        else:
            return self.end_pos, self.end_angle

def calculate_line_positions(judgment_pos, angle, length=300):
    rad_angle = math.radians(angle)
    x_offset = length * math.cos(rad_angle)
    y_offset = length * math.sin(rad_angle)
    start_pos = [judgment_pos[0] - x_offset, judgment_pos[1] - y_offset]
    end_pos = [judgment_pos[0], judgment_pos[1]]
    return start_pos, end_pos
