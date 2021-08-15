from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql.schema import ForeignKey, Table

from models import BaseModel


class Student(BaseModel):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    national_code = Column(String, unique=True)

    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)

    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)

    grade = Column(Integer, ForeignKey("grade.id", ondelete='CASCADE'))


grade_courses = Table(
    'gradeCourses',
    BaseModel.metadata,
    Column(
        'grade_id', Integer, ForeignKey(
            'grade.id', onupdate='CASCADE',
            ondelete='CASCADE'), primary_key=True, index=True),
    Column(
        'course_id', Integer, ForeignKey(
            'course.id', onupdate='CASCADE', ondelete='CASCADE'
        ), primary_key=True, index=True
    )
)


class Grade(BaseModel):
    __tablename__ = 'grade'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    number = Column(Integer)

    courses = relationship(
        "Course", secondary="gradeCourses", back_populates="grades")

    students = relationship('Student')


class Course(BaseModel):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    grades = relationship(
        "Grade", secondary="gradeCourses", back_populates="courses")


exam_courses = Table(
    'examCourses',
    BaseModel.metadata,
    Column('exam_id', Integer, ForeignKey(
        'exam.id', ondelete='CASCADE'), primary_key=True),
    Column('course_id', Integer, ForeignKey(
        'course.id', ondelete='CASCADE'), primary_key=True)
)

exam_students = Table(
    'examStudents',
    BaseModel.metadata,
    Column('exam_id', Integer, ForeignKey(
        'exam.id', ondelete='CASCADE'), primary_key=True),
    Column('student_id', Integer, ForeignKey(
        'student.id', ondelete='CASCADE'), primary_key=True)
)

exam_questions = Table(
    'examQuestions',
    BaseModel.metadata,
    Column('question_number', Integer, nullable=False),
    Column('exam_id', Integer, ForeignKey(
        'exam.id', ondelete='CASCADE'), primary_key=True),
    Column('question_id', Integer, ForeignKey(
        'question.id', ondelete='CASCADE'), primary_key=True)
)


class Question(BaseModel):
    __tablename__ = 'question'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String, nullable=False)

    course = Column(Integer, ForeignKey(
        Course.id, ondelete='CASCADE'), nullable=False)

    choice_1 = Column(String, nullable=False)
    choice_2 = Column(String, nullable=False)
    choice_3 = Column(String, nullable=False)
    choice_4 = Column(String, nullable=False)

    answer = Column(Integer)
    answer_details = Column(String)


class Exam(BaseModel):
    __tablename__ = 'exam'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    grade = Column(Integer, ForeignKey("grade.id", ondelete='CASCADE'))
    time = Column(Integer, nullable=False)
    creator = Column(Integer, ForeignKey("student.id", ondelete='CASCADE'))
    courses = relationship(
        'Course', secondary='examCourses', backref=backref('exams'))

    members = relationship(
        'Student', secondary='examStudents', backref=backref('exams'))

    questions = relationship(
        'Question', secondary='examQuestions', backref=backref('exams'))


class StudentExamAnswers(BaseModel):
    __tablename__ = 'studentExamAnswers'

    student = Column(Integer, ForeignKey(
        "student.id", ondelete='CASCADE'), primary_key=True)
    exam = Column(Integer, ForeignKey(
        "exam.id", ondelete='CASCADE'), primary_key=True)
    question_number = Column(Integer, primary_key=True)

    student_answer = Column(Integer)
    correct_answer = Column(Integer)


class StudentExamResult(BaseModel):
    __tablename__ = 'studentExamResult'

    student = Column(Integer, ForeignKey(
        "student.id", ondelete='CASCADE'), primary_key=True)
    exam = Column(Integer, ForeignKey(
        "exam.id", ondelete='CASCADE'), primary_key=True)

    corrects = Column(Integer, default=0)
    wrongs = Column(Integer, default=0)
    blanks = Column(Integer, default=0)
