---
title: Quick start guide
description: A tutorial for the Write2Audiobook project.
---

Follow this tutorial to learn how to use Write2Audiobook.

## Clone the repository

Clone the repository to your computer. Then use the `cd` command to enter the project's root directory.

```console
git clone https://github.com/deangelisdf/write2audiobook.git
cd write2audiobook
```

## Create a virtual environment

To keep your workspace clean and to prevent conflicts with previously installed libraries, create a virtual environment.

```console
python3 -m venv .venv
```

Activate your virtual environment.

=== "Powershell"
    ```powershell
    .venv\Scripts\Activate.ps1
    ```

=== "Command Prompt"
    ```bat
    .venv\Scripts\activate.bat
    ```

=== "Linux or macOS"
    ```console
    source .venv/bin/activate
    ```

## Install required libraries

Use `pip` to install the required libraries in your virtual environment.

```console
python3 -m pip install -r requirements
```

!!! note
    If you're on a Linux system, you must install additional system packages:
    ```console
    sudo apt update && sudo apt install espeak ffmpeg libespeak1 -y
    ```

## Convert a text-based file to an audiobook

To convert an EPUB file to an audiobook:

```console
python3 ebook2audio.py book.epub
```

To convert a plain text file to an audiobook:

```console
python3 txt2audio.py text.txt
```

To convert a PowerPoint presentation (PPTX) to an audiobook:

```console
python3 pptx2audio.py presentation.pptx
```

To convert a Word document (DOCX) to an audiobook:

```console
python3 docx2audio.py document.docx
```

## Play your audiobook

Write2Audio saves your audiobook as an MP3 file in the current directory. It will have the same name as the converted file.

![directory-image](img/example-output.png)

You can listen to your audiobook with any program that can open MP3 files.
