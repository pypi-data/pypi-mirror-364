from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from pathlib import Path
import os

from django_migration_testgen.utils import MigrationScanner, TestFileGenerator


class Command(BaseCommand):
    help = 'Generate test files for Django migrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--app',
            type=str,
            help='Generate tests for specific app only'
        )
        parser.add_argument(
            '--output-dir',
            type=str,
            help='Custom output directory for test files'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be generated without creating files'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing test files'
        )

    def handle(self, *args, **options):
        scanner = MigrationScanner()
        generator = TestFileGenerator()

        self.stdout.write("🔍 Scanning for migration files...")
        migrations = scanner.get_all_migrations()

        if options['app']:
            migrations = [m for m in migrations if m['app_label'] == options['app']]

        if not migrations:
            self.stdout.write(
                self.style.WARNING("No migrations found or all migrations already have tests.")
            )
            return

        self.stdout.write(f"📁 Found {len(migrations)} migration(s) to process")

        generated_count = 0
        for migration in migrations:
            try:
                output_dir = self._get_output_dir(migration, options.get('output_dir'))

                if not options['force'] and self._test_exists(output_dir, migration['migration_name']):
                    self.stdout.write(
                        f"⏭️  Skipping {migration['app_label']}.{migration['migration_name']} (test exists)"
                    )
                    continue

                if options['dry_run']:
                    self.stdout.write(
                        f"🧪 Would generate: {output_dir}/test_{migration['migration_name']}.py"
                    )
                else:
                    test_file = generator.generate_test_file(migration, output_dir)
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Generated: {test_file}")
                    )
                    generated_count += 1

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error generating test for {migration['migration_name']}: {e}")
                )

        if not options['dry_run']:
            self.stdout.write(
                self.style.SUCCESS(f"🚀 Successfully generated {generated_count} test file(s)!")
            )

    def _get_output_dir(self, migration, custom_output_dir):
        """Determine output directory for test file."""
        if custom_output_dir:
            return Path(custom_output_dir) / migration['app_label'] / "migrations"

        app_config = apps.get_app_config(migration['app_label'])
        return Path(app_config.path) / "tests" / "migrations"

    def _test_exists(self, output_dir, migration_name):
        """Check if test file already exists."""
        test_file = Path(output_dir) / f"test_{migration_name}.py"
        return test_file.exists()