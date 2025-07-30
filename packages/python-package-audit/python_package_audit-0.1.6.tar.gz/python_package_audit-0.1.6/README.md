## <ins> Package Audit </ins>

Python Package Audit is a lightweight static analysis tool designed to detect unused Python packages <br>

*Warning - Ignored directories starting with "." or "_" !* <br>
*Warning - Unused package detection is not guaranteed to be accurate !* <br>
*Warning -  It is highly recommended to review the results carefully before removing any packages !* <br>

### <ins> Features </ins>

- Scans Python files to detect all imported modules
- Maps import names to actual installed PyPI packages
- Tracks both direct and transitive dependencies
- Flags packages that are installed but unused
- Provides optional JSON output for automation pipelines
- Ignores common noise (E.G. folders starting with "." or "_")
- Multithreaded for fast analysis of large projects

### <ins> Installation </ins>

You can install this package via PIP: pip install python-package-audit <br>

### <ins> Dependencies </ins>

This project requires the following Python packages:
- colorama — For colored terminal output
- pipdeptree — For analyzing package dependency trees

### <ins> Usage </ins>

python -m pkgaudit --project "/path/to/your/project-root-directory" <br>

### <ins> JSON Output </ins>

python -m pkgaudit --project "/path/to/your/project-root-directory" --json <br>

### <ins> Output - Text </ins>

```
[Installed Packages (28)]
build
certifi
charset-normalizer
colorama
docutils
id
idna
jaraco.classes
jaraco.context
jaraco.functools
keyring
markdown-it-py
mdurl
more-itertools
nh3
packaging
pipdeptree
pygments
pyproject_hooks
python-package-audit
pywin32-ctypes
readme_renderer
requests
requests-toolbelt
rfc3986
rich
twine
urllib3

[Used Packages (14)]
Package: ast, Count: 1, Resolve: None
Package: importlib, Count: 1, Resolve: None
Package: json, Count: 2, Resolve: None
Package: os, Count: 2, Resolve: None
Package: subprocess, Count: 1, Resolve: None
Package: sys, Count: 1, Resolve: None
Package: concurrent, Count: 1, Resolve: None
Package: threading, Count: 1, Resolve: None
Package: colorama, Count: 1, Resolve: colorama
Package: argparse, Count: 1, Resolve: None
Package: warnings, Count: 1, Resolve: None
Package: package_analyzer, Count: 2, Resolve: python-package-audit
Package: tempfile, Count: 1, Resolve: None
Package: unittest, Count: 2, Resolve: None

[Unused Packages (25)]
Package: mdurl, Resolve: mdurl
Package: nh3, Resolve: nh3
Package: markdown-it-py, Resolve: markdown-it-py
Package: requests-toolbelt, Resolve: requests-toolbelt
Package: jaraco.functools, Resolve: jaraco.functools
Package: id, Resolve: id
Package: twine, Resolve: twine
Package: charset-normalizer, Resolve: charset-normalizer
Package: rfc3986, Resolve: rfc3986
Package: jaraco.context, Resolve: jaraco.context
Package: pygments, Resolve: Pygments
Package: readme_renderer, Resolve: readme_renderer
Package: build, Resolve: build
Package: packaging, Resolve: packaging
Package: idna, Resolve: idna
Package: pywin32-ctypes, Resolve: pywin32-ctypes
Package: pyproject_hooks, Resolve: pyproject_hooks
Package: more-itertools, Resolve: more-itertools
Package: requests, Resolve: requests
Package: docutils, Resolve: docutils
Package: jaraco.classes, Resolve: jaraco.classes
Package: rich, Resolve: rich
Package: urllib3, Resolve: urllib3
Package: certifi, Resolve: certifi
Package: keyring, Resolve: keyring
```

### <ins> Output - JSON </ins>

```
{
    "installed_packages_count": 28,
    "used_packages_count": 14,
    "unused_packages_count": 25,
    "installed_packages": [
        "build",
        "certifi",
        "charset-normalizer",
        "colorama",
        "docutils",
        "id",
        "idna",
        "jaraco.classes",
        "jaraco.context",
        "jaraco.functools",
        "keyring",
        "markdown-it-py",
        "mdurl",
        "more-itertools",
        "nh3",
        "packaging",
        "pipdeptree",
        "pygments",
        "pyproject_hooks",
        "python-package-audit",
        "pywin32-ctypes",
        "readme_renderer",
        "requests",
        "requests-toolbelt",
        "rfc3986",
        "rich",
        "twine",
        "urllib3"
    ],
    "used_packages": {
        "argparse": {
            "count": 1,
            "resolve": null
        },
        "warnings": {
            "count": 1,
            "resolve": null
        },
        "package_analyzer": {
            "count": 2,
            "resolve": "python-package-audit"
        },
        "ast": {
            "count": 1,
            "resolve": null
        },
        "importlib": {
            "count": 1,
            "resolve": null
        },
        "json": {
            "count": 2,
            "resolve": null
        },
        "os": {
            "count": 2,
            "resolve": null
        },
        "subprocess": {
            "count": 1,
            "resolve": null
        },
        "sys": {
            "count": 1,
            "resolve": null
        },
        "concurrent": {
            "count": 1,
            "resolve": null
        },
        "threading": {
            "count": 1,
            "resolve": null
        },
        "colorama": {
            "count": 1,
            "resolve": "colorama"
        },
        "tempfile": {
            "count": 1,
            "resolve": null
        },
        "unittest": {
            "count": 2,
            "resolve": null
        }
    },
    "unused_packages": {
        "jaraco.context": {
            "resolve": "jaraco.context"
        },
        "markdown-it-py": {
            "resolve": "markdown-it-py"
        },
        "idna": {
            "resolve": "idna"
        },
        "readme_renderer": {
            "resolve": "readme_renderer"
        },
        "charset-normalizer": {
            "resolve": "charset-normalizer"
        },
        "urllib3": {
            "resolve": "urllib3"
        },
        "packaging": {
            "resolve": "packaging"
        },
        "build": {
            "resolve": "build"
        },
        "id": {
            "resolve": "id"
        },
        "rich": {
            "resolve": "rich"
        },
        "twine": {
            "resolve": "twine"
        },
        "rfc3986": {
            "resolve": "rfc3986"
        },
        "docutils": {
            "resolve": "docutils"
        },
        "pywin32-ctypes": {
            "resolve": "pywin32-ctypes"
        },
        "keyring": {
            "resolve": "keyring"
        },
        "mdurl": {
            "resolve": "mdurl"
        },
        "requests-toolbelt": {
            "resolve": "requests-toolbelt"
        },
        "jaraco.functools": {
            "resolve": "jaraco.functools"
        },
        "requests": {
            "resolve": "requests"
        },
        "certifi": {
            "resolve": "certifi"
        },
        "pygments": {
            "resolve": "Pygments"
        },
        "more-itertools": {
            "resolve": "more-itertools"
        },
        "pyproject_hooks": {
            "resolve": "pyproject_hooks"
        },
        "jaraco.classes": {
            "resolve": "jaraco.classes"
        },
        "nh3": {
            "resolve": "nh3"
        }
    },
    "errors": []
}
```
