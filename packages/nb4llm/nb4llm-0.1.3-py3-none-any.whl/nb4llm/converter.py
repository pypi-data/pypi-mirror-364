# converter.py

import re
from pathlib import Path

import nbformat


# How many back ticks do I need?!
def get_fence(cell_source: str, min_length: int = 3) -> str:
    """
    Get the fence for a cell source. This helps ensure that the fence is not too short.

    Inputs:
    -------
    cell_source: str
        The source code of a cell.
    min_length: int
        The minimum length of the fence.

    Returns:
    --------
    fence: str
        The fence for the cell source.
    """
    matches = re.findall(r"`+", cell_source)
    max_len = max([len(m) for m in matches], default=0)
    fence_len = max(min_length, max_len + 1)
    return "`" * fence_len


# convert .ipynb to .txt
def convert_ipynb_to_txt(ipynb_path: str, txt_path: str) -> None:
    """
    Convert a Jupyter notebook (.ipynb) to a text file (.txt).

    This function reads a Jupyter notebook file and converts its content into a text format.
    It handles both markdown and code cells, converting them to Markdown and Python code blocks, respectively.

    Inputs:
    -------
    ipynb_path: str
        The path to the Jupyter notebook file.
    txt_path: str
        The path to the output text file.
    """
    nb = nbformat.read(ipynb_path, as_version=4)
    out_lines = []
    out_lines.append(f"# {Path(ipynb_path).name}\n")

    # Extract kernel language from notebook metadata
    kernel_language = "python"  # default fallback
    if hasattr(nb, "metadata") and nb.metadata:
        kernelspec = nb.metadata.get("kernelspec", {})
        if kernelspec and "language" in kernelspec:
            kernel_language = kernelspec["language"]

    for cell in nb.cells:
        fence = get_fence(cell.source)
        if cell.cell_type == "markdown":
            out_lines.append(f"{fence}markdown")
            out_lines.append(cell.source)
            out_lines.append(f"{fence}\n")
        elif cell.cell_type == "code":
            out_lines.append(f"{fence}{kernel_language}")
            out_lines.append(cell.source)
            out_lines.append(f"{fence}\n")
    with open(txt_path, "w") as f:
        f.write("\n".join(out_lines))
    # No return


# Usage
# ipynb_path = "note_book_name.ipynb"
# txt_path = "note_book_name.txt"
# with open(txt_path, "w") as f:
#    f.write(notebook_to_txt(ipynb_path))


# convert .txt to .ipynb
def convert_txt_to_ipynb(txt_path: str, ipynb_path: str) -> None:
    """
    Convert a text file (.txt) back to a Jupyter notebook (.ipynb).

    This function reads a text file in the format produced by convert_ipynb_to_txt
    and converts it back into a Jupyter notebook format.

    Inputs:
    -------
    txt_path: str
        The path to the input text file.
    ipynb_path: str
        The path to the output Jupyter notebook file.
    """
    import re

    with open(txt_path, "r") as f:
        content = f.read()

    # Split content into lines
    lines = content.split("\n")

    # Skip notebook name header if present
    if lines and lines[0].startswith("# "):
        lines = lines[1:]

    # Create notebook structure
    nb = nbformat.v4.new_notebook()

    # Default metadata (will be updated if we detect a different language)
    detected_language = "python"
    kernel_name = "python3"
    display_name = "Python 3"

    nb.metadata = {
        "kernelspec": {
            "display_name": display_name,
            "language": detected_language,
            "name": kernel_name,
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.8.0",
        },
    }

    # Parse blocks
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Check for fence start
        fence_match = re.match(r"^(`+)(\w*)$", line)
        if fence_match:
            fence = fence_match.group(1)
            cell_type = fence_match.group(2)

            # Find the end of this block
            block_content = []
            i += 1  # Move past the opening fence

            while i < len(lines):
                if lines[i].strip() == fence:
                    break
                block_content.append(lines[i])
                i += 1

            # Create the appropriate cell
            if cell_type == "markdown":
                cell = nbformat.v4.new_markdown_cell("\n".join(block_content))
            else:
                # Handle different code languages
                cell = nbformat.v4.new_code_cell("\n".join(block_content))

                # Update kernel metadata if we detect a different language
                if cell_type and cell_type != "python":
                    detected_language = cell_type
                    # Update kernel info based on detected language
                    if cell_type == "r":
                        kernel_name = "ir"
                        display_name = "R"
                    elif cell_type == "julia":
                        kernel_name = "julia-1.8"
                        display_name = "Julia 1.8.5"
                    elif cell_type == "javascript":
                        kernel_name = "nodejs"
                        display_name = "Node.js"
                    else:
                        # For other languages, use the language name as kernel name
                        kernel_name = cell_type
                        display_name = cell_type.capitalize()

                    # Update notebook metadata
                    nb.metadata["kernelspec"] = {
                        "display_name": display_name,
                        "language": detected_language,
                        "name": kernel_name,
                    }

            nb.cells.append(cell)
            i += 1  # Move past the closing fence
        else:
            # If we encounter content that's not in a fence, treat it as markdown
            block_content = []
            while i < len(lines):
                line = lines[i].strip()
                if not line or re.match(r"^`+(\w*)$", line):
                    break
                block_content.append(lines[i])
                i += 1

            if block_content:
                cell = nbformat.v4.new_markdown_cell("\n".join(block_content))
                nb.cells.append(cell)
            else:
                i += 1

    # Write the notebook
    nbformat.write(nb, ipynb_path)
