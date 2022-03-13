# Bay convention все команды джанго находятся в дериктории менеджмен и команды
import time
# модуль соеденения
from django.db import connections
# модуль ошибки при отсутвии соеденения
from django.db.utils import OperationalError
# Базовы модуль для создание класса команды
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is avalible"""
    # Handle запускается всякий раз когда запускается команда
    def handle(self, *args, **options):
        # функция печати в команде джанго
        self.stdout.write('Waiting for database...')
        db_conn = None
        # пока база не подключается
        while not db_conn:
            # попробуй подключится
            try:
                db_conn = connections['default']
            # если случилась ошибка
            except OperationalError:
                self.stdout.write('Database unavailable, waiting for 1 second')
                # остановка петли на одну секунду и попытка подключения
                time.sleep(1)
        # ПОсле завешения петли высвечивает месседж зеленым
        self.stdout.write(self.style.SUCCESS('Database is availible'))
