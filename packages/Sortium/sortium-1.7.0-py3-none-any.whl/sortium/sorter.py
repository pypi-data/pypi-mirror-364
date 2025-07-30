import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
from typing import Dict, List, Generator, Tuple
from .config import DEFAULT_FILE_TYPES
from .file_utils import FileUtils, _move_file_safely_wrapper


class Sorter:
    """Organizes files into directories based on various criteria.

    The Sorter class provides parallelized, memory-efficient methods to sort
    files based on their type, modification date, or custom regex patterns.
    It is designed to handle very large numbers of files without consuming
    excessive memory.

    Attributes:
        file_types_dict (Dict[str, List[str]]): A mapping of file category
            names to lists of associated file extensions.
        file_utils (FileUtils): An instance of a file utility class.
    """

    def __init__(
        self,
        file_types_dict: Dict[str, List[str]] = None,
        file_utils: FileUtils = None,
    ):
        """Initializes the Sorter instance.

        Args:
            file_types_dict (Dict[str, List[str]], optional): A dictionary
                mapping category names to file extensions. Defaults to
                ``DEFAULT_FILE_TYPES``.
            file_utils (FileUtils, optional): An instance of FileUtils.
                Defaults to a new ``FileUtils()`` instance.
        """
        self.file_types_dict = file_types_dict or DEFAULT_FILE_TYPES
        self.file_utils = file_utils or FileUtils()
        self.extension_to_category = {
            ext.lower(): category
            for category, extensions in self.file_types_dict.items()
            for ext in extensions
        }

    def _get_category(self, extension: str) -> str:
        """Determines the category for a file extension.

        Args:
            extension: The file extension (e.g., ".pdf").

        Returns:
            The corresponding category name (e.g., "Documents") or "Others".
        """
        return self.extension_to_category.get(extension.lower(), "Others")

    def _execute_sort(
        self,
        task_generator: Generator[Tuple[str, str], None, None],
        description: str,
    ) -> None:
        """Executes a sorting operation in parallel using a task generator.

        This private helper method encapsulates the ``ProcessPoolExecutor`` logic,
        consuming tasks from a generator to ensure memory efficiency.

        Args:
            task_generator: A generator that yields tuples of
                (source_path, destination_folder_path).
            description: A string describing the sort operation for logging.
        """
        print(f"Starting sort {description}...")
        with ProcessPoolExecutor() as executor:
            # Use the robust 'map' method with the wrapper function.
            results = executor.map(_move_file_safely_wrapper, task_generator)

            # Process results as they are completed by worker processes
            for error_msg in results:
                if error_msg:
                    print(error_msg)
        print(f"Sorting {description} complete.")

    def sort_by_type(
        self,
        folder_path: str,
        dest_folder_path: str | None = None,
        ignore_dir: List[str] | None = None,
    ) -> None:
        """Sorts files into subdirectories by file type in parallel.

        Files in the top level of ``folder_path`` are moved into subdirectories
        (e.g., "Images", "Documents") inside ``dest_folder_path``.

        .. note:: This method is memory-efficient and suitable for sorting
                  directories with a very large number of files.

        Args:
            folder_path: Path to the directory containing unsorted files.
            dest_folder_path (str, optional): Base directory for the sorted
                category folders. If ``None``, ``folder_path`` is used.
            ignore_dir (List[str], optional): Directory names to ignore.

        Raises:
            FileNotFoundError: If ``folder_path`` does not exist.
        """
        source_folder = Path(folder_path)
        if not source_folder.exists():
            raise FileNotFoundError(f"The path '{source_folder}' does not exist.")
        dest_base_folder = Path(dest_folder_path) if dest_folder_path else source_folder

        def generate_tasks():
            for item in self.file_utils.iter_shallow_files(
                str(source_folder), ignore_dir
            ):
                category = self._get_category(item.suffix)
                dest_folder = dest_base_folder / category
                yield (str(item), str(dest_folder))

        self._execute_sort(generate_tasks(), "by type")

    def sort_by_date(
        self,
        folder_path: str,
        folder_types: List[str],
        dest_folder_path: str | None = None,
    ) -> None:
        """Sorts files within category folders by their modification date.

        Files are moved into date-stamped subfolders (e.g., "01-Jan-2023").

        Args:
            folder_path: Root directory containing the category folders to process.
            folder_types: List of category folder names (e.g., ['Images']).
            dest_folder_path (str, optional): Base directory for the sorted
                folders. If ``None``, files are sorted within their current
                category folders.

        Raises:
            FileNotFoundError: If ``folder_path`` does not exist.
        """
        source_root = Path(folder_path)
        if not source_root.exists():
            raise FileNotFoundError(f"The path '{source_root}' does not exist.")
        dest_root = Path(dest_folder_path) if dest_folder_path else source_root

        def generate_tasks():
            for folder_type in folder_types:
                category_folder = source_root / folder_type
                if category_folder.is_dir():
                    for file_path in category_folder.iterdir():
                        if file_path.is_file():
                            try:
                                modified = self.file_utils.get_file_modified_date(
                                    str(file_path)
                                )
                                date_str = modified.strftime("%d-%b-%Y")
                                final_dest_folder = dest_root / folder_type / date_str
                                yield (str(file_path), str(final_dest_folder))
                            except Exception as e:
                                print(f"Could not prepare file '{file_path.name}': {e}")
                else:
                    print(f"Category folder '{category_folder}' not found, skipping.")

        self._execute_sort(generate_tasks(), "by date")

    def sort_by_regex(
        self, folder_path: str, regex: Dict[str, str], dest_folder_path: str
    ) -> None:
        """Sorts files recursively based on regex patterns.

        Scans ``folder_path`` and its subdirectories for files whose names
        match the provided regex patterns, then moves them to categorized
        folders within ``dest_folder_path``.

        Args:
            folder_path: Path to the directory to scan recursively.
            regex: Dictionary mapping category names to regex patterns.
            dest_folder_path: Base directory where sorted files will be moved.

        Raises:
            FileNotFoundError: If ``folder_path`` does not exist.
            RuntimeError: If a critical error occurs during parallel sorting.
        """
        source_path = Path(folder_path)
        if not source_path.exists():
            raise FileNotFoundError(f"The path '{source_path}' does not exist.")
        dest_base_path = Path(dest_folder_path)

        def generate_tasks():
            file_generator = self.file_utils.iter_all_files_recursive(str(source_path))
            for file_path in file_generator:
                for category, pattern in regex.items():
                    if re.match(pattern, file_path.name):
                        dest_folder = dest_base_path / category
                        yield (str(file_path), str(dest_folder))
                        break  # Move to next file once a match is found

        try:
            self._execute_sort(generate_tasks(), "by regex")
        except Exception as e:
            raise RuntimeError(f"An error occurred during parallel sorting: {e}")
