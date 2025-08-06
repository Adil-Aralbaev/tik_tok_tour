import telebot
import django
import os
import random
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from account.models import User
from account.services import generate_random_password, generate_otp, store_to_cache
from .config import BOT

bot = telebot.TeleBot(BOT)


@bot.message_handler(commands=['start'])
def main(message):
    # Создаем кнопку с запросом контакта
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    contact_button = telebot.types.KeyboardButton(
        text="Отправить номер телефона", request_contact=True
    )
    markup.add(contact_button)

    bot.send_message(
        message.chat.id,
        "Пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже:",
        reply_markup=markup
    )


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    contact = message.contact
    phone_number = contact.phone_number
    otp_code = generate_otp()

    try:
        user = User.objects.get(phone_number=f'{phone_number}')
        say_hello = f"""

                    Здравствуйте {user.username}! 

                    Вы запросили вход в систему. Ваш одноразовый код (OTP):

                    🔐 {otp_code}

                    Пожалуйста, введите этот код в приложении для подтверждения.

                    Код действителен в течение 5 минут.

                    Если вы не запрашивали код, просто проигнорируйте это сообщение.

                    С уважением,  
                    Ваша команда поддержки.

                    """

    except User.DoesNotExist:
        username = 'user' + str(random.randint(100000, 999999))
        password = generate_random_password()
        chat_id = message.chat.id
        user = User(username=username, phone_number=phone_number, chat_id=chat_id)
        user.is_verified = False
        user.set_password(password)
        user.save()

        say_hello = f"""

                    Здравствуйте!

                    Вы успешно зарегистрировались в нашем сервисе.

                    Для подтверждения входа используйте одноразовый код (OTP):

                    🔐 OTP код: {otp_code}

                    Ваши временные учетные данные:

                    👤 Логин : {user.username}  
                    🔑 Временный пароль: {password}

                    ⚠️ В целях безопасности, рекомендуем как можно скорее сменить пароль и добавить личные данные в вашем профиле.

                    После подтверждения OTP кода вы сможете войти в личный кабинет.

                    Спасибо, что выбрали наш сервис!

                """

    store_to_cache(identifier=user.chat_id, value=otp_code)
    print('otp in cache')
    bot.send_message(
        message.chat.id,
        f'{say_hello}',
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )


while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"Polling crashed: {e}")


