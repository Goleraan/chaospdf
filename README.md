# ChaosPDF - PDF text and image extraction
The tools allows the extraction of unformatted and slightly HTML-formatted text as well as embedded image files from unprotected portable document format (PDF) files.

It is a command-line tool written in Python 3.12. The only external dependency is PyMuPDF.

The name is derived from the chaos that can come out of PDF files when trying to extract data from them with automated workflows.

## Version and maturity
Current version is 0.1.1.

The tool is experimental. Most of its intended features are implemented but are not necessarily robust and not fully tested.

## Notable features
- Extract plain text from PDF files
- Extract basic HTML-formatted text from PDF files
- Recover most of the paragraphs
- Remove page numbers from the extracted HTML
- Optional clear page separation to manually process the text of long PDF files more easily
- Extract all images with their transparency information from PDF files
- Basic text menu to specify the settings
- Batch processing of a large number of PDF files

## Usage instructions
- Either download the source code to run with Python or the Windows exe file from the releases
- For source code:
  - Using a virtual environment is highly recommended
  - Download all files from the src folder
  - Use pip to install pymupdf
  - Start the program from the console with "python chaospdf.py" from the src folder
  - Follow the instructions in the console
- For the Windows executable:
  - Download the latest version from the bin directory
  - Put the executable and the PDF files in the same directory for a simplified user experience
  - Start the executable from a PowerShell or command prompt and start the extraction by entering 1
- Both versions:
  - The extraction settings can be changed with the console-based menu
  - Default settings include:
    - Process all files with the file extension *.pdf in the working directory and its sub directories
    - Create one sub-directory for the results for each PDF file
    - Save TOC, plain text, and HTML-formatted text
    - Extract all images that are larger than 130x130 pixels that are larger than 5000 byte (uncompressed); avoid duplicates
  - Additional files or the working directories can be changed with the text menu just like the image extraction settings
  - If output files exist already, they are overwritten without confirmation

**NOTE: Not all of the options exposed in the text menu are fully tested or even fully implemented!**

## Known limitations
- Depending on the layout software and the original PDF export options, the order of the text on a page can be incorrect. Especially complex layouts with break-out boxes, multiple columns, and images with floating text can screw up the order of the extracted text.
- If images are split into multiple segments by the layout software's PDF export, they are not assembled into a single image. Image extraction for such files is pretty much useless right now.
- If images are saved in CMYK colorspace, they are not converted into RGB, which can be unexpected. The image files look inverted when shown with standard image viewers.
- Not all available settings are implemented or tested, e.g.:
  - Image extraction based on individual pages is not implemented
  - Changing image extraction properties are mostly untested
  - Page numbers in TOC extraction can be incorrect
  - Removing repeating text like title or chapter headings is not implemented

## Intention of the tool
Getting text or images out of a PDF can be useful in many different scenarios. PDF is not intended to extract the data, though. Copying text or images from various PDF readers often suffers from one or multiple of these drawbacks:
- Images cannot be selected reliably
- Image transparency is not copied
- Text formatting is not consistent
- Hyphenation at line ends are either kept or replaced by non-printing characters that can throw-off text editors
- There can be line breaks for each line which are not useful for processing the text further
- Paragraph breaks and line breaks are removed together
- Handling of ligatures is unreliable

The main use case for the author is the transfer of text and images from tabletop or pen-and-paper role-playing PDF publications into virtual tabletop (VTT) systems. There are many adventure modules available as PDF for countless game systems. Copying some of the content into the preferred VTT can take a tremendous amount of preparation time for the game master (GM). If the adventure modules are well prepared, it is possible play a game at the table with minimal preparation time. However, this is counteracted by getting all the content into a form that allows efficient use of the capabilities of the VTT system.

The tool is intended to help out by providing basic HTML-formatted text that can just be copied into the text editor of the VTT system. The only additional effort is to break up the text into consumable snippets and add cross references and game system shortcuts, e.g. for quickly roll talent or attribute checks. This cannot be automated in a general way because it is different for all VTTs and game systems.

Obviously, it is possible to violate common usage rights by extracting information from a bundled package like a PDF file. When you use a tool like ChaosPDF, keep in mind that a re-publication of copyrighted material is usually not allwed.

***When using the ChaosPDF tool like in the use case outlined above, make sure that the content cannot be accessed without user authentication to stay within the intended usage of such publications and to avoid violating copyright laws.***
