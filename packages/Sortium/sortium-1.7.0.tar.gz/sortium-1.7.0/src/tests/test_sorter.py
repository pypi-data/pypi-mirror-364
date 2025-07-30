# src/tests/test_sorter.py
import pytest
from pathlib import Path
import time
from sortium.sorter import Sorter
from sortium.file_utils import FileUtils, _generate_unique_path


@pytest.fixture
def sorter_instance():
    """Returns a Sorter instance with default settings for testing."""
    return Sorter(file_utils=FileUtils())


def test_generate_unique_path(tmp_path: Path):
    """Tests the collision-avoidance path generation logic."""
    (tmp_path / "file.txt").touch()

    # First collision should be "file (1).txt"
    unique_path = _generate_unique_path(tmp_path / "file.txt")
    assert unique_path.name == "file (1).txt"

    # Create the next collision file
    (tmp_path / "file (1).txt").touch()

    # Second collision should be "file (2).txt"
    unique_path_2 = _generate_unique_path(tmp_path / "file.txt")
    assert unique_path_2.name == "file (2).txt"

    # Test with a path that does not exist
    non_existent_path = tmp_path / "new_file.txt"
    assert _generate_unique_path(non_existent_path) == non_existent_path


def test_sort_by_type(sorter_instance: Sorter, file_tree: Path):
    """Tests sorting shallow files into category directories."""
    sorter_instance.sort_by_type(str(file_tree))

    # Check that files were moved to correct category folders
    assert (file_tree / "Images" / "main_image.jpg").is_file()
    assert (file_tree / "Documents" / "main_doc.txt").is_file()
    assert (file_tree / "Archives" / "main_archive.rar").is_file()
    assert (file_tree / "Code" / "script.py").is_file()
    assert (file_tree / "Spreadsheets" / "data_report_2023.csv").is_file()

    # Check that original files are gone
    assert not (file_tree / "main_image.jpg").exists()

    # Check that nested files were NOT touched
    assert (file_tree / "sub_dir" / "nested_image.png").is_file()


def test_sort_by_type_to_destination(sorter_instance: Sorter, file_tree: Path):
    """Tests sorting files to a separate destination directory."""
    dest_path = file_tree / "sorted_output"

    sorter_instance.sort_by_type(str(file_tree), dest_folder_path=str(dest_path))

    # Check files in the new destination
    assert (dest_path / "Images" / "main_image.jpg").is_file()
    assert (dest_path / "Documents" / "main_doc.txt").is_file()

    # Check original files are gone from the source
    assert not (file_tree / "main_image.jpg").exists()

    # Check source directory does not contain new category folders
    assert not (file_tree / "Images").exists()


def test_sort_by_type_with_collision(sorter_instance: Sorter, tmp_path: Path):
    """Tests that sort_by_type correctly handles file name collisions."""
    (tmp_path / "image.jpg").touch()

    # Create a pre-existing file in the destination category
    img_dir = tmp_path / "Images"
    img_dir.mkdir()
    (img_dir / "image.jpg").touch()

    sorter_instance.sort_by_type(str(tmp_path))

    # The original should be moved and renamed
    assert (img_dir / "image (1).jpg").is_file()


def test_sort_by_date(sorter_instance: Sorter, file_tree: Path):
    """Tests sorting files by their modification date."""
    # First, sort by type to create category folders
    sorter_instance.sort_by_type(str(file_tree))

    # Let's modify a file to have a distinct, older date
    doc_path = file_tree / "Documents" / "main_doc.txt"
    time.sleep(0.1)  # Ensure timestamp is different
    doc_path.touch()

    sorter_instance.sort_by_date(str(file_tree), folder_types=["Images", "Documents"])

    # Check that files are in date-stamped folders
    # Note: This can be brittle. A better test would mock the date.
    # For simplicity, we check for the existence of ANY date-stamped folder.

    img_subdirs = [d.name for d in (file_tree / "Images").iterdir() if d.is_dir()]
    doc_subdirs = [d.name for d in (file_tree / "Documents").iterdir() if d.is_dir()]

    assert len(img_subdirs) == 1
    assert len(doc_subdirs) == 1

    # Check that the file is inside that date folder
    date_folder_name = img_subdirs[0]
    assert (file_tree / "Images" / date_folder_name / "main_image.jpg").is_file()

    # Check original category folder is now empty of files
    assert not (file_tree / "Images" / "main_image.jpg").exists()


def test_sort_by_regex(sorter_instance: Sorter, file_tree: Path):
    """Tests recursive sorting based on regex patterns."""
    dest_path = file_tree / "regex_sorted"
    regex_map = {
        "Reports": r".*_report_.*\.csv$",
        "Python_Code": r".*\.py$",
        "All_Images": r".*\.(jpg|png|gif)$",
    }

    sorter_instance.sort_by_regex(str(file_tree), regex_map, str(dest_path))

    # Check that files from all levels were moved and categorized
    assert (dest_path / "Reports" / "data_report_2023.csv").is_file()
    assert (dest_path / "Python_Code" / "script.py").is_file()
    assert (dest_path / "All_Images" / "main_image.jpg").is_file()
    assert (dest_path / "All_Images" / "nested_image.png").is_file()

    # Check that unmatched files were NOT moved
    assert (file_tree / "main_doc.txt").is_file()
    assert (file_tree / "sub_dir" / "deep_dir" / "deep_archive.zip").is_file()
