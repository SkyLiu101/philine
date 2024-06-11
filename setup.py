from setuptools import setup
import os

def find_data_files(source, target):
    results = []
    for root, _, files in os.walk(source):
        for file in files:
            source_path = os.path.join(root, file)
            target_path = os.path.join(target, os.path.relpath(root, source))
            results.append((target_path, [source_path]))
    return results

# Include all assets and source files in the build
assets = find_data_files('assets', 'assets')
src_files = find_data_files('src', 'src')
chart_files = find_data_files('charts', 'charts')
config_files = find_data_files('config', 'config')

# Additional files to include
additional_files = assets + src_files + chart_files + config_files

OPTIONS = {
    'argv_emulation': True,
    'packages': ['pygame'],
    'includes': ['encodings'],
}

setup(
    app=['main.py'],
    data_files=additional_files,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
