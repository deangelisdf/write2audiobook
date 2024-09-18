# Quick start guide for Write2Audiobook

Follow this tutorial to learn how to use Write2Audiobook.

## Prequisites

Before you begin, clone the repository and install the packages from the `requirements` file.

```bash
git clone https://github.com/deangelisdf/write2audiobook.git
cd write2audiobook
python3 -m pip install -r requirements
```

NOTE:
If you're on a linux system, you must install additional packages:<br>
    ```
    sudo apt update && sudo apt install espeak ffmpeg libespeak1 -y
    ```

## Convert a text-based file to an audiobook

To convert an EPUB file to an audiobook:

```bash
python3 ebook2audio.py book.epub
```

To convert a plain text file to an audiobook:

```bash
python3 txt2audio.py text.txt
```

To convert a PowerPoint presentation (PPTX file) to an audiobook:

```bash
python3 pptx2audio.py presentation.pptx
```

To convert a Word document (DOCX) to an audiobook:

```bash
python3 docx2audio.py document.docx
```

## Enjoy your audiobook

Write2Audio saves your audiobook as an MP3 file in your current directory. It will have the same name as the file you converted.

```bash
python3 txt2audio.py test.txt
```

![directory-image](img/example-output.png)