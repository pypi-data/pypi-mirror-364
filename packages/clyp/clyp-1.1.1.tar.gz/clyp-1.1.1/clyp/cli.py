import argparse
import sys
import os
import traceback
import shutil
import importlib.machinery
import json
import platform
import zipfile
import tempfile
import glob
import hashlib
import concurrent.futures
from setuptools import setup
from Cython.Build import cythonize
from clyp import __version__
from clyp.transpiler import parse_clyp
from clyp.formatter import format_clyp_code
from .importer import find_clyp_imports


def calculate_sha256(file_path):
    """Calculates the SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_cache_dir(project_root):
    """Returns the path to the cache directory."""
    return os.path.join(project_root, ".clyp-cache")


def get_cache_path(project_root, module_name):
    """Returns the path to the cache file for a given module."""
    cache_dir = get_cache_dir(project_root)
    return os.path.join(cache_dir, f"{module_name}.json")


def read_cache(project_root, module_name):
    """Reads cache data for a given module."""
    cache_path = get_cache_path(project_root, module_name)
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


def write_cache(project_root, module_name, data):
    """Writes cache data for a given module."""
    cache_dir = get_cache_dir(project_root)
    os.makedirs(cache_dir, exist_ok=True)
    cache_path = get_cache_path(project_root, module_name)
    with open(cache_path, "w") as f:
        json.dump(data, f, indent=4)


def resolve_import_path(import_name, current_file_path):
    """Resolves the absolute path of a Clyp import."""
    module_path = import_name.replace(".", os.path.sep) + ".clyp"

    search_paths = [os.path.dirname(current_file_path)] + sys.path

    for path in search_paths:
        potential_path = os.path.join(path, module_path)
        if os.path.exists(potential_path):
            return os.path.abspath(potential_path)
    return None


class Log:
    """A simple logger with color support."""

    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    _supports_color = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()

    @classmethod
    def _print(cls, color, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{color}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)

    @classmethod
    def info(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)

    @classmethod
    def success(cls, *args, **kwargs):
        cls._print(cls.GREEN, *args, **kwargs)

    @classmethod
    def warn(cls, *args, **kwargs):
        cls._print(cls.WARNING, *args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs):
        cls._print(cls.FAIL, *args, **kwargs)

    @classmethod
    def bold(cls, *args, **kwargs):
        msg = "".join(map(str, args))
        if cls._supports_color:
            print(f"{cls.BOLD}{msg}{cls.ENDC}", **kwargs)
        else:
            print(msg, **kwargs)

    @classmethod
    def traceback_header(cls, *args, **kwargs):
        cls._print(cls.BOLD, *args, **kwargs)

    @classmethod
    def traceback_location(cls, *args, **kwargs):
        cls._print(cls.BLUE, *args, **kwargs)

    @classmethod
    def traceback_code(cls, *args, **kwargs):
        cls._print(cls.CYAN, *args, **kwargs)


def build_module(file_path, project_root, cache_dir, force_rebuild=False, nthreads=1):
    """
    Builds a single Clyp module, returning metadata and path to the compiled artifact.
    Returns None if the module is up-to-date.
    """
    module_name = os.path.splitext(os.path.basename(file_path))[0]

    # Check cache
    cache_data = read_cache(project_root, module_name)
    source_hash = calculate_sha256(file_path)

    if (
        not force_rebuild
        and cache_data
        and cache_data.get("source_hash") == source_hash
    ):
        cached_module_path = os.path.join(cache_dir, cache_data["module_filename"])
        if os.path.exists(cached_module_path):
            Log.info(f"Module '{module_name}' is up to date.")
            return {
                "module_name": module_name,
                "metadata": cache_data["metadata"],
                "artifact_path": cached_module_path,
            }

    Log.info(f"Building module from '{file_path}'...")
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except (IOError, UnicodeDecodeError) as e:
            Log.error(f"Error reading file {file_path}: {e}")
            return None

        python_code = parse_clyp(clyp_code, file_path)
        if isinstance(python_code, tuple):
            python_code = python_code[0]

        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        pyx_file = f"{module_name}.pyx"
        with open(pyx_file, "w", encoding="utf-8") as f:
            f.write(python_code)

        original_argv = sys.argv
        sys.argv = ["setup.py", "build_ext", "--inplace"]
        try:
            setup(
                name=module_name,
                ext_modules=cythonize(pyx_file, quiet=True, nthreads=nthreads),
                script_args=["build_ext", "--inplace"],
            )
        finally:
            sys.argv = original_argv
            os.chdir(original_cwd)

        # Locate compiled modules using dynamic extension suffixes
        suffixes = importlib.machinery.EXTENSION_SUFFIXES
        compiled_files = []
        for suffix in suffixes:
            compiled_files.extend(
                glob.glob(os.path.join(temp_dir, f"{module_name}*{suffix}"))
            )
        # Fallback to legacy patterns if none found
        if not compiled_files:
            compiled_files = glob.glob(
                os.path.join(temp_dir, f"{module_name}.*.so")
            ) + glob.glob(os.path.join(temp_dir, f"{module_name}.*.pyd"))
        if not compiled_files:
            Log.error(f"Build failed for {module_name}. No compiled module found.")
            return None
        compiled_module_path = compiled_files[0]

        cached_module_filename = os.path.basename(compiled_module_path)
        cached_module_dest = os.path.join(cache_dir, cached_module_filename)
        shutil.move(compiled_module_path, cached_module_dest)

        module_checksum = calculate_sha256(cached_module_dest)

        metadata = {
            "clyp_version": __version__,
            "python_version": sys.version,
            "platform": sys.platform,
            "architecture": platform.machine(),
            "module_filename": os.path.basename(cached_module_dest),
            "checksum": module_checksum,
            "source_file": os.path.basename(file_path),
        }

        new_cache_data = {
            "source_hash": source_hash,
            "module_filename": cached_module_filename,
            "metadata": metadata,
        }
        write_cache(project_root, module_name, new_cache_data)

        return {
            "module_name": module_name,
            "metadata": metadata,
            "artifact_path": cached_module_dest,
        }


def build_project(config, project_root, force_rebuild=False, jobs=1, clean=False):
    """Builds a Clyp project based on the given configuration."""
    build_dir = os.path.join(project_root, config.get("build_dir", "build"))
    cache_dir = get_cache_dir(project_root)
    # Clean build and cache directories if requested
    if clean:
        shutil.rmtree(build_dir, ignore_errors=True)
        shutil.rmtree(cache_dir, ignore_errors=True)
    os.makedirs(build_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)

    entry_point = os.path.join(project_root, config["entry"])
    project_name = config.get(
        "name", os.path.splitext(os.path.basename(entry_point))[0]
    )

    # Dependency resolution
    files_to_process = [os.path.abspath(entry_point)]
    processed_files = set()
    all_dependencies = []

    while files_to_process:
        current_file = files_to_process.pop(0)
        if current_file in processed_files:
            continue

        processed_files.add(current_file)
        all_dependencies.append(current_file)

        imports = find_clyp_imports(current_file)
        for imp in imports:
            resolved_path = resolve_import_path(imp, current_file)
            if resolved_path and resolved_path not in processed_files:
                files_to_process.append(resolved_path)

    Log.info(f"Found {len(all_dependencies)} modules to build.")

    built_artifacts = []
    # Build dependencies, possibly in parallel
    if jobs and jobs > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=jobs) as executor:
            future_to_path = {
                executor.submit(
                    build_module, fp, project_root, cache_dir, force_rebuild, jobs
                ): fp
                for fp in all_dependencies
            }
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                artifact_info = future.result()
                if artifact_info:
                    built_artifacts.append(artifact_info)
                else:
                    Log.error(f"Failed to build dependency: {path}. Aborting.")
                    sys.exit(1)
    else:
        for file_path in all_dependencies:
            artifact_info = build_module(
                file_path, project_root, cache_dir, force_rebuild, jobs
            )
            if artifact_info:
                built_artifacts.append(artifact_info)
            else:
                Log.error(f"Failed to build dependency: {file_path}. Aborting.")
                sys.exit(1)

    if not built_artifacts:
        Log.info("No modules needed to be rebuilt. Project is up to date.")
        return

    # Packaging
    clb_file_path = os.path.join(build_dir, f"{project_name}.clb")
    Log.info(f"Packaging project into '{clb_file_path}'...")

    package_metadata = {
        "clyp_version": __version__,
        "entry_module": os.path.splitext(os.path.basename(entry_point))[0],
        "modules": {art["module_name"]: art["metadata"] for art in built_artifacts},
    }

    with zipfile.ZipFile(clb_file_path, "w") as zf:
        zf.writestr("metadata.json", json.dumps(package_metadata, indent=4))
        for art in built_artifacts:
            zf.write(art["artifact_path"], arcname=art["metadata"]["module_filename"])

    Log.success(f"Build successful! Output is '{clb_file_path}'.")


def main():
    parser = argparse.ArgumentParser(description="Clyp CLI tool.")
    parser.add_argument(
        "--version", action="store_true", help="Display the version of Clyp."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # go command
    go_parser = subparsers.add_parser(
        "go", help="Transpile and run a Clyp file on the fly."
    )
    go_parser.add_argument("file", type=str, help="Path to the Clyp file to execute.")
    go_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to pass to the Clyp script."
    )

    # build command
    build_parser = subparsers.add_parser("build", help="Build a Clyp file or project.")
    build_parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="Path to the Clyp file to build. If omitted, builds the project in the current directory.",
    )
    build_parser.add_argument(
        "--force", action="store_true", help="Force a rebuild, ignoring any cache."
    )
    build_parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=1,
        help="Number of parallel build jobs (default: 1).",
    )  # New option for parallel builds
    build_parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build directory and cache before building.",
    )  # New option to clean before build

    # run command
    run_parser = subparsers.add_parser("run", help="Run a built Clyp module.")
    run_parser.add_argument("file", type=str, help="Path to the built module to run.")
    run_parser.add_argument(
        "args", nargs=argparse.REMAINDER, help="Arguments to pass to the Clyp module."
    )

    # init command
    init_parser = subparsers.add_parser("init", help="Initialize a new Clyp project.")
    init_parser.add_argument("name", type=str, help="The name of the project.")

    # format command
    format_parser = subparsers.add_parser(
        "format", help="Format a Clyp file (overwrites by default)."
    )
    format_parser.add_argument(
        "file", type=str, help="Path to the Clyp file to format."
    )
    format_parser.add_argument(
        "--print",
        action="store_true",
        help="Print formatted code instead of overwriting.",
    )
    format_parser.add_argument(
        "--no-write",
        action="store_true",
        help="Do not overwrite the file (alias for --print).",
    )

    # py2clyp command (Python to Clyp transpiler with many options)
    py2clyp_parser = subparsers.add_parser(
        "py2clyp", help="Transpile Python code to Clyp with advanced options."
    )
    py2clyp_parser.add_argument(
        "file", type=str, help="Path to the Python file to transpile."
    )
    py2clyp_parser.add_argument(
        "-o", "--output", type=str, default=None, help="Output file for Clyp code."
    )
    py2clyp_parser.add_argument(
        "--print", action="store_true", help="Print transpiled Clyp code to stdout."
    )
    py2clyp_parser.add_argument(
        "--format", action="store_true", help="Format the output Clyp code."
    )
    py2clyp_parser.add_argument(
        "--diff",
        action="store_true",
        help="Show a diff between the Python and Clyp code.",
    )
    py2clyp_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite the input Python file with Clyp code.",
    )
    py2clyp_parser.add_argument(
        "--check",
        action="store_true",
        help="Check if the file can be transpiled (dry run, no output).",
    )
    py2clyp_parser.add_argument(
        "--quiet", action="store_true", help="Suppress non-error output."
    )
    py2clyp_parser.add_argument(
        "--no-format", action="store_true", help="Do not format the output."
    )
    py2clyp_parser.add_argument(
        "--stats",
        action="store_true",
        help="Show statistics about the transpilation (lines, tokens, etc.).",
    )

    # clean command
    clean_parser = subparsers.add_parser(
        "clean", help="Remove build artifacts and cache."
    )
    clean_parser.add_argument(
        "--all",
        action="store_true",
        help="Remove all build and cache directories in subfolders.",
    )

    # check command
    check_parser = subparsers.add_parser(
        "check", help="Check a Clyp file or project for syntax errors."
    )
    check_parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="Clyp file or project to check. If omitted, checks the project in the current directory.",
    )

    # deps command
    deps_parser = subparsers.add_parser(
        "deps", help="Show the dependency tree for a Clyp file or project."
    )
    deps_parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="Clyp file or project to analyze.",
    )

    args = parser.parse_args()

    def get_clyp_line_for_py(py_line, line_map, clyp_lines):
        if not line_map or not clyp_lines:
            return "?", ""
        mapped_lines = sorted(line_map.keys())
        prev = None
        for ml in mapped_lines:
            if ml > py_line:
                break
            prev = ml
        if prev is not None:
            clyp_line = line_map[prev]
            if 0 <= clyp_line - 1 < len(clyp_lines):
                return clyp_line, clyp_lines[clyp_line - 1]
            if clyp_lines:
                return len(clyp_lines), clyp_lines[-1]
        return "?", ""

    if args.version:
        print(f"{__version__}")
        sys.exit(0)

    if not args.command:
        # If a file is provided without a command, default to 'go' for backward compatibility
        # To do this, we need to re-parse args a bit differently.
        # A bit of a hack, but it preserves the old `clyp <file>` behavior.
        if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
            args.command = "go"
            args.file = sys.argv[1]
        else:
            parser.print_help()
            sys.exit(0)

    if args.command == "go":
        try:
            file_path = os.path.abspath(args.file)
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except FileNotFoundError:
            Log.error(f"File {args.file} not found.", file=sys.stderr)
            sys.exit(1)
        except (IOError, UnicodeDecodeError) as e:
            Log.error(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            Log.error(
                f"Unexpected error reading file {args.file}: {e}", file=sys.stderr
            )
            sys.exit(1)
        try:
            result = parse_clyp(clyp_code, file_path, return_line_map=True)
        except Exception as e:
            Log.error(f"{type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        if isinstance(result, tuple):
            python_code, line_map, clyp_lines = result
        else:
            python_code = result
            line_map = None
            clyp_lines = None
        # Set sys.argv for the script
        sys.argv = [file_path] + (args.args if hasattr(args, "args") else [])
        try:
            exec(python_code, {"__name__": "__main__", "__file__": file_path})
        except SyntaxError as e:
            py_line = e.lineno
            Log.traceback_header(
                "\nTraceback (most recent call last):", file=sys.stderr
            )
            clyp_line, code = get_clyp_line_for_py(py_line, line_map, clyp_lines)
            Log.traceback_location(
                f"  File '{args.file}', line {clyp_line}", file=sys.stderr
            )
            Log.traceback_code(f"    {code}", file=sys.stderr)
            Log.warn(f"(Python error at transpiled line {py_line})", file=sys.stderr)
            Log.error(f"{type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            tb = traceback.extract_tb(sys.exc_info()[2])
            Log.traceback_header(
                "\nTraceback (most recent call last):", file=sys.stderr
            )
            # Find all Clyp frames
            clyp_frame_indices = [
                idx for idx, frame in enumerate(tb) if frame.filename == "<string>"
            ]
            last_clyp_frame_idx = clyp_frame_indices[-1] if clyp_frame_indices else None
            for idx, frame in enumerate(tb):
                if frame.filename == "<string>":
                    py_line = frame.lineno
                    clyp_line, code = get_clyp_line_for_py(
                        py_line, line_map, clyp_lines
                    )
                    marker = ">>>" if idx == last_clyp_frame_idx else "   "
                    Log.traceback_location(
                        f"{marker} File '{args.file}', line {clyp_line}",
                        file=sys.stderr,
                    )
                    # Show a few lines of Clyp context for each frame
                    if clyp_lines and clyp_line != "?":
                        start = max(0, clyp_line - 3)
                        end = min(len(clyp_lines), clyp_line + 2)
                        for i in range(start, end):
                            pointer = "->" if (i + 1) == clyp_line else "  "
                            Log.traceback_code(
                                f"{pointer} {i + 1}: {clyp_lines[i]}", file=sys.stderr
                            )
                    else:
                        Log.traceback_code(f"    {code}", file=sys.stderr)
                else:
                    Log.traceback_location(
                        f"    File '{frame.filename}', line {frame.lineno}",
                        file=sys.stderr,
                    )
                    Log.traceback_code(f"      {frame.line}", file=sys.stderr)
            Log.error(f"{type(e).__name__}: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.command == "build":
        if args.file:
            # Build a single file
            file_path = os.path.abspath(args.file)
            config = {
                "entry": file_path,
                "name": os.path.splitext(os.path.basename(file_path))[0],
            }
            build_project(
                config,
                os.path.dirname(file_path) or os.getcwd(),
                force_rebuild=args.force,
                jobs=args.jobs,
                clean=args.clean,
            )
        else:
            # Build a project
            project_root = os.getcwd()
            config_path = os.path.join(project_root, "clyp.json")
            if not os.path.exists(config_path):
                Log.error(
                    "No 'clyp.json' found in the current directory. To build a project, either run 'clyp init' or specify a file to build."
                )
                sys.exit(1)

            with open(config_path, "r") as f:
                config = json.load(f)

            build_project(
                config,
                project_root,
                force_rebuild=args.force,
                jobs=args.jobs,
                clean=args.clean,
            )

    elif args.command == "run":
        clb_path = os.path.abspath(args.file)
        if not clb_path.endswith(".clb"):
            Log.error(
                f"Error: The 'run' command expects a .clb file, but got '{args.file}'.",
                file=sys.stderr,
            )
            sys.exit(1)

        temp_dir = tempfile.mkdtemp()
        all_modules_meta = None  # Ensure variable is always defined
        try:
            with zipfile.ZipFile(clb_path, "r") as zf:
                # Extract and read metadata
                zf.extract("metadata.json", temp_dir)
                with open(os.path.join(temp_dir, "metadata.json"), "r") as f:
                    metadata = json.load(f)

                # Verify environment
                if metadata["clyp_version"] != __version__:
                    Log.warn(
                        f"Warning: Clyp version mismatch detected. "
                        f"This file was built with Clyp {metadata['clyp_version']}, "
                        f"but you are running Clyp {__version__}. "
                        f"Transpiled code may still work, but incompatibilities could exist."
                    )

                entry_module_name = metadata.get("entry_module")
                if not entry_module_name:
                    Log.error(
                        "Error: Invalid .clb file. Entry module not specified in metadata.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                all_modules_meta = metadata.get("modules", {})
                if not all_modules_meta:
                    Log.error(
                        "Error: Invalid .clb file. No modules found in metadata.",
                        file=sys.stderr,
                    )
                    sys.exit(1)

                # Extract all modules
                for module_name, module_meta in all_modules_meta.items():
                    module_filename = module_meta["module_filename"]
                    zf.extract(module_filename, temp_dir)

                    # Verify checksum
                    module_path = os.path.join(temp_dir, module_filename)
                    if "checksum" in module_meta:
                        expected_checksum = module_meta["checksum"]
                        actual_checksum = calculate_sha256(module_path)
                        if expected_checksum != actual_checksum:
                            Log.error(
                                f"Error: Checksum mismatch for module '{module_name}'. The file is corrupted.",
                                file=sys.stderr,
                            )
                            sys.exit(1)
                    else:
                        Log.warn(
                            f"Warning: No checksum for module '{module_name}'. Skipping integrity check.",
                            file=sys.stderr,
                        )

                sys.path.insert(0, temp_dir)
                # Set sys.argv for the module
                sys.argv = [clb_path] + (args.args if hasattr(args, "args") else [])
                # Import the main module to run it
                importlib.import_module(entry_module_name)

        except FileNotFoundError:
            Log.error(
                f"Error: '{args.file}' not found or is not a valid .clb file.",
                file=sys.stderr,
            )
            sys.exit(1)
        except (ImportError, KeyError):
            Log.error(
                f"Error: Could not import module from {args.file}. Make sure it is a valid and compatible Clyp build.",
                file=sys.stderr,
            )
            sys.exit(1)
        except Exception as e:
            Log.error(f"Error running module: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            # Clean up for Windows by releasing the module lock
            if all_modules_meta is not None:
                for module_name in all_modules_meta.keys():
                    if module_name in sys.modules:
                        del sys.modules[module_name]

            # Force garbage collection to release file handles
            import gc

            gc.collect()

            if temp_dir in sys.path:
                sys.path.remove(temp_dir)

            # Now, it should be safe to remove the temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)
    elif args.command == "init":
        project_name = args.name
        project_root = os.path.join(os.getcwd(), project_name)

        if os.path.exists(project_root):
            Log.error(f"Directory '{project_name}' already exists.")
            sys.exit(1)

        os.makedirs(project_root)

        config = {
            "name": project_name,
            "version": "0.1.0",
            "entry": "src/main.clyp",
            "build_dir": "dist",
        }

        config_path = os.path.join(project_root, "clyp.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)

        src_dir = os.path.join(project_root, "src")
        os.makedirs(src_dir)

        main_clyp_path = os.path.join(src_dir, "main.clyp")
        with open(main_clyp_path, "w") as f:
            f.write('print("Hello from Clyp!")\n')

        gitignore_path = os.path.join(project_root, ".gitignore")
        with open(gitignore_path, "w") as f:
            f.write("dist/\n")
            f.write("*.clb\n")
            f.write(".clyp-cache/\n")

        Log.success(f"Initialized Clyp project '{project_name}'")
        Log.info(f"Created project structure in: {project_root}")
        Log.info("You can now `cd` into the directory and run `clyp build`.")
    elif args.command == "format":
        file_path = os.path.abspath(args.file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                clyp_code = f.read()
        except Exception as e:
            Log.error(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        try:
            formatted = format_clyp_code(clyp_code)
        except Exception as e:
            Log.error(f"Formatting failed: {e}", file=sys.stderr)
            sys.exit(1)
        if args.print or args.no_write:
            print(formatted)
        else:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(formatted)
                Log.success(f"Formatted {args.file} in place.")
            except Exception as e:
                Log.error(f"Error writing file {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
    elif args.command == "py2clyp":
        from clyp.transpiler import transpile_to_clyp
        import difflib

        file_path = os.path.abspath(args.file)

        def python_to_clyp_transpile(py_code):
            return transpile_to_clyp(py_code)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                py_code = f.read()
        except Exception as e:
            Log.error(f"Error reading file {args.file}: {e}", file=sys.stderr)
            sys.exit(1)
        if args.check:
            # Just check if transpilation is possible
            try:
                clyp_code = python_to_clyp_transpile(py_code)
                if not clyp_code or not isinstance(clyp_code, str):
                    Log.error(
                        "Transpilation failed: No output generated.", file=sys.stderr
                    )
                    sys.exit(1)
                if not args.quiet:
                    Log.success(f"{args.file} can be transpiled to Clyp.")
                sys.exit(0)
            except Exception as e:
                Log.error(f"Transpilation failed: {e}", file=sys.stderr)
                sys.exit(1)  # Ensure SystemExit is always raised on failure
            # Fallback: if we ever reach here, exit with error
            sys.exit(1)
        try:
            clyp_code = python_to_clyp_transpile(py_code)
        except Exception as e:
            Log.error(f"Transpilation failed: {e}", file=sys.stderr)
            sys.exit(1)
        if args.format and not args.no_format:
            try:
                clyp_code = format_clyp_code(clyp_code)
            except Exception as e:
                Log.warn(f"Formatting failed: {e}", file=sys.stderr)
        if args.stats:
            py_lines = len(py_code.splitlines())
            clyp_lines = len(clyp_code.splitlines())
            Log.info(f"Python lines: {py_lines}, Clyp lines: {clyp_lines}")
        if args.diff:
            diff = difflib.unified_diff(
                py_code.splitlines(),
                clyp_code.splitlines(),
                fromfile=args.file,
                tofile=args.output or "clyp_output.clyp",
                lineterm="",  # No extra newlines
            )
            print("\n".join(diff))
        if args.print:
            print(clyp_code)
        if args.output:
            try:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Wrote transpiled Clyp code to {args.output}")
            except Exception as e:
                Log.error(f"Error writing to {args.output}: {e}", file=sys.stderr)
                sys.exit(1)
        if args.overwrite:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clyp_code)
                if not args.quiet:
                    Log.success(f"Overwrote {args.file} with transpiled Clyp code.")
            except Exception as e:
                Log.error(f"Error overwriting {args.file}: {e}", file=sys.stderr)
                sys.exit(1)
        if not (args.print or args.output or args.overwrite or args.diff):
            # Default: print to stdout
            print(clyp_code)
    elif args.command == "clean":

        def remove_dirs(root, dirs):
            for d in dirs:
                path = os.path.join(root, d)
                if os.path.exists(path):
                    shutil.rmtree(path, ignore_errors=True)
                    Log.success(f"Removed {path}")

        if args.all:
            for dirpath, dirnames, _ in os.walk(os.getcwd()):
                remove_dirs(dirpath, ["build", "dist", ".clyp-cache"])
        else:
            remove_dirs(os.getcwd(), ["build", "dist", ".clyp-cache"])
    elif args.command == "check":

        def check_file(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    clyp_code = f.read()
                parse_clyp(clyp_code, file_path)
                Log.success(f"{file_path} OK")
            except Exception as e:
                Log.error(f"{file_path}: {e}")
                return False
            return True

        if args.file:
            check_file(os.path.abspath(args.file))
        else:
            # Check all .clyp files in project
            ok = True
            for dirpath, _, filenames in os.walk(os.getcwd()):
                for f in filenames:
                    if f.endswith(".clyp"):
                        if not check_file(os.path.join(dirpath, f)):
                            ok = False
            if ok:
                Log.success("All files OK.")
            else:
                sys.exit(1)
    elif args.command == "deps":
        from .importer import find_clyp_imports

        def print_deps(file_path, seen=None, level=0):
            if seen is None:
                seen = set()
            abs_path = os.path.abspath(file_path)
            if abs_path in seen:
                print("  " * level + f"- {os.path.basename(file_path)} (already shown)")
                return
            seen.add(abs_path)
            print("  " * level + f"- {os.path.basename(file_path)}")
            try:
                imports = find_clyp_imports(abs_path)
                for imp in imports:
                    resolved = resolve_import_path(imp, abs_path)
                    if resolved:
                        print_deps(resolved, seen, level + 1)
            except Exception as e:
                print("  " * (level + 1) + f"[error: {e}]")

        if args.file:
            print_deps(args.file)
        else:
            # Try to find entry from clyp.json
            config_path = os.path.join(os.getcwd(), "clyp.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                entry = config.get("entry")
                if entry:
                    print_deps(entry)
                else:
                    Log.error("No entry found in clyp.json.")
            else:
                Log.error("No file specified and no clyp.json found.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
