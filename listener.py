import speech_recognition as sr

class Listener:
    """
    A class which serves as an interface between the speaking user and the ASR service

    Attributes
    ----------
    _microphone:
        object to record audio from the microphone
    _recognizer:
        object to recognize speech from audio (ASR)
    """
    def __init__(self, mic_index=0):
        """
        Constructor
        :param mic_index: the index of the microphone device to listen from
        """
        self._microphone = sr.Microphone(device_index=mic_index)
        self._recognizer = sr.Recognizer()

    def listen(self):
        """
        Listens from the microphone then tries to recognize text from the recorded audio fragment
        via the Google's ASR API
        :return: a dictionary with three keys:
            "success": a boolean indicating whether or not the API request was
                       successful
            "error":   `None` if no error occured, otherwise the exception caught
            "transcription": `None` if speech could not be transcribed,
                       otherwise a string containing the transcribed text
        """

        # adjust the recognizer sensitivity to ambient noise and record audio from the microphone
        with self._microphone as source:
            self._recognizer.adjust_for_ambient_noise(source)
            # print("* listening *")
            audio = self._recognizer.listen(source)

        # set up the response object
        response = {
            "success": True,
            "error": None,
            "sentence": None
        }

        # try recognizing the speech in the recording
        try:
            response["sentence"] = self._recognizer.recognize_google(audio).lower().strip()
        except sr.RequestError as err:
            # API was unreachable or unresponsive
            response["success"] = False
            response["error"] = err
        except sr.UnknownValueError as err:
            # speech was unintelligible
            response["success"] = False
            response["error"] = err

        return response

