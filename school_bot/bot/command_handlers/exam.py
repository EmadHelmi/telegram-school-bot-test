from telegram import Update
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup

from utils import encode


def exam(details: Update, context: CallbackContext):
    keyboard = [
        # First row
        [
            InlineKeyboardButton(
                text="ایجاد آزمون",
                callback_data=encode(
                    {
                        "area": "exam",
                        "function": "create",
                        "act": "start"
                    }
                )
            )
        ],
        # Second row
        [
            InlineKeyboardButton(
                text="اشتراک گذاری آزمون",
                callback_data=encode(
                    {
                        "area": "exam",
                        "function": "share",
                        "act": "start"
                    }
                )
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=details.effective_chat.id,
        text="به بخش آزمون خوش آمدید",
        reply_to_message_id=details.message.message_id,
        reply_markup=reply_markup
    )
