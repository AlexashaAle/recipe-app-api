from unittest.mock import patch

from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTest(TestCase):

    def test_wait_for_db_ready(self):
        """Test waiting for db when db is avalible"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # мок обьект симуляция поведения реального обьекта
            # в данной функии если функция сработала в джанго возвращает правду
            gi.return_value = True
            call_command('wait_for_db')
            # Посчитать количество запросов
            self.assertEqual(gi.call_count, 1)
    # функция мок обьектов Симулирует ожидание для быстроей проверки теста

    @patch('time.sleep', return_value=True)
    # требует внесения в аргументы, или выдаст ошибку
    def test_wait_for_db(self, ts):
        """test waiting dor db """
        # симулирует поведение указанной в ковычках программы
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # первые 5 раз симулировать ошибку  на 6ой вернуть правду
            gi.side_effect = [OperationalError] * 5 + [True]
            # вызывает нашу команду
            call_command('wait_for_db')
            # проверяем количество запрсов
            self.assertEqual(gi.call_count, 6)
