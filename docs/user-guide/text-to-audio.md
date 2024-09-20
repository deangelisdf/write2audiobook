---
title: Text files
description: Instructions on converting plain text files to MP3.
---

This page explains how to use the `txt2audio.py` script to convert plain text files to MP3 files.

!!! important
    Text files you want to convert must meet these requirements:

    * The file encoding must be **UTF-8**.
    * The file extension must be **.txt**.

## Run the script

To convert a TXT file to an MP3 file:

1. [Download the script](./download-scripts.md) and then [install the required libraries](./install-libraries.md).
1. In your terminal, go to the Write2Audiobook project's root directory.

    ```console
    cd write2audiobook
    ```

1. Run the `txt2audio.py` script.

    ```console
    python3 txt2audio.py path/to/file/test.txt
    ```

## View the output

Look for the MP3 file in your current directory to confirm the conversion was successful.

![successful-conversion](../img/example-output.png)
