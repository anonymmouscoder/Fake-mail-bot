from aiogram import types



menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
	types.KeyboardButton('✉️ Obtenir un mail')
)

apanel = types.InlineKeyboardMarkup(row_width=3)
apanel.add(
    types.InlineKeyboardButton(text='Statut', callback_data='stats'),
	types.InlineKeyboardButton(text='mailing', callback_data='rass')
    )


back = types.ReplyKeyboardMarkup(resize_keyboard=True)
back.add(
    types.KeyboardButton('Annuler')
)
