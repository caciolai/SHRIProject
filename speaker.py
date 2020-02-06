import pyttsx3
import os

class Speaker:
    """
    A class that simply speaks sentences through the computer speakers
    """
    def __init__(self, language, rate=0, pitch=0, volume=0, spd=False):
        """
        Constructor
        :param language: language of the speaker
        :param rate: rate of the voice
        :param pitch: pitch of the voice
        :param volume: volume of the voice
        :param spd: if set, use ubuntu spd-say instead of pyttsx3
        """

        self.spd = spd
        self.language = language
        self.rate = rate
        self.pitch = pitch
        self.volume = volume

        if not self.spd:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('pitch', float(pitch))
            self.engine.setProperty('volume', float(volume))

            if language == "en":
                self.engine.setProperty("voice", "english")
            elif language == "it":
                self.engine.setProperty("voice", "italian")

    def speak(self, sentence):
        """
        Speaks the given sentence through the computer speakers
        :param sentence: sentence
        :return: None
        """

        if self.spd:
            self.speak_spd(sentence)
        else:
            self.speak_pyttsx3(sentence)


    def speak_spd(self, sentence):
        os.system(
            "spd-say \"{}\" "
            "--language {} "
            "--rate {} "
            "--pitch {} "
            "--volume {}".format(
                sentence,
                self.language,
                self.rate,
                self.pitch,
                self.volume
            )
        )

    def speak_pyttsx3(self, sentence):
        """
        Speaks the given sentence through the computer speakers using pyttsx3
        :param sentence: sentence
        :return: None
        """
        self.engine.say(sentence)
        self.engine.runAndWait()