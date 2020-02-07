import os
from datetime import  datetime
import json


class KB:
    """
    A class that represents what the bot knows
    """
    def __init__(self):
        self.kb = {
            "menu": []
        }


