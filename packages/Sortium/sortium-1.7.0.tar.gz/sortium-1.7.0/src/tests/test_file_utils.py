# src/tests/test_file_utils.py
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from sortium.file_utils import FileUtils

# Initialize once, as it's stateless
file_utils = FileUtils()


def test_get_file_modified_date(tmp_path: Path):
    """Tests that the correct modification datetime is returned."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Get initial modification time
    mod_time = file_utils.get_file_modified_date(str(test_file))
    assert isinstance(mod_time, datetime)
    # Check if the time is very recent
    assert datetime.now() - mod_time < timedelta(seconds=5)

    with pytest.raises(FileNotFoundError):
        file_utils.get_file_modified_date(str(tmp_path / "non_existent.txt"))


def test_iter_shallow_files(file_tree: Path):
    """Tests the non-recursive file iterator."""
    # Get a list of file names from the generator
    files = {p.name for p in file_utils.iter_shallow_files(str(file_tree))}

    expected_files = {
        "main_image.jpg",
        "main_doc.txt",
        "main_archive.rar",
        "script.py",
        "data_report_2023.csv",
    }

    assert files == expected_files


def test_iter_shallow_files_with_ignore(file_tree: Path):
    """Tests ignoring specific files in the shallow iterator."""
    files = {
        p.name
        for p in file_utils.iter_shallow_files(
            str(file_tree), ignore_dir=["script.py", "main_doc.txt"]
        )
    }

    assert "script.py" not in files
    assert "main_doc.txt" not in files
    assert "main_image.jpg" in files


def test_iter_all_files_recursive(file_tree: Path):
    """Tests the recursive file iterator."""
    files = {p.name for p in file_utils.iter_all_files_recursive(str(file_tree))}

    expected_files = {
        "main_image.jpg",
        "main_doc.txt",
        "main_archive.rar",
        "script.py",
        "data_report_2023.csv",
        "nested_image.png",
        "nested_doc.pdf",
        "deep_archive.zip",
        "secret.txt",  # Not ignored by default
    }
    assert files == expected_files


def test_iter_all_files_recursive_with_ignore(file_tree: Path):
    """Tests ignoring a directory during recursive iteration."""
    files = {
        p.name
        for p in file_utils.iter_all_files_recursive(
            str(file_tree), ignore_dir=["ignore_this_dir", "sub_dir"]
        )
    }

    # Check that nothing from the ignored dirs is present
    assert "secret.txt" not in files
    assert "nested_image.png" not in files
    assert "deep_archive.zip" not in files

    # Check that top-level files are still present
    assert "main_image.jpg" in files
    assert "script.py" in files


def test_find_unique_extensions(file_tree: Path):
    """Tests finding all unique extensions recursively."""
    extensions = file_utils.find_unique_extensions(str(file_tree))

    expected_extensions = {
        ".jpg",
        ".txt",
        ".rar",
        ".py",
        ".csv",
        ".png",
        ".pdf",
        ".zip",
    }
    assert extensions == expected_extensions


def test_find_unique_extensions_with_ignore(file_tree: Path):
    """Tests finding extensions while ignoring directories."""
    extensions = file_utils.find_unique_extensions(
        str(file_tree), ignore_dir=["sub_dir"]
    )

    # .png, .pdf, .zip from sub_dir should be ignored
    expected_extensions = {".jpg", ".txt", ".rar", ".py", ".csv", ".txt"}
    assert extensions == expected_extensions
    assert ".png" not in extensions
    assert ".pdf" not in extensions


def test_flatten_dir(file_tree: Path):
    """Tests moving all nested files into a single directory."""
    dest_path = file_tree / "flattened"
    file_utils.flatten_dir(str(file_tree), str(dest_path))

    # All nested files should now be in dest_path
    assert (dest_path / "main_image.jpg").exists()  # Moved from root
    assert (dest_path / "nested_image.png").exists()  # Moved from sub_dir
    assert (dest_path / "deep_archive.zip").exists()  # Moved from deep_dir

    # Original files should be gone
    assert not (file_tree / "main_image.jpg").exists()
    assert not (file_tree / "sub_dir" / "nested_image.png").exists()

    # Original directories should still exist (but be empty of files)
    assert (file_tree / "sub_dir").is_dir()


def test_flatten_dir_with_ignore(file_tree: Path):
    """Tests flattening while ignoring a directory."""
    dest_path = file_tree / "flattened_ignore"
    file_utils.flatten_dir(str(file_tree), str(dest_path), ignore_dir=["sub_dir"])

    # Files from sub_dir should NOT be in the destination
    assert not (dest_path / "nested_image.png").exists()
    assert not (dest_path / "deep_archive.zip").exists()

    # Files from sub_dir should still be in their original location
    assert (file_tree / "sub_dir" / "nested_image.png").exists()

    # Other files should be moved
    assert (dest_path / "main_image.jpg").exists()
