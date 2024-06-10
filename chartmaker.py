import librosa
import json

# Load the audio file
audio_path = 'assets/music/tutorial.ogg'
y, sr = librosa.load(audio_path)

# Perform beat tracking
tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

# Convert beat frames to timestamps
beat_times = librosa.frames_to_time(beats, sr=sr)

# Generate chart data
chart_data = {
    "lines": [
        {
            "judgment_pos": [900, 600],
            "angle": 90,
            "key_binding": "a",
            "movement": [],
            "opacity_changes": [{"time": 0, "opacity": 50}, {"time": 2000, "opacity": 255}]
        },
        {
            "judgment_pos": [300, 600],
            "angle": 90,
            "key_binding": "s",
            "movement": [],
            "opacity_changes": [{"time": 1000, "opacity": 50}, {"time": 3000, "opacity": 255}]
        },
        {
            "judgment_pos": [500, 600],
            "angle": 90,
            "key_binding": "d",
            "movement": [],
            "opacity_changes": [{"time": 2000, "opacity": 50}, {"time": 4000, "opacity": 255}]
        },
        {
            "judgment_pos": [700, 600],
            "angle": 90,
            "key_binding": "f",
            "movement": [],
            "opacity_changes": [{"time": 3000, "opacity": 50}, {"time": 5000, "opacity": 255}]
        }
    ],
    "notes": [],
    "hold_notes": [],
    "audio_path": "assets/music/tutorial.ogg"
}

# Assign notes to lines based on beat times
for i, beat_time in enumerate(beat_times):
    # Convert beat time to milliseconds
    beat_time_ms = int(beat_time * 1000)
    note = {
        "line": i % 4,  # Cycle through lines
        "hit_time": beat_time_ms,
        "speed": 10
    }
    chart_data["notes"].append(note)

# Add a sample hold note (adjust the timing as needed)
hold_note = {
    "line": 3,
    "hit_time": int(beat_times[10] * 1000),  # Start time of the hold note
    "end_time": int(beat_times[20] * 1000),  # End time of the hold note
    "type": "blue",
    "speed": 10,
    "checkpoints": [int(beat_times[i] * 1000) for i in range(11, 20)]  # Checkpoints for the hold note
}
chart_data["hold_notes"].append(hold_note)

# Save chart data to a JSON file
with open('chart.json', 'w') as json_file:
    json.dump(chart_data, json_file, indent=4)
