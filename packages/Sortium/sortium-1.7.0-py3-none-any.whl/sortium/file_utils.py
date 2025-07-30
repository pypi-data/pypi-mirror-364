import shutil
from pathlib import Path
from datetime import datetime
from typing import Set, Generator, Sequence, List
from concurrent.futures import ProcessPoolExecutor


def _generate_unique_path(dest_path: Path) -> Path:
    """Creates a unique path to avoid overwriting existing files.

    If a file or directory already exists at ``dest_path``, this function
    appends a counter (e.g., " (1)", " (2)") to the file stem until a
    unique path is found.

    Args:
        dest_path: The desired destination path.

    Returns:
        A unique, non-existent path.
    """
    if not dest_path.exists():
        return dest_path

    parent, stem, suffix = dest_path.parent, dest_path.stem, dest_path.suffix
    counter = 1
    while True:
        new_path = parent / f"{stem} ({counter}){suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


def _move_file_safely(source_path_str: str, dest_folder_str: str) -> str:
    """Moves a single file, handling name collisions. Intended for worker processes.

    This function is designed to be the target for a ``ProcessPoolExecutor``,
    as it is a top-level function that can be pickled.

    Args:
        source_path_str: The full path of the file to move.
        dest_folder_str: The path of the folder to move the file into.

    Returns:
        An empty string on success, or an error message string on failure.
    """
    try:
        source_path = Path(source_path_str)
        dest_folder = Path(dest_folder_str)
        dest_folder.mkdir(parents=True, exist_ok=True)
        final_dest_path = _generate_unique_path(dest_folder / source_path.name)
        shutil.move(str(source_path), str(final_dest_path))
        return ""
    except Exception as e:
        return f"Error moving file '{source_path_str}': {e}"


def _move_file_safely_wrapper(args):
    """
    Helper to unpack arguments for use with 'executor.map'.
    This allows passing multiple arguments to the target function.
    """
    return _move_file_safely(*args)


class FileUtils:
    """Provides memory-efficient utilities for file and directory manipulation."""

    def get_file_modified_date(self, file_path: str) -> datetime:
        """Returns the last modified datetime of a file.

        Args:
            file_path: Full path to the file.

        Returns:
            A datetime object for the last modification time.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"File does not exist: {file_path}")
        return datetime.fromtimestamp(path.stat().st_mtime)

    def iter_shallow_files(
        self, folder_path: str, ignore_dir: Sequence[str] | None = None
    ) -> Generator[Path, None, None]:
        """Yields files in the top level of a directory.

        This is a non-recursive generator.

        Args:
            folder_path: Path to the folder to iterate.
            ignore_dir (Sequence[str], optional): Names of directories or files to ignore.

        Yields:
            A generator of ``Path`` objects for each file.
        """
        source_root = Path(folder_path)
        ignore_set = set(ignore_dir or [])
        try:
            for item in source_root.iterdir():
                if item.name in ignore_set:
                    continue
                if item.is_file():
                    yield item
        except FileNotFoundError:
            print(f"Directory not found: {folder_path}")
        except PermissionError:
            print(f"Permission denied for directory: {folder_path}")

    def iter_all_files_recursive(
        self, folder_path: str, ignore_dir: Sequence[str] | None = None
    ) -> Generator[Path, None, None]:
        """Recursively yields all files in a directory and its subdirectories.

        This is a memory-efficient generator that does not load the entire
        file list into memory.

        Args:
            folder_path: Path to the root directory to scan.
            ignore_dir (Sequence[str], optional): Directory names to ignore.

        Yields:
            A generator of ``Path`` objects for each file found.
        """
        source_root = Path(folder_path)
        if not source_root.is_dir():
            return

        ignore_set = set(ignore_dir or [])

        try:
            for item in source_root.iterdir():
                if item.name in ignore_set:
                    continue
                if item.is_dir():
                    yield from self.iter_all_files_recursive(str(item), ignore_dir)
                elif item.is_file():
                    yield item
        except PermissionError:
            print(f"Permission denied for directory: {folder_path}")

    def flatten_dir(
        self,
        folder_path: str,
        dest_folder_path: str,
        ignore_dir: Sequence[str] | None = None,
    ) -> None:
        """Moves all files from a directory tree into a single destination folder.

        This method recursively finds all files in ``folder_path`` and moves
        them to ``dest_folder_path``. It does not preserve the original
        directory structure. It does not delete the original empty folders.

        .. warning:: This operation is parallelized but does not currently
                     support removing the original subdirectories due to the
                     complexities of doing so safely in parallel.

        Args:
            folder_path: Path to the root folder to flatten.
            dest_folder_path: Path to the single folder where all files will be moved.
            ignore_dir (Sequence[str], optional): Directory names to ignore.

        Raises:
            FileNotFoundError: If ``folder_path`` does not exist.
        """
        source_root = Path(folder_path)
        dest_root = Path(dest_folder_path)
        if not source_root.exists():
            raise FileNotFoundError(f"The folder path '{folder_path}' does not exist.")

        dest_root.mkdir(parents=True, exist_ok=True)

        def generate_tasks():
            for file_path in self.iter_all_files_recursive(
                str(source_root), ignore_dir
            ):
                yield (str(file_path), str(dest_root))

        print("Starting directory flattening...")
        with ProcessPoolExecutor() as executor:
            # Use the robust 'map' with the wrapper function
            results = executor.map(_move_file_safely_wrapper, generate_tasks())
            for error_msg in results:
                if error_msg:
                    print(error_msg)
        print("Flattening complete.")

    def find_unique_extensions(
        self, source_path: str, ignore_dir: List[str] | None = None
    ) -> Set[str]:
        """Recursively finds all unique file extensions in a directory.

        This method is memory-efficient, scanning the directory tree without
        loading all paths into memory at once.

        Args:
            source_path: Path to the root directory to scan.
            ignore_dir (List[str], optional): Directory names to ignore.

        Returns:
            A set of unique file extensions (e.g., {".txt", ".jpg"}).

        Raises:
            FileNotFoundError: If ``source_path`` does not exist.
        """
        source_root = Path(source_path)
        if not source_root.exists():
            raise FileNotFoundError(f"The path '{source_root}' does not exist.")

        extensions: Set[str] = set()
        file_generator = self.iter_all_files_recursive(str(source_root), ignore_dir)

        for file_path in file_generator:
            if file_path.suffix:
                extensions.add(file_path.suffix.lower())

        return extensions
