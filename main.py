import telebot
import urllib
import dlib
import os
import requests
from skimage import io
import ffmpeg


if not os.path.exists('photos'):
    os.mkdir('photos')
if not os.path.exists('voice'):
    os.mkdir('voice')
if not os.path.exists('voice_ogg'):
    os.mkdir('voice_ogg')


f = open('token.txt', 'r')
token = f.read().replace('\n', '')
bot = telebot.TeleBot(token)
f.close()


def photo(image, file_path):
    detector = dlib.get_frontal_face_detector()
    face_rects = list(detector(image, 1))
    if face_rects != []:
        return True
    else:
        return False


@bot.message_handler(commands=['start'])
def start_message(message):
    print(message)
    bot.send_message(message.chat.id, '''Hello! I
                     can save audio files and photos with faces.  \n  /audio - to
                     get the saved audio \n /photo - to get photos with faces''')


@bot.message_handler(commands=['photo'])
def photo_message(message):
    path = './photos/' + str(message.from_user.id) + '/'
    if os.path.exists(path):
        photos = sorted(os.listdir(path))
        for img in photos:
            post = 'https://api.telegram.org/bot%s/sendPhoto?chat_id=%s' % (token, message.chat.id)
            files = {'photo': open(path+img, 'rb')}
            status = requests.post(post, files=files)
            print(status)
    else:
        bot.send_message(message.chat.id, 'Нет сохраненных фотографий')


@bot.message_handler(commands=['audio'])
def audio_message(message):
    path = './voice/' + str(message.from_user.id) + "/"
    if os.path.exists(path):
        audios = sorted(os.listdir(path))
        for aud in audios:
            post = 'https://api.telegram.org/bot%s/sendAudio?chat_id=%s' % (token, message.chat.id)
            files = {'audio': open(path+aud, 'rb')}
            status = requests.post(post, files=files)
            print(status)
    else:
        bot.send_message(message.chat.id,
                         'Нет сохраненных голосовых сообщений')


@bot.message_handler(content_types=['text', 'photo', 'voice'])
def send_text(message):
    # Если прислали фотографию
    if message.content_type == 'photo':
        print(message)
        file_path = bot.get_file(message.photo[-1].file_id).file_path
        path = 'https://api.telegram.org/file/bot%s/%s' % (token, file_path)
        print(path)
        image = io.imread(path)
        io.imshow(image)
        if photo(image, file_path):
            save_path = './photos/' + str(message.from_user.id) + '/'
            if not os.path.exists(save_path):
                os.mkdir(save_path)
            f = open(save_path + 'photo' +
                     str(len(os.listdir(save_path))+1), 'wb')
            f.write(urllib.request.urlopen('https://api.telegram.org/file/bot%s/%s'
                                           % (token, file_path)).read())
            f.close()
            bot.send_message(message.chat.id, 'Photo сохранено')
        else:
            bot.send_message(message.chat.id,
                             'Photo не сохранено - лица не найдены')
    # Если прислали голосовое сообщение
    if message.content_type == 'voice':
        file_path = bot.get_file(message.voice.file_id).file_path
        ogg_path = './voice_ogg/' + str(message.from_user.id) + '/'
        wav_path = './voice/' + str(message.from_user.id) + '/'
        if not os.path.exists(ogg_path):
            os.mkdir(ogg_path)
            os.mkdir(wav_path)
        print(urllib.request.urlopen('https://api.telegram.org/file/bot%s/%s'
                                     % (token, file_path)))
        name = 'audio_message_'
        f = open(ogg_path + name +
                 str(len(os.listdir(ogg_path))+1) + '.ogg', 'wb')
        f.write(urllib.request.urlopen('https://api.telegram.org/file/bot%s/%s'
                                       % (token, file_path)).read())
        f.close()
        in1 = ffmpeg.input(ogg_path + name +
                           str(len(os.listdir(ogg_path))) + '.ogg').audio
        out = ffmpeg.output(in1, wav_path + name +
                            str(len(os.listdir(wav_path))+1) + '.wav', ar=16000)
        out.run()


bot.polling()
