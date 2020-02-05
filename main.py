import os
import speech_recognition as sr

from texttable import Texttable

def text_from_speech(recognizer, microphone):
    """
    Transcribe speech from recording from `microphone`
    :param recognizer: recognizer wrapper
    :param microphone: microphone wrapper
    :return: a dictionary with three keys:
        "success": a boolean indicating whether or not the API request was
                   successful
        "error":   `None` if no error occured, otherwise a string containing
                   an error message if the API could not be reached or
                   speech was unrecognizable
        "transcription": `None` if speech could not be transcribed,
                   otherwise a string containing the transcribed text
    """
    # check that recognizer and microphone arguments are appropriate type
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    # adjust the recognizer sensitivity to ambient noise and record audio
    # from the microphone
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source) # #  analyze the audio source for 1 second
        audio = recognizer.listen(source)

    # set up the response object
    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    # try recognizing the speech in the recording
    # if a RequestError or UnknownValueError exception is caught,
    #   update the response object accordingly
    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API was unreachable or unresponsive
        response["success"] = False
        response["error"] = "API unavailable/unresponsive"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


def text_to_speech(text, spd=False, rate=-50, pitch=0, volume=0):
    if spd:
        os.system("spd-say "
                  "--rate {} "
                  "--pitch {} "
                  "--volume {} "
                  "\"{}\"".format(rate, pitch, volume, text))
    else:
        os.system("say \"{}\"".format(text))


if __name__ == '__main__':
    rec = sr.Recognizer()
    mic = sr.Microphone()
    print("\nSetup done. Say something now...")
    res = text_from_speech(rec, mic)
    success, error, transcription = res["success"], res["error"], res["transcription"]
    t = Texttable()
    t.add_rows([["Key", "Value"],
                ["Success", success],
                ["Error", error],
                ["Transcription", transcription]])
    print(t.draw())

    if transcription is not None:
        text_to_speech(transcription)