from telegram import Update
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from utils import encode


def student(details: Update, context: CallbackContext):
    keyboard = [
        # First row
        [
            InlineKeyboardButton(
                text="ثبت نام",
                callback_data=encode(
                    {
                        "area": "student",
                        "function": "register",
                        "act": "start"
                    }
                )
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=details.effective_chat.id,
        text="به بخش دانش آموزان خوش آمدید",
        reply_to_message_id=details.message.message_id,
        reply_markup=reply_markup
    )
