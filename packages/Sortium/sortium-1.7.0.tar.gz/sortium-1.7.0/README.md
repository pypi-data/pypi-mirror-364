# Sortium

[![PyPI version](https://badge.fury.io/py/sortium.svg)](https://badge.fury.io/py/sortium)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**Sortium** is a high-performance, parallelized Python utility for rapidly organizing file systems. It leverages multiple CPU cores to sort thousands of files into clean, categorized directories based on type, modification date, or custom regex patterns.

Designed for both speed and safety, it is memory-efficient for handling massive directories and automatically prevents file overwrites.

---

## Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
- [Getting Started: Usage Examples](#getting-started-usage-examples)
- [Running Tests](#running-tests)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [Author](#author)
- [License](#license)

---

## Key Features

- ✅ **Parallel Processing**: Utilizes multiple CPU cores to dramatically speed up file moving and organization, especially in large directories.
- ✅ **Memory-Efficient**: Employs generators to process files one by one, ensuring a tiny memory footprint even with millions of files.
- ✅ **Flexible Sorting Methods**:
  - `sort_by_type`: Organize files into categories like `Images`, `Documents`, `Archives`, etc.
  - `sort_by_date`: Further organize categorized files into date-stamped folders (e.g., `01-Jan-2023`).
  - `sort_by_regex`: Use powerful, custom regex patterns to categorize files recursively.
- ✅ **Safe File Operations**: Automatically handles file name collisions by appending a counter (e.g., `image (1).jpg`), preventing accidental data loss.
- ✅ **Sort In-Place or to a New Destination**: Choose to organize files within their current directory or move them to an entirely separate destination folder.
- ✅ **Standalone Utilities**: Includes a `FileUtils` class with helpful methods like recursive file finding (`iter_all_files_recursive`) and directory flattening (`flatten_dir`).

---

## Installation

### From PyPI

To install the latest stable version from PyPI:

```bash
pip install sortium
```

### From Source

To install the latest development version from the repository:

```bash
git clone https://github.com/Sarthak-G0yal/Sortium.git
cd Sortium
pip install -e .
```

---

## Getting Started: Usage Examples

Here are a few examples to get you started quickly.

### Example 1: Sort Files by Type

This is the most common use case. It organizes all files in a folder into subdirectories like `Images`, `Documents`, `Videos`, etc.

```python
from sortium.sorter import Sorter

# The folder you want to clean up
source_directory = "./my_messy_downloads_folder"

# Create a Sorter instance
sorter = Sorter()

# Run the sort!
print(f"Sorting files in {source_directory} by type...")
sorter.sort_by_type(source_directory)
print("Done!")
```

### Example 2: Sort Files to a Different Destination

Organize files from a source folder and move the categorized results to a completely different location.

```python
from sortium.sorter import Sorter

source_dir = "./my_source_files"
destination_dir = "./organized_archive"

sorter = Sorter()

# Files from source_dir will be moved to categorized folders inside destination_dir
sorter.sort_by_type(source_dir, dest_folder_path=destination_dir)
```

### Example 3: Advanced Sorting with Regex

Recursively scan a directory and sort files based on custom patterns. This is great for organizing project files, logs, or datasets.

```python
from sortium.sorter import Sorter

project_folder = "./my_data_science_project"
sorted_output = "./sorted_project_files"

# Define categories and their corresponding regex patterns
regex_map = {
    "Datasets": r".*\.csv$",
    "Notebooks": r".*\.ipynb$",
    "Python_Code": r".*\.py$",
    "Final_Reports": r"final_report_.*\.pdf$"
}

sorter = Sorter()
sorter.sort_by_regex(project_folder, regex_map, sorted_output)
```

---

## Running Tests

To run the full test suite and generate a coverage report, first install the development dependencies:

```bash
pip install pytest pytest-cov
```

Then, from the project's root directory, run:

```bash
pytest --cov=sortium
```

For more details on the test structure, see the [Test Suite README](./src/tests/README.md).

---

## Documentation

This project uses [Sphinx](https://www.sphinx-doc.org/) for documentation.

- **Online Documentation**: [**View Documentation**](https://sarthak-g0yal.github.io/Sortium)

- To build the documentation locally:
  ```bash
  # Navigate to the docs directory
  cd docs
  # Install documentation requirements
  pip install -r requirements.txt
  # Build the HTML pages
  make html
  ```
  View the generated files at `docs/_build/html/index.html`.

---

## Contributing

Contributions are welcome! Please follow these steps to contribute:

1.  Fork the repository.
2.  Create a new branch for your feature or fix (`feature/my-feature` or `fix/my-fix`).
3.  Write tests that cover your changes.
4.  Commit your changes using clear, conventional messages.
5.  Open a pull request with a detailed description of your work.

Please follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. Ensure all code is linted and tested before submitting.

- For bugs and feature requests, please [open an issue](https://github.com/Sarthak-G0yal/Sortium/issues).

---

## Author

**Sarthak Goyal**

- Email: [sarthakgoyal487@gmail.com](mailto:sarthakgoyal487@gmail.com)

---

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
