---
title: Quick start guide
description: A tutorial for the Write2Audiobook project.
---

Follow this tutorial to learn how to use Write2Audiobook.

## Prerequisites

Before you begin, download and install the required files.

Learn more about [downloading the scripts from GitHub](./user-guide/download-scripts.md) and [installing the required packages](./user-guide/install-libraries.md).

## Convert a text-based file to an audiobook

1. In your terminal, go to the Write2Audiobook project's root directory.

    ```console
    cd write2audiobook
    ```

1. Run one of the scripts to convert a text-based file to an audiobook:
    To convert an Ebook (EPUB) to an audiobook:

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

Write2Audio saves your audiobook as an audio file in the current directory. It will have the same name as the converted file.

![directory-image](img/example-output.png)

You can listen to your audiobook with any program that can open MP3 or M4B files, like [VLC](https://www.videolan.org/vlc/).
