import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.apps import apps
from io import StringIO

from django_migration_testgen.management.commands.generate_migration_tests import Command
from django_migration_testgen.utils import MigrationScanner, TestFileGenerator


class GenerateMigrationTestsCommandTest(TestCase):
    """Test the generate_migration_tests management command."""

    def setUp(self):
        self.command = Command()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_command_help(self):
        """Test that command help is available."""
        help_text = self.command.help
        self.assertIn('Generate test files for Django migrations', help_text)

    @patch('django_migration_testgen.management.commands.generate_migration_tests.MigrationScanner')
    @patch('django_migration_testgen.management.commands.generate_migration_tests.TestFileGenerator')
    def test_command_execution(self, mock_generator, mock_scanner):
        """Test basic command execution."""
        # Mock scanner
        mock_scanner_instance = MagicMock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.get_all_migrations.return_value = [
            {
                'app_label': 'testapp',
                'migration_name': '0001_initial',
                'file_path': Path('/fake/path'),
                'dependencies': [],
                'operations': ['CreateModel']
            }
        ]

        # Mock generator
        mock_generator_instance = MagicMock()
        mock_generator.return_value = mock_generator_instance
        mock_generator_instance.generate_test_file.return_value = Path('/fake/test.py')

        # Run command
        out = StringIO()
        call_command('generate_migration_tests', stdout=out)

        # Verify scanner was called
        mock_scanner_instance.get_all_migrations.assert_called_once()

        # Verify generator was called
        mock_generator_instance.generate_test_file.assert_called_once()

        # Check output
        output = out.getvalue()
        self.assertIn('Scanning for migration files', output)
        self.assertIn('Found 1 migration(s) to process', output)

    @patch('django_migration_testgen.management.commands.generate_migration_tests.MigrationScanner')
    def test_command_no_migrations(self, mock_scanner):
        """Test command when no migrations are found."""
        # Mock scanner to return empty list
        mock_scanner_instance = MagicMock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.get_all_migrations.return_value = []

        # Run command
        out = StringIO()
        call_command('generate_migration_tests', stdout=out)

        # Check output
        output = out.getvalue()
        self.assertIn('No migrations found', output)

    @patch('django_migration_testgen.management.commands.generate_migration_tests.MigrationScanner')
    def test_command_app_filter(self, mock_scanner):
        """Test command with app filter."""
        # Mock scanner
        mock_scanner_instance = MagicMock()
        mock_scanner.return_value = mock_scanner_instance
        mock_scanner_instance.get_all_migrations.return_value = [
            {
                'app_label': 'testapp',
                'migration_name': '0001_initial',
                'file_path': Path('/fake/path'),
                'dependencies': [],
                'operations': ['CreateModel']
            },
            {
                'app_label': 'otherapp',
                'migration_name': '0001_initial',
                'file_path': Path('/fake/path2'),
                'dependencies': [],
                'operations': ['CreateModel']
            }
        ]

        # Run command with app filter
        out = StringIO()
        with patch('django_migration_testgen.management.commands.generate_migration_tests.TestFileGenerator'):
            call_command('generate_migration_tests', app='testapp', stdout=out)

        # Verify filtering logic would be applied
        mock_scanner_instance.get_all_migrations.assert_called_once()

    def test_command_dry_run(self):
        """Test command dry run mode."""
        with patch(
                'django_migration_testgen.management.commands.generate_migration_tests.MigrationScanner') as mock_scanner:
            with patch(
                    'django_migration_testgen.management.commands.generate_migration_tests.TestFileGenerator') as mock_generator:
                # Mock scanner
                mock_scanner_instance = MagicMock()
                mock_scanner.return_value = mock_scanner_instance
                mock_scanner_instance.get_all_migrations.return_value = [
                    {
                        'app_label': 'testapp',
                        'migration_name': '0001_initial',
                        'file_path': Path('/fake/path'),
                        'dependencies': [],
                        'operations': ['CreateModel']
                    }
                ]

                # Run command in dry run mode
                out = StringIO()
                call_command('generate_migration_tests', dry_run=True, stdout=out)

                # Verify generator was not called in dry run
                mock_generator.return_value.generate_test_file.assert_not_called()

                # Check output indicates dry run
                output = out.getvalue()
                self.assertIn('Would generate:', output)