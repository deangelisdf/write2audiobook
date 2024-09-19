---
title: PowerPoint presentations
description: Instructions on converting PowerPoint presentations to MP3.
---

This page explains how to use the `pptx2audio.py` script to convert PowerPoint presentations to MP3 files.

!!! important
    PowerPoint presentations you want to convert must meet these requirements:

    * The file extension must be **.pptx**.

## Run the script

To convert a PowerPoint presentation to an m4b file:

1. [Download the script](./download-scripts.md) and [install the required libraries](./install-libraries.md).
1. In your terminal, go to the Write2Audiobook project's root directory.

    ```console
    cd write2audiobook
    ```

1. Run the `pptx2audio.py` script.

    ```console
    python3 pptx2audio.py path/to/file/test.pptx
    ```

## View the output

Look for the mb4 file in your current directory to confirm the conversion was successful.

![successful-conversion](../img/pptx-to-audio-output.png)
