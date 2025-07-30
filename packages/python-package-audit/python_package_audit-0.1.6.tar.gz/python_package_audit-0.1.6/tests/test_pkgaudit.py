import json
import os
import tempfile
import unittest
from unittest.mock import patch, MagicMock

from package_analyzer import PackageAnalyzer


class TestPackageAnalyzer(unittest.TestCase):
    def test_find_imports_in_file_simple(self):
        test_code = 'import os\nimport sys\nfrom collections import defaultdict'
        with tempfile.NamedTemporaryFile('w+', suffix='.py', delete=False) as temp:
            temp.write(test_code)
            temp_path = temp.name

        analyzer = PackageAnalyzer(project_path='.')
        imports = analyzer._find_imports_in_file(temp_path)
        os.unlink(temp_path)

        expected = {'os': 1, 'sys': 1, 'collections': 1}
        self.assertEqual(imports, expected)

    @patch('importlib.metadata.distribution')
    def test_resolve_import_to_package(self, mock_distribution):
        mock_dist = MagicMock()
        mock_dist.metadata = {'Name': 'requests'}
        mock_distribution.return_value = mock_dist

        analyzer = PackageAnalyzer(project_path='.')
        self.assertEqual(analyzer._resolve_import_to_package('requests').lower(), 'requests')

    @patch('subprocess.run')
    def test_get_installed_packages(self, mock_run):
        mock_run.return_value.stdout = 'requests==2.31.0\nflask==2.3.3\n'
        mock_run.return_value.returncode = 0

        analyzer = PackageAnalyzer(project_path='.')
        packages = analyzer._get_installed_packages()
        self.assertEqual(packages, {'requests', 'flask'})

    @patch('subprocess.run')
    def test_get_package_dependencies(self, mock_run):
        fake_json = json.dumps([
            {
                'package': {'key': 'flask'},
                "dependencies": [{'package': {'key': 'click'}}]
            },
            {
                "package": {'key': 'click'},
                "dependencies": []
            }
        ])
        mock_run.return_value.stdout = fake_json
        mock_run.return_value.returncode = 0  # noqa

        analyzer = PackageAnalyzer(project_path='.')
        deps = analyzer._get_package_dependencies()
        self.assertEqual(deps, {"flask": {"click"}, "click": set()})
