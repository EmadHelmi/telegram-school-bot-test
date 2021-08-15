import logging
import traceback
from datetime import datetime

from sqlalchemy import Column, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from telegram.ext.callbackcontext import CallbackContext

from settings import DATABASE

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    created_date = Column(DateTime, default=datetime.utcnow)
    modified_date = Column(DateTime)
    deleted_date = Column(DateTime)


class DB:
    def __init__(self, db_type="psql") -> None:
        db = DATABASE[db_type]
        self.engine = create_engine(
            f'postgresql://{db["DB_USER"]}:{db["DB_PASSWORD"]}@{db["DB_HOST"]}:{db["DB_PORT"]}/{db["DB_NAME"]}',
            echo=True
        )

    def open_session(self):
        self.session = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine)
        )

    def commit(self, chat_id=None, context: CallbackContext = None):
        try:
            self.session.commit()
        except:
            self.session.rollback()
            logging.error(traceback.format_exc())
            if chat_id and context:
                context.bot.send_message(
                    chat_id=chat_id,
                    text="مشکلی رخ داده است لطفا مجددا تلاش نمایید"
                )

    def close_session(self):
        self.session.close()
