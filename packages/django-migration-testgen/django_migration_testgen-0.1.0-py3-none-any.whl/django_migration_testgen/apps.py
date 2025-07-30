from django.apps import AppConfig


class DjangoMigrationTestgenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'django_migration_testgen'
    verbose_name = 'Django Migration Test Generator'