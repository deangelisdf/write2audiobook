# Write2Audiobook
Simplify life with audiobooks.<br>
A tool designed to help visually impaired people by converting text-based documents into audiobooks.

## Features
Convert various text formats to audio, including EPUB, TXT, PPTX, and DOCX.<br>
Easy to use with simple command-line instructions.<br>
Enhances accessibility for visually impaired users.<br>
## Requirements
To get started, clone the repository and install the necessary dependencies:
```
cd write2audiobook
python3 -m pip install -r requirements.txt
```

## How to Use
You can convert your documents to audiobooks using the following commands:<br>
To convert an EPUB book to an audiobook:
```
python3 ebook2audio.py book.epub language
```
To convert a plain text file to an audiobook:
```
python3 txt2audio.py text.txt language
```
To convert a PowerPoint presentation to an audiobook:
```
python3 pptx2audio.py presentation.pptx language
```
To convert a Word document to an audiobook:
```
python3 docx2audio.py document.docx language
```
where `language` supported is `it` stay for italian and `en` stay for english.
## Contributing
We welcome contributions! If you'd like to contribute, please fork the repository and submit a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.

## Contact
For questions, suggestions, or feedback, feel free to open an issue or contact us.
