"""
Tests for utility functions and classes.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

from django.test import TestCase
from django.apps import apps

from django_migration_testgen.utils import MigrationScanner, TestFileGenerator


class MigrationScannerTest(TestCase):
    """Test the MigrationScanner class."""

    def setUp(self):
        self.scanner = MigrationScanner()

    def test_scanner_initialization(self):
        """Test that scanner initializes properly."""
        self.assertIsNotNone(self.scanner.loader)

    @patch('django_migration_testgen.utils.apps.get_app_configs')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_get_all_migrations(self, mock_glob, mock_exists, mock_get_app_configs):
        """Test getting all migrations."""
        # Mock app config
        mock_app_config = MagicMock()
        mock_app_config.name = 'testapp'
        mock_app_config.path = '/fake/path/testapp'
        mock_get_app_configs.return_value = ['testapp']

        # Mock apps.get_app_config
        with patch('django_migration_testgen.utils.apps.get_app_config') as mock_get_app:
            mock_get_app.return_value = mock_app_config

            # Mock path exists
            mock_exists.return_value = True

            # Mock migration files
            mock_migration_file = MagicMock()
            mock_migration_file.name = '0001_initial.py'
            mock_migration_file.stem = '0001_initial'
            mock_glob.return_value = [mock_migration_file]

            # Mock file reading
            with patch('builtins.open', mock_open(read_data='dependencies = []\\noperations = []')):
                with patch.object(self.scanner, '_has_existing_test', return_value=False):
                    migrations = self.scanner.get_all_migrations()

            # Verify results
            self.assertIsInstance(migrations, list)

    def test_extract_dependencies(self):
        """Test dependency extraction from migration files."""
        migration_content = '''
        dependencies = [
            ('auth', '0001_initial'),
            ('contenttypes', '0002_remove_content_type_name'),
        ]
        '''

        with patch('builtins.open', mock_open(read_data=migration_content)):
            deps = self.scanner._extract_dependencies(Path('/fake/path'))

        expected_deps = [('auth', '0001_initial'), ('contenttypes', '0002_remove_content_type_name')]
        self.assertEqual(deps, expected_deps)

    def test_extract_operations(self):
        """Test operation extraction from migration files."""
        migration_content = '''
        operations = [
            migrations.CreateModel(
                name='User',
                fields=[],
            ),
            migrations.AddField(
                model_name='user',
                name='email',
                field=models.EmailField(),
            ),
        ]
        '''

        with patch('builtins.open', mock_open(read_data=migration_content)):
            ops = self.scanner._extract_operations(Path('/fake/path'))

        expected_ops = ['CreateModel', 'AddField']
        self.assertEqual(ops, expected_ops)

    def test_has_existing_test(self):
        """Test checking for existing test files."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = True
            result = self.scanner._has_existing_test('testapp', '0001_initial')
            self.assertTrue(result)

            mock_exists.return_value = False
            result = self.scanner._has_existing_test('testapp', '0001_initial')
            self.assertFalse(result)


class TestFileGeneratorTest(TestCase):
    """Test the TestFileGenerator class."""

    def setUp(self):
        self.generator = TestFileGenerator()
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock template
        self.template_content = '''
class {migration_class_name}(TestCase):
    """Test for {app_label}.{migration_name}"""
    pass
        '''

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_generator_initialization(self):
        """Test that generator initializes properly."""
        self.assertIsNotNone(self.generator.template_path)

    def test_to_class_name_conversion(self):
        """Test migration name to class name conversion."""
        test_cases = [
            ('0001_initial', 'Test0001Initial'),
            ('0002_add_user_email', 'Test0002AddUserEmail'),
            ('0003_remove_old_field', 'Test0003RemoveOldField'),
        ]

        for migration_name, expected_class_name in test_cases:
            result = self.generator._to_class_name(migration_name)
            self.assertEqual(result, expected_class_name)

    def test_generate_test_file(self):
        """Test test file generation."""
        migration_info = {
            'app_label': 'testapp',
            'migration_name': '0001_initial',
            'dependencies': [('auth', '0001_initial')],
            'operations': ['CreateModel', 'AddField']
        }

        with patch.object(self.generator, '_load_template', return_value=self.template_content):
            output_path = self.generator.generate_test_file(migration_info, self.temp_dir)

        # Verify file was created
        self.assertTrue(output_path.exists())

        # Verify content
        with open(output_path, 'r') as f:
            content = f.read()

        self.assertIn('class Test0001Initial(TestCase):', content)
        self.assertIn('Test for testapp.0001_initial', content)

    def test_load_template(self):
        """Test template loading."""
        template_path = Path(self.temp_dir) / 'test_template.py'
        template_content = 'class {migration_class_name}(TestCase): pass'

        with open(template_path, 'w') as f:
            f.write(template_content)

        generator = TestFileGenerator(template_path)
        loaded_content = generator._load_template()

        self.assertEqual(loaded_content, template_content)