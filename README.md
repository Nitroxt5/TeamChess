# TeamChess

This repository contains a TeamChess game. It is a swedish variation of chess, 
which you can play against an AI with the help of this program. 

It is a part of my graduate work in Belarusian State University.

### Description

------------

 - ScoreBoard and TestDLL are libraries written in C++. They contain helper functions for AI and move generating.
 - Images and Sound folders contain all the multimedia required.
 - SETTINGS.json is for saving settings.
 - Utils folder contains entities for logging, multimedia handling and more.
 - UI folder contains menus and widget classes for their construction.
 - Generators folder includes generators for moves, threat tables and more.
 - Engine folder contains classes for keeping game state in computer memory.
 - AI folder contains AI to play with or against.

### Running the code

------------

 - You must have Python 3.9+ installed
 - Clone the repository
 - (Optional) Set up a virtual environment
 - Install poetry with: *pip install poetry*
 - Install all the dependencies with: *poetry install*
 - Run the code with: *python -OO main.py*