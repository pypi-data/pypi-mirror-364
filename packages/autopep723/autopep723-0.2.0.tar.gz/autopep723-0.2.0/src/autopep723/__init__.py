import ast
import pkgutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Optional

from .logger import command, error, verbose

# Mapping for packages where import name differs from install name
IMPORT_TO_PACKAGE_MAP = {
    "PIL": "Pillow",
    "yaml": "PyYAML",
    "bs4": "beautifulsoup4",
    "sklearn": "scikit-learn",
    "skimage": "scikit-image",
    "cv2": "opencv-python",
    "serial": "pyserial",
    "usb": "pyusb",
    "Crypto": "pycryptodome",
    "OpenGL": "PyOpenGL",
    "setuptools_scm": "setuptools-scm",
    "flask_sqlalchemy": "Flask-SQLAlchemy",
    "flask_login": "Flask-Login",
    "flask_migrate": "Flask-Migrate",
    "flask_wtf": "Flask-WTF",
    "flask_mail": "Flask-Mail",
    "flask_cors": "Flask-Cors",
    "flask_jwt_extended": "Flask-JWT-Extended",
    "flask_restful": "Flask-RESTful",
    "flask_bcrypt": "Flask-Bcrypt",
    "psycopg2": "psycopg2-binary",
    "pyside2": "PySide2",
    "win32com": "pywin32",
    "Xlib": "python-xlib",
    "Levenshtein": "python-Levenshtein",
    "dash_bootstrap_components": "dash-bootstrap-components",
    "dash_table": "dash-table",
    "pandas_datareader": "pandas-datareader",
    "jupyter_core": "jupyter-core",
    "jupyter_client": "jupyter-client",
    "prometheus_client": "prometheus-client",
    "sqlalchemy_utils": "SQLAlchemy-Utils",
    "sqlalchemy_mixins": "sqlalchemy-mixins",
    "markdown_it": "markdown-it-py",
    "email_validator": "email-validator",
    "python_jose": "python-jose",
    "jwt": "PyJWT",
    "python_http_client": "python-http-client",
    "dateutil": "python-dateutil",
    "dotenv": "python-dotenv",
    "fitz": "PyMuPDF",
    "ConfigParser": "configparser",
}


def get_builtin_modules() -> set[str]:
    """Get a set of all built-in modules in Python."""
    builtin_modules = set(sys.builtin_module_names)

    # Add standard library modules
    for module_info in pkgutil.iter_modules():
        builtin_modules.add(module_info.name)

    return builtin_modules


def get_third_party_imports(file_path: Path) -> list[str]:
    """Parse a Python file and extract third-party imports.

    Args:
        file_path: Path to the Python file to analyze

    Returns:
        List of third-party package names
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except SyntaxError as e:
        error(f"Error parsing {file_path}: {e}")
        return []
    except Exception as e:
        error(f"Error reading {file_path}: {e}")
        return []

    builtin_modules = get_builtin_modules()
    all_imports = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                module_name = name.name.split(".")[0]
                all_imports.add(module_name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            module_name = node.module.split(".")[0]
            all_imports.add(module_name)

    # Filter out built-in modules and convert to package names
    third_party_imports = []
    for imp in sorted(all_imports):
        if imp not in builtin_modules:
            package_name = IMPORT_TO_PACKAGE_MAP.get(imp, imp)
            third_party_imports.append(package_name)

    return sorted(set(third_party_imports))


def generate_pep723_metadata(dependencies: list[str], python_version: str = ">=3.13") -> str:
    """Generate PEP 723 metadata block.

    Args:
        dependencies: List of package dependencies
        python_version: Required Python version

    Returns:
        PEP 723 metadata as string
    """
    if not dependencies:
        metadata = f'''# /// script
# requires-python = "{python_version}"
# ///'''
    else:
        deps_str = ",\n#     ".join(f'"{dep}"' for dep in dependencies)
        metadata = f'''# /// script
# requires-python = "{python_version}"
# dependencies = [
#     {deps_str},
# ]
# ///'''

    return metadata


def has_existing_metadata(content: str) -> bool:
    """Check if the file already has PEP 723 metadata."""
    return "# /// script" in content and "# ///" in content


def extract_existing_metadata(content: str) -> tuple[str, str, str]:
    """Extract existing metadata and return (before, metadata, after) parts."""
    lines = content.splitlines(keepends=True)
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if "# /// script" in line:
            start_idx = i
        elif start_idx is not None and "# ///" in line and i > start_idx:
            end_idx = i + 1
            break

    if start_idx is not None and end_idx is not None:
        before = "".join(lines[:start_idx])
        metadata = "".join(lines[start_idx:end_idx])
        after = "".join(lines[end_idx:])
        return before, metadata, after

    return content, "", ""


def update_file_with_metadata(file_path: Path, metadata: str) -> None:
    """Update the file with new PEP 723 metadata."""
    content = file_path.read_text(encoding="utf-8")

    if has_existing_metadata(content):
        before, _, after = extract_existing_metadata(content)
        new_content = before + metadata + "\n" + after
    else:
        # Add metadata at the beginning, after shebang if present
        lines = content.splitlines(keepends=True)
        if lines and lines[0].startswith("#!"):
            new_content = lines[0] + metadata + "\n" + "".join(lines[1:])
        else:
            new_content = metadata + "\n" + content

    file_path.write_text(new_content, encoding="utf-8")


def run_with_uv(script_path: Path, dependencies: list[str], script_args: Optional[list[str]] = None) -> None:
    """Run the script using uv run with dependencies and script arguments."""
    if script_args is None:
        script_args = []

    cmd = ["uv", "run"]

    for dep in dependencies:
        cmd.extend(["--with", dep])

    cmd.append(str(script_path))

    # Add script arguments after the script path
    cmd.extend(script_args)

    command(" ".join(cmd))

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        if e.returncode != 0:
            error(f"Script execution failed with exit code {e.returncode}")
        else:
            error(f"Error running script: {e}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        error("'uv' command not found. Please install uv first.")
        error("Install with: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)


def check_uv_available() -> bool:
    """Check if uv is available in the system."""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def has_pep723_metadata(script_path: Path) -> bool:
    """Check if script already has PEP 723 metadata."""
    try:
        content = script_path.read_text(encoding="utf-8")
        return has_existing_metadata(content)
    except Exception:
        return False


def is_url(path: str) -> bool:
    """Check if the given path is a valid URL.

    Args:
        path: String to check

    Returns:
        True if path is a URL, False otherwise
    """
    try:
        result = urllib.parse.urlparse(path)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def download_script(url: str) -> Path:
    """Download a script from URL to a temporary file.

    Args:
        url: URL to download from

    Returns:
        Path to the downloaded temporary file

    Raises:
        Exception: If download fails
    """

    try:
        verbose(f"📥 Downloading script from: {url}")

        # Download the file
        with urllib.request.urlopen(url) as response:
            content = response.read().decode("utf-8")

        # Create a temporary file with .py extension
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="autopep723_", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        verbose(f"💾 Script downloaded to: {temp_path}")
        return temp_path

    except Exception as e:
        error(f"Error downloading script from {url}: {e}")
        sys.exit(1)


def resolve_script_path(script_input: str) -> Path:
    """Resolve script input to a local file path.

    If input is a URL, downloads it to a temporary file.
    Otherwise, returns the path as-is.

    Args:
        script_input: File path or URL

    Returns:
        Path to local script file
    """
    if is_url(script_input):
        return download_script(script_input)
    else:
        return Path(script_input)


def main() -> None:
    """Main entry point for autopep723."""
    from .cli import (
        create_parser,
        get_script_args_from_args,
        get_script_path_from_args,
        is_default_run_command,
        should_show_help,
    )
    from .commands import add_command, check_command, run_script_command
    from .logger import init_logger

    # Initialize logger with default settings first
    init_logger(verbose=False)

    # Handle help case
    if should_show_help():
        parser = create_parser()
        parser.print_help()
        sys.exit(1)

    # Handle default run command (script execution)
    if is_default_run_command():
        # Check if verbose flag is present in args
        verbose = "-v" in sys.argv or "--verbose" in sys.argv

        # Re-initialize logger with verbose setting if needed
        if verbose:
            init_logger(verbose=True)

        script_path = get_script_path_from_args()
        script_args = get_script_args_from_args()
        run_script_command(script_path, script_args)
        return

    # Handle subcommands
    parser = create_parser()
    args = parser.parse_args()

    # Re-initialize logger with verbose flag from args if needed
    if args.verbose:
        init_logger(verbose=True)

    if args.command == "check":
        check_command(args.script, args.python_version)
    elif args.command == "add":
        add_command(args.script, args.python_version)


if __name__ == "__main__":
    main()
