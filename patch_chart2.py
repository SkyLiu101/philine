import json

def replace_note_type(chart_path):
    with open(chart_path, 'r') as file:
        chart_data = json.load(file)

    # Iterate through notes and hold_notes to replace type for line 4 and 5
    for note in chart_data['notes']:
        if note['line'] in [2]:
            note['type'] = 'orange'

    for hold_note in chart_data['hold_notes']:
        if hold_note['line'] in [2]:
            hold_note['type'] = 'orange'

    # Save the updated chart data back to the file
    with open(chart_path, 'w') as file:
        json.dump(chart_data, file, indent=4)

# Path to your chart JSON file
chart_path = 'assets/charts/ringedgenesis.json'
replace_note_type(chart_path)
