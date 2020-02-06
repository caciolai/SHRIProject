import speech_recognition as sr

class Listener:
    """
    A class which serves as an interface between the speaking user and the ASR service
    """
    def __init__(self, language="en", mic_index=0):
        """
        Constructor
        :param language: desired language (ISO code)
        """
        self.microphone = sr.Microphone(device_index=mic_index)
        self.recognizer = sr.Recognizer()
        self.language = language

    def listen(self):
        """
        Listens for commands from the user and returns the transcript once it is properly
        understood by Google's ASR API
        :return: the command from the user
        :rtype: str
        """
        res = self._listen()
        while not res["success"]:
            print("ERROR: {}".format(res["error"]))
            print("Please say that again.")
            res = self._listen()

        return res["command"]

    def _listen(self):
        """
        Listens from the microphone then tries to recognize text from the recorded audio fragment
        via the Google's ASR API
        :return: a dictionary with three keys:
            "success": a boolean indicating whether or not the API request was
                       successful
            "error":   `None` if no error occured, otherwise a string containing
                       an error message if the API could not be reached or
                       speech was unrecognizable
            "transcription": `None` if speech could not be transcribed,
                       otherwise a string containing the transcribed text
        """

        # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            print("* listening *")
            audio = self.recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "command": None
        }

        # try recognizing the speech in the recording
        try:
            response["command"] = self.recognizer.recognize_google(audio, language=self.language)
        except sr.RequestError:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            # speech was unintelligible
            response["success"] = False
            response["error"] = "Unable to recognize speech"

        return response

