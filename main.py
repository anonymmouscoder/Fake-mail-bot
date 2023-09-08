import logging
import asyncio
import sqlite3
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup

from config import API_TOKEN, admin
from onesec_api import Mailbox

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

connection = sqlite3.connect('data.db')
q = connection.cursor()
q.execute('CREATE TABLE IF NOT EXISTS users (user_id integer)')
connection.commit()

menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_keyboard.add("✉️ Obtenir un mail", "🔐 Mot de passe", "✉️ Composer un e-mail")

class SenderStates(StatesGroup):
    text = State()
    to_email = State()
    to_subject = State()
    to_body = State()

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"Bienvenue, {message.from_user.first_name} !\n"
        "Ce bot est conçu pour recevoir rapidement du courrier temporaire.\n"
        "Utilisez les boutons ci-dessous pour obtenir un email temporaire, générer un mot de passe ou composer un e-mail.",
        reply_markup=menu_keyboard,
    )

@dp.message_handler(lambda message: message.text == "✉️ Obtenir un mail")
async def get_temp_email(message: types.Message):
    try:
        ma = Mailbox('')
        email = f'{ma._mailbox_}@1secmail.com'
        await message.answer(
            '📫 Voici votre email: <b>{}</b>\nEnvoyer un mail.\n'
            'Votre boite mail sera vérifiée chaque 05 secondes pour de nouveaux messages!\n\n'
            '<b>Le mail va expirer dans 10 minutes!!</b>'.format(email), parse_mode='HTML'
        )
        timeout = 600
        timer = {}
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            test = 0
            if test == 5:
                break
            test -= 1
            mb = ma.filtred_mail()
            if mb != 'not found':
                for i in mb:
                    if i not in timer:
                        timer[i] = i
                        if isinstance(mb, list):
                            mf = ma.mailjobs('read', mb[0])
                            js = mf.json()
                            fromm = js['from']
                            theme = js['subject']
                            mes = js['textBody']
                            await message.answer(f'🔐 Nouveau message:\n\n<b>📧 Email</b>: {fromm}\n<b>📄 Sujet</b>: {theme}\n<b>📝 Message</b>: {mes}', reply_markup=menu_keyboard, parse_mode='HTML')
                            continue
            await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"Erreur lors de la récupération de l'e-mail temporaire : {e}")
        await message.answer("Une erreur s'est produite. Veuillez réessayer plus tard.")
        
@dp.message_handler(lambda message: message.text == "🔐 Mot de passe")
async def generate_password(message: types.Message):
    try:
       
        password = "passe123" 
        await message.answer(f"Mot de passe généré : {password}")
    except Exception as e:
        logging.error(f"Erreur lors de la génération du mot de passe : {e}")
        await message.answer("Une erreur s'est produite. Veuillez réessayer plus tard.")

@dp.message_handler(lambda message: message.text == "✉️ Composer un e-mail")
async def compose_email(message: types.Message):
    try:
        await message.answer("Veuillez saisir l'adresse e-mail du destinataire :")
        await SenderStates.to_email.set()
    except Exception as e:
        logging.error(f"Erreur lors de la composition de l'e-mail : {e}")
        await message.answer("Une erreur s'est produite. Veuillez réessayer plus tard.")

@dp.message_handler(state=SenderStates.to_email)
async def to_email(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['to_email'] = message.text

        await message.answer("Veuillez saisir le sujet de l'e-mail :")
        await SenderStates.to_subject.set()
    except Exception as e:
        logging.error(f"Erreur lors de la saisie de l'adresse e-mail du destinataire : {e}")
        await message.answer("Une erreur s'est produite. Veuillez réessayer plus tard.")

@dp.message_handler(state=SenderStates.to_subject)
async def to_subject(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['subject'] = message.text

        await message.answer("Veuillez saisir le corps de l'e-mail :")
        await SenderStates.to_body.set()
    except Exception as e:
        logging.error(f"Erreur lors de la saisie du sujet de l'e-mail : {e}")
        await message.answer("Une erreur s'est produite. Veuillez réessayer plus tard.")

@dp.message_handler(state=SenderStates.to_body)
async def to_body(message: types.Message, state: FSMContext):
    try:
        async with state.proxy() as data:
            data['body'] = message.text

        sender_email = "codingmailer@gmail.com"  # ton adresse e-mail
        sender_password = "votre_mot_de_passe"  #  mot de passe

        subject = data['subject']
        body = data['body']
        to_email = data['to_email']

        msg = MIMEMultipart()
        msg.attach(MIMEText(body, 'plain'))
        msg['From'] = sender_email
        msg['To'] = to_email
        msg['Subject'] = subject

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        text = msg.as_string()
        server.sendmail(sender_email, to_email, text)

        server.quit()

        await message.answer("E-mail envoyé avec succès !")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
        await message.answer("Une erreur s'est produite lors de l'envoi de l'e-mail. Veuillez réessayer plus tard.")

    finally:
        await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
