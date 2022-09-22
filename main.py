import logging
import json
import asyncio
import sqlite3
import time

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from config import API_TOKEN, admin
import keyboard as kb
from onesec_api import Mailbox


storage = MemoryStorage()
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


connection = sqlite3.connect('data.db')
q = connection.cursor()

q.execute('CREATE TABLE IF NOT EXISTS users (user_id integer)')
connection.commit()


class sender(StatesGroup):
    text = State()


@dp.message_handler(content_types=['text'], text='✉️ Obtenir un mail')
async def takeamail(m: types.Message):
    ma = Mailbox('')
    email = f'{ma._mailbox_}@1secmail.com'
    await m.answer(
        '📫 Voici votre email: <b>{}</b>\nEnvoyer un mail.\n'
        'Votre boite mail sera vérifiée chaque 05 secondes pour de nouveaux messages!\n\n'
        '<b>Le mail va expirer dans 10 minutes!!</b>'.format(email), parse_mode='HTML')
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
                        await m.answer(f'🔐 Nouveau message:\n\n<b>📧 Email</b>: {fromm}\n<b>📄 Sujet</b>: {theme}\n<b>📝 Message</b>: {mes}', reply_markup=kb.menu, parse_mode='HTML')
                        continue
        await asyncio.sleep(5)


#@dp.message_handler(content_types=['text'], text='🔐 Mot de passe')
#async def randompass(m: types.Message):
 #ma = Mailbox('')
 #passw = ma.rand_pass_for('')
    # await m.answer(f'🔑 Oui je génére un mot de passe pour vous: `{passw}`\n\n*Oui je génére un mot de passe pour vous', parse_mode='MarkdownV2')


@dp.message_handler(commands=['admin'])
async def adminstration(m: types.Message):
    if m.chat.id == admin:
        await m.answer('Bienvenue dans le panneau admin.', reply_markup=kb.apanel)
    else:
        await m.answer('Merde! Tu as piraté le serveur :(')


@dp.message_handler(content_types=['text'])
async def texthandler(m: types.Message):
    q.execute(f"SELECT * FROM users WHERE user_id = {m.chat.id}")
    result = q.fetchall()
    if len(result) == 0:
        uid = 'user_id'
        sql = 'INSERT INTO users ({}) VALUES ({})'.format(uid, m.chat.id)
        q.execute(sql)
        connection.commit()
    await m.answer(f'<b>Bienvenue, {m.from_user.mention} Ce bot est conçu pour recevoir rapidement du courrier temporaire.Utilisez les boutons ci-dessous  pour obtenir un email temporaire👇\n\n👨‍💻 Maintenu par @A_liou</b>', reply_markup=kb.menu,parse_mode='HTML')


@dp.callback_query_handler(text='stats')
async def statistics(call):
    row = q.execute('SELECT * FROM users').fetchall()
    lenght = len(row)
    await call.message.answer('Utilisateur totales: {}'.format(lenght))


@dp.callback_query_handler(text='rass')
async def usender(call):
    await call.message.answer('Saisissez le texte à envoyer.\n\nCliquez sur le bouton ci-dessous pour annuler 👇', reply_markup=kb.back)
    await sender.text.set()


@dp.message_handler(state=sender.text)
async def process_name(message: types.Message, state: FSMContext):
    info = q.execute('SELECT user_id FROM users').fetchall()
    if message.text == 'Отмена':
        await message.answer('Annuler! Retour au menu principal.', reply_markup=kb.menu)
        await state.finish()
    else:
        await message.answer('Patientez...', reply_markup=kb.menu)
        for i in range(len(info)):
            try:
                await bot.send_message(info[i][0], str(message.text))
            except:
                pass
        await message.answer('Distribution terminée.')
        await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True) 
