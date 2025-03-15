import speech_recognition as sr


def record_and_recognize(time_record=10):
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Говорите что-нибудь на русском языке...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.record(source, duration=time_record)
        print("Запись завершена, обрабатываю...")

    try:
        text = recognizer.recognize_google(audio, language="ru-RU")
        print("Вы сказали:", text)
        return text
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return None
    except sr.RequestError as e:
        print(f"Ошибка сервиса распознавания: {e}")
        return None
