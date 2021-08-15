from telegram import Update
from telegram.ext import CallbackContext
from unidecode import unidecode

from models import DB
from models.models import Grade, Student
from redis_connection import redis_conn as conn
from settings import REDIS


class StudentQueryHandler:
    @staticmethod
    def register(details: Update, context: CallbackContext, act=None, status=None, extra_details=None):
        user_id = details.effective_user.id

        redis_register_key = list(REDIS["STUDENT_REGISTER"].items())[0][0].format(
            user_id=user_id)
        redis_status_key = list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        redis_status_value = list(REDIS["STATUS"].items())[0][1]

        area = "student"
        function = "register"

        if not status:
            status = conn.get(redis_status_key).split("#")[2]

        if act == "start":
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_firstname"),
            )

            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفام نام کوچک خود را وارد کنید"
            )
        else:
            if not status:
                status = conn.get(redis_status_key).split("#")[2]

        if status == "waiting_for_firstname":
            firstname = details.effective_message.text
            conn.hset(
                redis_register_key,
                "firstname",
                firstname
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_lastname"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا نام خانوادگی خود را وارد کنید"
            )
        elif status == "waiting_for_lastname":
            lastname = details.effective_message.text
            conn.hset(
                redis_register_key,
                "lastname",
                lastname
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_national_id"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا کد ملی خود را وارد کنید"
            )
        elif status == "waiting_for_national_id":
            national_id = unidecode(details.effective_message.text)
            conn.hset(
                redis_register_key,
                "national_id",
                national_id
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_phone_number"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا شماره موبایل خود را وارد کنید"
            )
        elif status == "waiting_for_phone_number":
            phone_number = unidecode(details.effective_message.text)
            conn.hset(
                redis_register_key,
                "phone_number",
                phone_number
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_email"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا ایمیل خود را وارد کنید (این گزینه اختیاری است. در صورت عدم تمایل کلمه «بعدا» را ارسال فرمایید)"
            )
        elif status == "waiting_for_email":
            email = details.effective_message.text
            if email != "بعدا":
                conn.hset(
                    redis_register_key,
                    "email",
                    email
                )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_grade"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا پایه تحصیلی خود را وارد کنید (به صورت عددی بین ۱۰ تا ۱۲)"
            )
        elif status == "waiting_for_grade":
            grade = unidecode(details.effective_message.text)
            conn.hset(
                redis_register_key,
                "grade",
                grade
            )
            info = conn.hgetall(redis_register_key)

            db = DB()
            db.open_session()

            student = Student(
                telegram_id=user_id,
                national_code=info["national_id"],
                first_name=info["firstname"],
                last_name=info["lastname"],
                phone_number=info["phone_number"],
                email=info.get("email"),
                grade=db.session.query(Grade).filter(
                    Grade.number == info["grade"]).first().id
            )
            db.session.add(student)
            db.commit(details.effective_chat.id, context)

            conn.delete(redis_status_key, redis_register_key)
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="اطلاعات شما با موفقیت ذخیره شد"
            )
