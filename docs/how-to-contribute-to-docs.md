# How to contribute to the Write2Audiobook documentation

The Write2Audiobook documentation is built with [Mkdocs](https://github.com/mkdocs/mkdocs/tree/master) and
the [Materials](https://github.com/squidfunk/mkdocs-material/tree/master) theme. These tools use simple Markdown
with a handful of extensions to create a suite of static sites.

For reference material when writing Markdown, see [Material's reference page](https://squidfunk.github.io/mkdocs-material/reference/).

Test your changes locally before submitting a pull request.

```console
python3 -m pip install docs/requirements
mkdocs serve
```

## Style guide

### Write documentation in Visual Studio Code with Markdown extensions

Documentation written with the `markdownlint` VS Code extension will be more consistent with varying writers.

There is a `.markdownlint.rc` file in the project's root that helps enforce consistency.

### Use front matter

Each page should have a `title` and `description` tag in its front matter.
This adds useful metadata to the generated HTML header.

```yaml
---
title: My page
description: The description of the page.
---
```

### Don't use the single `#` header level.

The title of the page comes from the YAML front matter. Having a second first level heading is redundant.

### Sections go in their own directory

Keep each section in a single directory. You can have subdirectories if you have subsections.
This keeps the documentation folder organized.

### Functions and modules have consistent docstrings

The `mkdocstrings` plugin requires a consistent docstring format.

Module-level docstrings appear at the top of the page in mkdocs. They should follow this format:

```python
"""
file: [myfile.py](link to file in GitHub)

definition: A brief, one sentence description of the module's purpose.

Example usage:
    `python myfile.py`
"""
```

Function-level docstrings appear under their function names in mkdocs. They should follow this format:

```python
def my_function(arg1: str) -> int:
    """Description of the function.

    Arguments:
        arg1: Define the arguments (where they come from, what they represent).
    
    Returns:
        Define what the function returns.
```