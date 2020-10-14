# SHRIProject

This is the project of the *Spoken Human Robot Interaction* (SHRI) module of the course in Articial Intelligence
(A.Y. 2019/2020). 
The goal of the project has been the implementation of a task-oriented Spoken Dialouge System (SDS), 
and it is a very simple *waiter bot*, able to take an order according to a modifiable menu.

## Getting started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

The project is built with Python3. Open a terminal and input the following commands to install the needed libraries.

*Note*: check that the system's default Python is Python3, otherwise install Python3 and `pip3` and replace `pip` with `pip3` in the following commands.

- Google Speech Recognition library, spaCy, pyttsx3:
```
pip3 install spacy SpeechRecognition pyttsx3
```

- Other libraries for formatting purposes:
```
pip3 install colorama termcolor texttable nltk
```

### Installing

Clone this repo, then get the English model for spaCy with
```
python -m spacy download en_core_web_sm
```

*Note*: Again, you may need to replace `python` with `python3`.

### Usage

Launch the bot with 
```
python main.py
``` 

Different options are available, check them out with
```
python main.py --help
```

## Documentation

Read the project report [here](report.pdf) for a more detailed documentation of the project.

## Built with

- [Google Speech Recognition library](https://pypi.org/project/SpeechRecognition/) - For speech-to-text and ASR
- [spaCy](https://spacy.io/usage) - For NLP
- [pyttsx3](https://pypi.org/project/pyttsx3/) - For text-to-speech.

## Authors
- **Andrea Caciolai** - *Main work*
