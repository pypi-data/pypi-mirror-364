# coding: utf-8
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import router

from ... import init
from ... import is_initialized
from ... import set_partitioning_for_model


class Command(BaseCommand):
    """Применяет партицирование к таблице переданной модели.

    Команда, если это необходимо, сперва инициализирует средства партицирования
    для БД, в которой хранится переданная модель, а затем создает необходимые
    триггеры. Подробнее см. в `django_postgres_partitioning.init` и
    `django_postgres_partitioning.set_partitioning_for_model`.

    """
    help = 'Applies partitioning to the table.'

    def add_arguments(self, parser):
        parser.add_argument(
            'app_label',
            help=u'App label of an application.',
        )
        parser.add_argument(
            'model_name',
            help=u'Model name.',
        )
        parser.add_argument(
            'field_name',
            help=u'Field name. It will be the partition key.',
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        model_name = options['model_name']
        field_name = options['field_name']
        Model = apps.get_model(app_label, model_name)
        db_alias = router.db_for_write(Model)

        if not is_initialized(db_alias):
            init(db_alias)

        set_partitioning_for_model(Model, field_name, force=True)
