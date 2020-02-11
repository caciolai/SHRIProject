import pyttsx3
import os


WIN_EN = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"


class Speaker:
    """
    A class that simply speaks sentences through the computer speakers
    """
    def __init__(self, rate=0, pitch=0, volume=0, spd=False):
        """
        Constructor
        :param rate: rate of the voice
        :param pitch: pitch of the voice
        :param volume: volume of the voice
        :param spd: if set, use ubuntu spd-say instead of pyttsx3
        """

        self._spd = spd
        self._rate = rate
        self._pitch = pitch
        self._volume = volume

        if not self._spd:
            self._engine = pyttsx3.init()
            self._engine.setProperty('rate', rate)
            self._engine.setProperty('pitch', float(pitch))
            self._engine.setProperty('volume', float(volume))

            if os.name == "nt":
                self._engine.setProperty("voice", WIN_EN)
            else:
                self._engine.setProperty("voice", "english")

    def speak(self, sentence):
        """
        Speaks the given sentence through the computer speakers
        :param sentence: sentence
        :return: None
        """

        if self._spd:
            self._speak_spd(sentence)
        else:
            self._speak_pyttsx3(sentence)

    def _speak_spd(self, sentence):
        """
        Speaks the given sentence through the computer speakers using spd (on Linux)
        :param sentence: sentence
        :return: None
        """
        assert os.name == "posix"
        os.system(
            "spd-say \"{}\" "
            "--rate {} "
            "--pitch {} "
            "--volume {}".format(
                sentence,
                self._rate,
                self._pitch,
                self._volume
            )
        )

    def _speak_pyttsx3(self, sentence):
        """
        Speaks the given sentence through the computer speakers using pyttsx3
        :param sentence: sentence
        :return: None
        """
        self._engine.say(sentence)
        self._engine.runAndWait()