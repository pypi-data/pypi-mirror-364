import ast
import importlib.metadata
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from colorama import Fore, Style

EXCLUDED_PACKAGES = {'pipdeptree'}


class PackageAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.errors = []
        self.thread_lock = Lock()

    # noinspection PyMethodMayBeStatic
    def _find_imports_in_file(self, filepath) -> dict:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as fd:
            tree = ast.parse(fd.read(), filename=filepath)

        usage_counts = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    base = alias.name.split('.')[0]
                    usage_counts[base] = usage_counts.get(base, 0) + 1  # noqa
            elif isinstance(node, ast.ImportFrom) and node.module:  # noqa
                base = node.module.split('.')[0]
                usage_counts[base] = usage_counts.get(base, 0) + 1
        return usage_counts

    # noinspection PyMethodMayBeStatic
    def _resolve_import_to_package(self, import_name: str) -> str:
        """
        Tries to resolve an import name to its installed PyPI package name
        using importlib.metadata.
        """
        try:
            distribution = importlib.metadata.distribution(import_name)
            return distribution.metadata['Name']
        except importlib.metadata.PackageNotFoundError:
            for dist in importlib.metadata.distributions():
                # noinspection PyBroadException
                try:
                    top_level = dist.read_text('top_level.txt')
                    if top_level:
                        modules = [line.strip() for line in top_level.splitlines()]
                        if import_name in modules:
                            return dist.metadata['Name']
                except Exception:
                    continue
            return ''

    def _get_used_packages(self) -> dict:
        total_usage = {}
        py_files = []

        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if not (d.startswith('.') or d.startswith('_'))]
            for file in files:
                if file.lower().endswith('.py'):
                    py_files.append(os.path.join(root, file))

        def analyze_file(filepath) -> dict:
            try:
                return self._find_imports_in_file(filepath)
            except SyntaxError as e:
                self.errors.append(f'Skipping file with syntax error: {filepath}, error {e}')
                return {}
            except Exception as e:
                self.errors.append(f'Error parsing file {filepath}: {e}')
                return {}

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(analyze_file, f) for f in py_files]
            for future in as_completed(futures):
                file_usage = future.result()
                for pkg, count in file_usage.items():
                    total_usage[pkg] = total_usage.get(pkg, 0) + count

        # Cache for resolved package names
        resolve_cache = {}

        resolved_usage = {}
        for pkg, count in total_usage.items():
            if pkg not in resolve_cache:
                resolve_cache[pkg] = self._resolve_import_to_package(pkg)
            resolved_usage[pkg] = {
                'count': count,
                'resolve': resolve_cache[pkg] or None
            }

        return resolved_usage

    # noinspection PyMethodMayBeStatic
    def _get_installed_packages(self) -> set:
        result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], capture_output=True, text=True, check=True)
        return set(line.split('==')[0].lower() for line in result.stdout.splitlines() if line)

    def _get_package_dependencies(self) -> dict:
        """
        Returns a dict mapping package names to a set of their direct dependencies
        Uses pipdeptree JSON output
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pipdeptree', '--json-tree'],
                capture_output=True,
                text=True,
                check=True
            )
            tree = json.loads(result.stdout)
        except Exception as e:
            self.errors.append(f'Failed to run pipdeptree: {e}')
            return {}

        dependencies = {}
        visited = set()

        def process_node(node):
            pkg = node.get('package')
            if not pkg:
                return
            pkg_name = pkg.get('key')
            if not pkg_name:
                return

            if pkg_name in visited:
                return
            visited.add(pkg_name)

            deps = node.get('dependencies', [])
            dep_names = set()
            for dep in deps:
                dep_pkg = dep.get('package')
                if dep_pkg and 'key' in dep_pkg:
                    dep_names.add(dep_pkg['key'])
                process_node(dep)

            dependencies[pkg_name] = dep_names

        for root_node in tree:
            process_node(root_node)

        return dependencies

    def analyze(self, json_output: bool = False) -> None:
        installed_packages = self._get_installed_packages()
        used_packages = self._get_used_packages()
        dependencies = self._get_package_dependencies()

        # Compute all dependencies of used packages (recursively)
        def get_all_dependencies(package: str, seen: set = None):
            if seen is None:
                seen = set()
            for dep in dependencies.get(package, []):
                if dep not in seen:
                    seen.add(dep)
                    get_all_dependencies(dep, seen)
            return seen

        used_import_names = set(used_packages.keys())
        resolve_cache = {}

        # Collect resolved PyPI package names for all used import names
        resolved_used_names = set()
        for import_name in used_import_names:
            resolved = self._resolve_import_to_package(import_name)
            resolve_cache[import_name] = resolved
            if resolved:
                resolved_used_names.add(resolved.lower())

        # Compute transitive dependencies of resolved packages
        all_deps = set()
        for pkg in resolved_used_names:
            all_deps.update(get_all_dependencies(pkg))

        effectively_used = used_import_names.union(resolved_used_names, all_deps)  # noqa
        unused_packages = installed_packages - effectively_used - EXCLUDED_PACKAGES

        ret = dict()

        # Count
        ret['installed_packages_count'] = len(installed_packages)
        ret['used_packages_count'] = len(used_packages)
        ret['unused_packages_count'] = len(unused_packages)

        # Data
        ret['installed_packages'] = sorted(installed_packages)
        ret['used_packages'] = used_packages
        ret['unused_packages'] = {
            pkg: {
                'resolve': resolve_cache.setdefault(pkg, self._resolve_import_to_package(pkg)) or None
            } for pkg in unused_packages
        }

        # Error
        ret['errors'] = self.errors

        # Pretty Text
        if json_output:

            print(json.dumps(ret, indent=4) + '\n')
        else:
            ret['used_packages'] = [
                f'Package: {k}, Count: {v["count"]}, Resolve: {v["resolve"]}' for k, v in ret['used_packages'].items()
            ]
            ret['unused_packages'] = [
                f'Package: {k}, Resolve: {v["resolve"]}' for k, v in ret['unused_packages'].items()
            ]

            msg = (
                '[Warning] Ignored directories starting with "." or "_" !',
                '[Warning] Unused package detection is not guaranteed to be accurate !',
                '[Warning] It is highly recommended to review the results carefully before removing any packages !'
            )

            print(Fore.YELLOW + Style.BRIGHT + '\n'.join(msg) + '\n' + Fore.RESET)

            print(f'[Installed Packages ({ret["installed_packages_count"]})]')
            print('\n'.join(ret['installed_packages']) + '\n')

            print(f'[Used Packages ({ret["used_packages_count"]})]')
            print('\n'.join(ret['used_packages']) + '\n')

            print(f'[Unused Packages ({ret["unused_packages_count"]})]')
            print('\n'.join(ret['unused_packages']) + '\n')
