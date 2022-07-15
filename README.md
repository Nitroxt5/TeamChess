# TeamChess

This repository contains a TeamChess game. It is a part of my graduate work in Belarusian State University.

### Description

------------

 - ScoreBoard and TestDLL are libraries written in C++. They contain helper functions for AI and move generating.
 - Images and Sound folders contain all the multimedia required.
 - lang_ru.py and lang_eu.py files contain localization.
 - SETTINGS.json is for saving settings.
 - Utils.py contains helper functions for creating UI and logging.
 - UI.py contains classes which are widgets. They are used in UI constructing.
 - Main.py contains methods that create UI and handle events. It is an entry point of the game.
 - Engine.py contains classes for validating moves and tracking game state.
 - AIpy.py contains AI to play with or against.

### Running the code

------------

 - You must have Python 3.9+ installed
 - Clone the repository
 - (Optional) Set up a virtual environment
 - Install poetry with: *pip install poetry*
 - Install all the dependencies with: *poetry install*
 - Run the code with: *python -OO main.py*