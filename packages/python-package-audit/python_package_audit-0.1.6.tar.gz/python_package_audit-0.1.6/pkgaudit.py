import argparse
import warnings

from package_analyzer import PackageAnalyzer

warnings.filterwarnings('ignore', category=SyntaxWarning)

parser = argparse.ArgumentParser(description='Package Audit')
parser.add_argument(
    '--project_root_directory',
    type=str,
    required=True,
    help='Full path to the project root directory'
)
parser.add_argument(
    '--json',
    action='store_true',
    default=False,
    help='Enable JSON output format'
)

args = parser.parse_args()
package_analyzer = PackageAnalyzer(project_path=args.project_root_directory)
package_analyzer.analyze(json_output=args.json)



