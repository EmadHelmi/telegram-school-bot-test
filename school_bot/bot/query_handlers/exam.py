import datetime
import random

from telegram import Update
from telegram.ext import CallbackContext
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from unidecode import unidecode

from models import DB
from models.models import Course, Exam, Grade, Question, Student
from redis_connection import redis_conn as conn
from settings import REDIS
from utils import encode


def send_remaining_time(context: CallbackContext):
    remain_time = conn.ttl(context.job.context["exam_redis_key"]) // 60
    if remain_time > 0:
        for member_id in context.job.context["members_id"]:
            context.bot.send_message(
                chat_id=member_id,
                text=f"از وقت آزمون شما {remain_time} دقیقه مانده‌است."
            )


def send_finish_message(context: CallbackContext):
    conn.delete(context.job.context["exam_redis_key"])
    for member_id in context.job.context["members_id"]:
        context.bot.send_message(
            chat_id=member_id,
            text=f"آزمون شما به پایان رسیده‌است"
        )


class ExamQueryHandler:
    @staticmethod
    def create(
        details: Update,
        context: CallbackContext,
        act=None,
        status=None,
        extra_details=None
    ):
        user_id = details.effective_user.id

        redis_status_key = list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        redis_status_value = list(REDIS["STATUS"].items())[0][1]

        area = "exam"

        if act == "start":
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function="fill_details",
                    status="waiting_for_details"),
            )

            keyboard = [
                # First row
                [
                    InlineKeyboardButton(
                        text="متوجه شدم! بزن بریم",
                        callback_data=encode(
                            {
                                "area": "exam",
                                "function": "fill_details",
                            }
                        )
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text=(
                    "وقت بخیر!\n"
                    "به فرایند طراحی آزمون خوش آمدید:)!\n"
                    "در این شبیه‌ساز تعداد سوالات توسط ربات انتخاب می‌شوند "
                    "آنچه نیاز است تا شما وارد کنید عبارتند از:\n"
                    "نام آزمون، پایه‌ای که آزمون برای آن برگزار می‌شود و مدت زمان آزمون.\n"
                    "در نهایت لازم است تا این آزمون با حد اقل یک نفر دیگر به اشتراک گذاشته شود "
                    "تا بتوان آن را برگزار کرد.\n"
                ),
                reply_markup=reply_markup
            )

    @staticmethod
    def fill_details(
        details: Update,
        context: CallbackContext,
        act=None,
        status=None,
        extra_details=None
    ):
        user_id = details.effective_user.id

        redis_register_key = list(REDIS["EXAM_REGISTER"].items())[0][0].format(
            user_id=user_id)
        redis_status_key = list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        redis_status_value = list(REDIS["STATUS"].items())[0][1]

        area = "exam"
        function = "fill_details"

        res = conn.get(redis_status_key)
        status = res.split("#")[2]

        if status == "waiting_for_details":
            conn.hset(
                redis_register_key,
                "creator",
                user_id
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_exam_name"
                )
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا نام آزمون را وارد کنید"
            )
        elif status == "waiting_for_exam_name":
            exam_name = details.effective_message.text
            conn.hset(
                redis_register_key,
                "name",
                exam_name
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_grade"),
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا پایه‌ی مد نظر خود را وارد کنید (به صورت عددی بین ۱۰ تا ۱۲)"
            )
        elif status == "waiting_for_grade":
            grade = unidecode(details.effective_message.text)
            conn.hset(
                redis_register_key,
                "grade",
                grade
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_time"),
            )
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا مدت زمان آزمون را (به دقیقه) وارد کنید"
            )
        elif status == "waiting_for_time":
            time = unidecode(details.effective_message.text)
            conn.hset(
                redis_register_key,
                "time",
                time
            )

            info = conn.hgetall(redis_register_key)

            db = DB()
            db.open_session()

            exam = Exam(
                name=info["name"],
                time=info["time"],
                creator=db.session.query(Student).filter(
                    Student.telegram_id == user_id).first().id,
                grade=db.session.query(Grade).filter(
                    Grade.number == info["grade"]).first().id
            )
            db.session.add(exam)
            db.commit(details.effective_chat.id, context)

            grade = db.session.query(Grade).filter(
                Grade.id == exam.grade).first()
            courses = db.session.query(Course).filter(
                Course.grades.contains(grade)).all()
            questions = db.session.query(Question).filter(
                Question.course.in_([course.id for course in courses])
            ).all()

            if len(questions) < 5:
                context.bot.send_message(
                    chat_id=details.effective_chat.id,
                    text="تعداد سوالات کمتر از ۵ است"
                )
                return

            random.shuffle(questions)
            questions = questions[:5]

            for question in questions:
                exam.questions.append(question)

            conn.delete(redis_status_key, redis_register_key)
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="آزمون با موفقیت ساخته شد. حال می‌توانید آن را از طریق بخش آزمون به اشتراک بگذارید"
            )

    @staticmethod
    def share(
        details: Update,
        context: CallbackContext,
        act=None,
        status=None,
        extra_details=None
    ):
        user_id = details.effective_user.id

        redis_status_key = list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        redis_status_value = list(REDIS["STATUS"].items())[0][1]

        area = "exam"
        function = "share"

        db = DB()
        db.open_session()

        if act == "start":
            exams = db.session.query(Exam).filter(
                Exam.creator == db.session.query(Student).filter(
                    Student.telegram_id == user_id).first().id
            ).all()

            if len(exams) == 0:
                context.bot.send_message(
                    chat_id=details.effective_chat.id,
                    text="شما هیچ آزمونی ندارید"
                )
                return

            keyboard = [
                [
                    InlineKeyboardButton(
                        text=exam.name,
                        callback_data=encode(
                            {
                                "area": area,
                                "function": function,
                                "exam_id": exam.id
                            }
                        )
                    )
                ] for exam in exams
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا آزمون خود را انتخاب کنید",
                reply_markup=reply_markup
            )

            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_exam_selection"),
            )
        else:
            if not status:
                status = conn.get(redis_status_key).split("#")[2]

        if status == "waiting_for_exam_selection":
            # extra_details argument in **kwargs has the exam id
            # it is a list and its first index is the exam id
            exam = db.session.query(Exam).filter(
                Exam.id == extra_details["exam_id"]).first()
            students = db.session.query(Student).filter(
                Student.grade == exam.grade).all()

            if len(students) == 0:
                context.bot.send_message(
                    chat_id=details.effective_chat.id,
                    text="هیچ دانش آموزی صلاحیت شرکت در این آزمون را ندارد"
                )
                return

            keyboard = [
                [
                    InlineKeyboardButton(
                        text="{student_name} - ۴ رقم آخر کد ملی: {national_code}".format(
                            student_name=student.first_name + " " + student.last_name,
                            national_code=student.national_code[:-4]
                        ),
                        callback_data=encode(
                            {
                                "area": area,
                                "function": function,
                                "exam_id": exam.id,
                                "student_id": student.id
                            }
                        )
                    )
                ] for student in students
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا دانش آموز مد نظر خود را انتخاب کنید",
                reply_markup=reply_markup
            )

            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_student_selection"),
            )
        elif status == "waiting_for_student_selection":
            # extra_details argument in **kwargs has the exam id
            # it is a list and its first index is the exam id
            exam = db.session.query(Exam).filter(
                Exam.id == extra_details["exam_id"]).first()
            # extra_details argument in **kwargs has the exam id
            # it is a list and its second index is the exam id
            student = db.session.query(Student).filter(
                Student.id == extra_details["student_id"]).first()

            creator = db.session.query(Student).filter(
                Student.id == exam.creator).first()

            keyboard = [
                [
                    InlineKeyboardButton(
                        text="شرکت می‌کنم",
                        callback_data=encode(
                            {
                                "area": area,
                                "function": "approve",
                                "exam_id": exam.id,
                                "approve": 1
                            }
                        )
                    ),
                    InlineKeyboardButton(
                        text="شرکت نمی‌کنم",
                        callback_data=encode(
                            {
                                "area": area,
                                "function": "approve",
                                "exam_id": exam.id,
                                "approve": 0
                            }
                        )
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=student.telegram_id,
                text=f"سلام\nکاربر: {creator.first_name} {creator.last_name}\nشما را به شرکت در یک آزمون دعوت کرده‌است",
                reply_markup=reply_markup
            )

            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا منتظر تایید کاربر مورد نظر خود باشید"
            )

            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_student_selection"),
            )

    @staticmethod
    def approve(
        details: Update,
        context: CallbackContext,
        act=None,
        status=None,
        extra_details=None
    ):
        user_id = details.effective_user.id

        redis_status_key = list(REDIS["STATUS"].items())[0][0].format(
            user_id=user_id)
        redis_status_value = list(REDIS["STATUS"].items())[0][1]

        area = "exam"
        function = "approve"

        db = DB()
        db.open_session()

        # extra_details argument in **kwargs has the exam id
        # it is a list and its first index is the exam id
        exam = db.session.query(Exam).filter(
            Exam.id == extra_details["exam_id"]).first()
        # extra_details argument in **kwargs has the exam id
        # it is a list and its second index is the exam id
        student = db.session.query(Student).filter(
            Student.telegram_id == user_id).first()

        creator = db.session.query(Student).filter(
            Student.id == exam.creator).first()

        if int(extra_details["approve"]):
            exam.members.append(student)
            exam.members.append(creator)

            db.commit()

            context.bot.send_message(
                chat_id=details.effective_chat.id,
                text="لطفا منتظر شروع آزمون توسط کاربر باشید"
            )

            keyboard = [
                [
                    InlineKeyboardButton(
                        text="شروع آزمون",
                        callback_data=encode(
                            {
                                "area": area,
                                "function": "start_exam",
                                "exam_id": exam.id,
                            }
                        )
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            context.bot.send_message(
                chat_id=creator.telegram_id,
                text="درخواست آزمون شما قبول شد",
                reply_markup=reply_markup
            )
            conn.set(
                redis_status_key,
                redis_status_value.format(
                    area=area,
                    function=function,
                    status="waiting_for_exam_starts"),
            )
        else:
            context.bot.send_message(
                chat_id=creator.telegram_id,
                text="درخواست آزمون شما رد شد"
            )

    @staticmethod
    def start_exam(
        details: Update,
        context: CallbackContext,
        act=None,
        status=None,
        extra_details=None
    ):
        db = DB()
        db.open_session()

        # extra_details argument in **kwargs has the exam id
        # it is a list and its first index is the exam id
        exam = db.session.query(Exam).filter(
            Exam.id == extra_details["exam_id"]).first()

        for member in exam.members:
            if member.id == exam.creator:
                continue
            student = db.session.query(Student).filter(
                Student.id == member.id).first()
            context.bot.send_message(
                chat_id=student.telegram_id,
                text="آزمون شروع شد"
            )
        conn.set(
            f"{exam.id}",
            datetime.datetime.utcnow().strftime("%s"),
            ex=exam.time * 60
        )

        context.job_queue.run_repeating(
            send_remaining_time,
            60,
            last=exam.time * 60,
            context={
                "exam_redis_key": exam.id,
                "members_id": [member.telegram_id for member in exam.members]
            }
        )
        context.job_queue.run_once(
            send_finish_message,
            exam.time * 60,
            context={
                "exam_redis_key": exam.id,
                "members_id": [member.telegram_id for member in exam.members]
            }
        )
        context.bot.send_message(
            chat_id=details.effective_chat.id,
            text="آزمون شروع شد"
        )
