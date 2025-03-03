import os
import glob


def create_markdown_from_python_files(output_filename="combined_code.md"):
    """
    Reads all .py files recursively in the current directory (excluding __init__.py and venv folder),
    and creates a markdown file containing the code of each file.

    Args:
        output_filename (str): The name of the output markdown file. Defaults to "combined_code.md".
    """

    with open(output_filename, "w") as outfile:
        for filepath in glob.glob("ragoo/**/*.py", recursive=True):
            if os.path.basename(filepath) == "__init__.py":
                continue  # Skip __init__.py files
            if "venv" in filepath.split(os.path.sep):
                continue  # skip any file in venv folder

            print(f"Processing file: {filepath}")  # Optional: for debugging

            try:
                with open(filepath, "r") as infile:
                    code = infile.read()

                outfile.write(f"## {filepath}\n\n")  # Header with filename
                outfile.write("```python\n")
                outfile.write(code)
                outfile.write("\n```\n\n")  # Code block
                outfile.write("---\n\n")  # Separator between files

            except Exception as e:
                print(f"Error reading or processing {filepath}: {e}")


if __name__ == "__main__":
    create_markdown_from_python_files()
    print("Markdown file created successfully!")
