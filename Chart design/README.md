#Manual for chartmaker.py

##1: perform pipeline install of pyqt6 and pygame (pip/pip3)
    - pip install pyqt6
    - pip install pygame

##2: open chartmaker.py with python/python3
    - cd your/path/philine
    - python chartmaker.py
    
##3: import base chart, song and illustratio

WARNING: Duplicate a base chart file before you preceed!n 

chart files stored in charts/
song files stored in assets/music
illustration files stored in assets/illustration

##4: Enter bpm

WARNING: proceed further steps without entering a Bpm would crash the tool

Bpm of the song could be found online by googling 'songname+arcaea+bpm' 
if the result says there are changes of bpm along the song, change a song as this function is not supported right yet.

##5: Navigate along the timeline. 

Choose a fraction rate from 1-32. This could be changed at any time and all notes will be auto gridded to the fraction rate.

    - directly enter the object time in the box and click left or right arrow
    - use the left and right arrow to navigate and auto grid according to the current fraction rate
    - scroll on the UI screen

##6: Visualize lines and edit notes

Click visualize lines.
left click on grid to add notes, shift left click a start and a end to add hold notes, right click to delete notes.

##7: click save chart to save the changes

##8: click play to preview from the current timespot

WARNING: This must proceed after save chart is clicked.



