import os
import re
from pathlib import Path
from django.apps import apps
from django.db.migrations.loader import MigrationLoader
from django.conf import settings


class MigrationScanner:
    """Scans Django apps for migration files and extracts metadata."""

    def __init__(self):
        self.loader = MigrationLoader(None)

    def get_all_migrations(self):
        """Get all migration files across all apps."""
        migrations = []

        for app_label in apps.get_app_configs():
            app_config = apps.get_app_config(app_label)
            migrations_dir = Path(app_config.path) / "migrations"

            if migrations_dir.exists():
                migration_files = self._scan_migration_files(migrations_dir, app_label)
                migrations.extend(migration_files)

        return migrations

    def _scan_migration_files(self, migrations_dir, app_label):
        """Scan individual migration files in an app."""
        migrations = []

        for file_path in migrations_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue

            migration_name = file_path.stem

            # Skip if already has test
            if self._has_existing_test(app_label, migration_name):
                continue

            migration_info = {
                'app_label': app_label,
                'migration_name': migration_name,
                'file_path': file_path,
                'dependencies': self._extract_dependencies(file_path),
                'operations': self._extract_operations(file_path)
            }
            migrations.append(migration_info)

        return migrations

    def _has_existing_test(self, app_label, migration_name):
        """Check if test already exists for this migration."""
        app_config = apps.get_app_config(app_label)
        test_file = Path(app_config.path) / "tests" / "migrations" / f"test_{migration_name}.py"
        return test_file.exists()

    def _extract_dependencies(self, file_path):
        """Extract migration dependencies from file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Look for dependencies = [...] pattern
            dep_match = re.search(r'dependencies\s*=\s*\[(.*?)\]', content, re.DOTALL)
            if dep_match:
                deps_str = dep_match.group(1)
                # Extract tuples like ('app', '0001_initial')
                deps = re.findall(r'\([\'"](\w+)[\'"],\s*[\'"](\w+)[\'"]\)', deps_str)
                return deps
        except Exception:
            pass
        return []

    def _extract_operations(self, file_path):
        """Extract operation types from migration file."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Look for common operation patterns
            operations = []
            if 'CreateModel' in content:
                operations.append('CreateModel')
            if 'DeleteModel' in content:
                operations.append('DeleteModel')
            if 'AddField' in content:
                operations.append('AddField')
            if 'RemoveField' in content:
                operations.append('RemoveField')
            if 'AlterField' in content:
                operations.append('AlterField')
            if 'RunSQL' in content:
                operations.append('RunSQL')
            if 'RunPython' in content:
                operations.append('RunPython')

            return operations
        except Exception:
            pass
        return []


class TestFileGenerator:
    """Generates test files for migrations."""

    def __init__(self, template_path=None):
        if template_path is None:
            template_path = Path(__file__).parent / "templates" / "migration_test_template.py"
        self.template_path = template_path

    def generate_test_file(self, migration_info, output_dir):
        """Generate a test file for a specific migration."""
        template_content = self._load_template()

        # Replace template variables
        test_content = template_content.format(
            app_label=migration_info['app_label'],
            migration_name=migration_info['migration_name'],
            migration_class_name=self._to_class_name(migration_info['migration_name']),
            dependencies=repr(migration_info['dependencies']),
            operations=', '.join(migration_info['operations']) or 'None'
        )

        # Ensure output directory exists
        output_path = Path(output_dir) / f"test_{migration_info['migration_name']}.py"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write test file
        with open(output_path, 'w') as f:
            f.write(test_content)

        return output_path

    def _load_template(self):
        """Load the test template."""
        with open(self.template_path, 'r') as f:
            return f.read()

    def _to_class_name(self, migration_name):
        """Convert migration name to test class name."""
        # Convert 0001_initial to Test0001Initial
        parts = migration_name.split('_')
        class_name = 'Test' + ''.join(word.capitalize() for word in parts)
        return class_name