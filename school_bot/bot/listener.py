from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from telegram.ext.callbackcontext import CallbackContext
from telegram.ext.callbackqueryhandler import CallbackQueryHandler
from telegram.update import Update

from bot.command_handlers.exam import exam
from bot.command_handlers.start import start
from bot.command_handlers.student import student
from bot.query_handlers.exam import ExamQueryHandler
from bot.query_handlers.student import StudentQueryHandler
from redis_connection import redis_conn as conn
from settings import REDIS
from utils import decode


class Listener:
    def __init__(self, token) -> None:
        self.updater = Updater(token=token)
        self.job = self.updater.job_queue
        self.dispatcher = self.updater.dispatcher

    def add_handlers(self):
        start_handler = CommandHandler('start', start)
        self.dispatcher.add_handler(start_handler)

        student_handler = CommandHandler('student', student)
        self.dispatcher.add_handler(student_handler)

        exam_handler = CommandHandler('exam', exam)
        self.dispatcher.add_handler(exam_handler)

        query_handler = CallbackQueryHandler(
            self.query_handler, pass_job_queue=True)
        self.dispatcher.add_handler(query_handler)

        message_handler = MessageHandler(
            Filters.text & (~Filters.command), self.message_handler)
        self.dispatcher.add_handler(message_handler)

    def query_handler(self, details: Update, context: CallbackContext):
        data = decode(details.callback_query.data)

        area = data.pop("area")
        func = data.pop("function")
        try:
            act = data.pop("act")
        except KeyError:
            act = None

        if area == "student":
            student_func = getattr(StudentQueryHandler, func)
            student_func(details, context, act=act, extra_details=data)
        elif area == "exam":
            exam_func = getattr(ExamQueryHandler, func)
            exam_func(details, context, act=act, extra_details=data)

    def message_handler(self, details: Update, context: CallbackContext):
        user_id = details.effective_user.id
        res = conn.get(list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        )
        if not res:
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="هیچی"
            )
            return
        area, func, status = res.split("#")
        if area == "student":
            student_func = getattr(StudentQueryHandler, func)
            student_func(details, context)
        elif area == "exam":
            exam_func = getattr(ExamQueryHandler, func)
            exam_func(details, context)
