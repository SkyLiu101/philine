import librosa
import numpy as np

# 读取音频文件
y, sr = librosa.load('/Users/skyliu/Documents/philine/assets/music/testify.ogg', sr=None)

# 提取音频的频率
onset_env = librosa.onset.onset_strength(y=y, sr=sr)
times = librosa.times_like(onset_env, sr=sr)
pitches, magnitudes = librosa.core.piptrack(y=y, sr=sr)

# 只保留最大强度的频率
frequencies = []
for t in range(pitches.shape[1]):
    index = magnitudes[:, t].argmax()
    pitch = pitches[index, t]
    if pitch > 0:
        frequencies.append(pitch)

# 简化频率数据
frequencies = frequencies [::50]

# 生成Arduino代码
num_notes = len(frequencies)
melody_lines = []
for i in range(num_notes):
    melody_lines.append(f"  melody[{i}] = {int(frequencies[i])};")

arduino_code = f"""
int a = 11;
int melody[{num_notes}];

void setup() {{
    pinMode(a, OUTPUT);
    // 初始化melody数组
{chr(10).join(melody_lines)}
}}

void loop() {{
    for (int thisNote = 0; thisNote < {num_notes}; thisNote++) {{
        tone(a, melody[thisNote]);
        delay(500);
    }}
}}
"""

# 保存Arduino代码到文件
with open("testifyfull.ino", "w") as f:
    f.write(arduino_code)

print("Arduino code generated in melody.ino")
