import json

def patch_chart(chart_path):
    with open(chart_path, 'r') as file:
        chart = json.load(file)

    for hold_note in chart.get('hold_notes', []):
        # Add start_time to each checkpoint
        if hold_note['checkpoints']:
            hold_note['checkpoints'][0] = {"time": hold_note['hit_time']}
        else:
            hold_note['checkpoints'].append({"time": hold_note['hit_time']})
        hold_note['speed'] = hold_note['speed']*3/4

    with open(chart_path, 'w') as file:
        json.dump(chart, file, indent=4)

# Example usage
patch_chart('charts/testify.json')
