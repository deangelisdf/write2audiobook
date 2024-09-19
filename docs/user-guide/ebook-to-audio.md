---
title: Ebooks
description: Instructions on converting Ebooks to MP3.
---

This page explains how to use the `ebook2audio.py` script to convert Ebooks to MP3 files.

!!! important
    Ebooks you want to convert must meet these requirements:

    * The file extension must be **.pub**.

## Run the script

To convert an Ebook to MP3 files:

1. [Download the script](./download-scripts.md) and [install the required libraries](./install-libraries.md).
1. In your terminal, go to the Write2Audiobook project's root directory.

    ```console
    cd write2audiobook
    ```

1. Run the `ebook2audio.py` script.

    ```console
    python3 ebook2audio.py path/to/file/test.epub
    ```

## View the output

The script creates MP3 files and plain text files as it converts the Ebook. It may convert
larger books into multiple MP3 files and text files.

For example, if the script creates *X* files:

- MP3 files will have a name like `itemX.mp3`.
- Text files will have a name like `itemX.log`

Look for the MP3 files in the Ebook's directory to confirm the conversion was successful.

![docx-to-audio-output](../img/ebook-to-audio-output.png)
