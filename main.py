import requests
import json
import pyttsx3
import speech_recognition as sr
import pyaudio
from io import BytesIO
from PIL import Image

# Инициализация голосового модуля
engine = pyttsx3.init()

# Функция для произношения текста голосом
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Функция для распознавания ключевого слова из голосового сообщения
def recognize_speech():
    r = sr.Recognizer()

    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
    try:
        message = r.recognize_google(audio, language='ru-RU')
        return message.lower()
    except sr.UnknownValueError:
        speak('Не удалось распознать сообщение')
    except sr.RequestError as e:
        speak('Ошибка запроса к сервису распознавания речи: {}'.format(e))

# Функция для получения случайной фотографии собаки с сайта dog.ceo
def get_dog_image():
    print("Получение фотографии...")
    url = "https://dog.ceo/api/breeds/image/random"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))
        print('Фото получено')
        return data['message']
    else:
        return None

# Функция для получения породы собаки из ссылки на сайте dog.ceo
def get_breed_name(image_url):
    breed_index = image_url.find('breeds/')
    if breed_index != -1:
        breed_index += 7
        end_index = image_url[breed_index:].find('/')
        if end_index != -1:
            breed_name = image_url[breed_index:breed_index + end_index]
            print(f'Порода собаки на заданном фото - {breed_name}')
            return breed_name.replace('-', ' ').capitalize()
    return 'Не удалось распознать породу'

# Функция для сохранения фотографии собаки как файла
def save_image(file_name, image_url):
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response:
                f.write(chunk)
        speak(f'Вы сохранили фотографию с названием {file_name}')
        print(f'Вы сохранили фотографию с названием {file_name}')
    else:
        speak('Не удалось сохранить фотографию')

# Функция для получения разрешения фотографии в пикселях
def get_resolution(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_data = response.content
        with open('temp_image.jpg', 'wb') as f:
            f.write(image_data)
        image = Image.open('temp_image.jpg')
        width, height = image.size
        print('Разрешение фотографии {}x{}'.format(width, height))
        return 'Разрешение фотографии {}x{}'.format(width, height)
    else:
        return 'Не удалось получить разрешение фотографии'

# Основная функция программы
def main():
    print("Запуск голосового ассистента...")
    speak('Добро пожаловать в голосовой ассистент для работы с фотографиями собак')
    print("Голосовой ассистент запущен. Ожидание команды.")
    image_url = None
    while True:
        speak('Скажите команду')
        command = recognize_speech()
        if command == 'выход':
            speak('До свидания!')
            break
        elif command == 'показать':
            image_url = get_dog_image()
            if image_url:
                speak('Вот случайная фотография собаки')
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    Image.open(BytesIO(response.content)).show()
                else:
                    speak('Не удалось загрузить фотографию')
            else:
                speak('Не удалось получить фотографию')
        elif command == 'сохранить':
            if image_url:
                speak('Введите имя файла')
                file_name = recognize_speech()
                if file_name:
                    save_image('{}.jpg'.format(file_name), image_url)

        elif command == 'следующая':
            image_url = get_dog_image()
            if image_url:
                speak('Вот новая случайная фотография собаки')
                response = requests.get(image_url, stream=True)
                if response.status_code == 200:
                    Image.open(BytesIO(response.content)).show()
                else:
                    speak('Не удалось загрузить фотографию')
            else:
                speak('Не удалось получить фотографию')
        elif command == 'назвать породу':#работет только когда уже есть фотография( команды показать/следущая)
            if image_url:
                breed_name = get_breed_name(image_url)
                if breed_name:
                    speak('Это порода {}'.format(breed_name))
                else:
                    speak('Не удалось распознать породу')
            else:
                speak('Не удалось получить фотографию')
        elif command == 'разрешение':
            if image_url:
                speak(get_resolution(image_url))
            else:
                speak('Не удалось получить фотографию')
        else:
            speak('Неизвестная команда')

if __name__ == '__main__':
    main()