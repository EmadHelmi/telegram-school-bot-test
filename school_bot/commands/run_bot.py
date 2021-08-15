from bot.listener import Listener
from settings import BOT_TOKEN

from . import Command


class CreateTablesCommand(Command):
    @staticmethod
    def run():
        try:
            listener = Listener(BOT_TOKEN)
            listener.add_handlers()
            listener.updater.start_polling()
        except KeyboardInterrupt:
            listener.updater.stop()
