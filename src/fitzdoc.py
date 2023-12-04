"""
 pathlib to access PDF files (in pdffiles)
 logging for logging and debugging
 re for analyzing text with regular expressions
 collections for finding unique items of lists
 fitz from pymupdf to process PDF documents
"""
from pathlib import Path
import logging
import re
from collections import Counter
import fitz
from fitzpage import Fitzpage

class Fitzdoc():
    def __init__(self, file:Path):
        self.log = logging.getLogger('doc')
        self.log.info('Initializing document for "%s"', file)
        self.file = file
        self.page_text = []
        self.doc = fitz.open(self.file)
        self.encryption = self.check_encryption()
        if self.encryption:
            self.log.warning('Document "%s" is encryptet, processing stopped', self.file)
            return
        self.toc = []
        self.repeating_text_to_remove = []

    def check_encryption(self):
        """
        check_encryption Check if the PDF file is encrypted and needs a password 
        to access

        :return: True if the file is encrypted and cannot be processed further
        :rtype: bool
        """
        self.log.debug('Entering method "check_encryption"')
        encryption = self.doc.needs_pass
        if encryption:
            self.log.error('Document "%s" is encrypted and cannot be processed', self.file)
        else:
            self.log.info('Document "%s" is not encrypted and can be processed normally', self.file)
        return encryption

    def get_toc(self):
        """
        get_toc gets the list of the file table of contents
        """
        self.log.debug('Entering method "get_toc"')
        self.toc = self.doc.get_toc()
        self.log.info('Read table of contents')

    def print_file_info(self):
        """
        print_file_info prints the basic file metadata to the console
        """
        self.log.debug('Entering method "print_file_info"')
        print('PDF File name:', self.doc.name)
        print('PDF Page count:', self.doc.page_count)
        print('\nMetadata\n========')
        for item in self.doc.metadata:
            print(item)
        print('\nTable of contents\n=================')
        for item in self.toc:
            # item is a list with:
            # Heading level, heading, page number, ...
            print(' '*(item[0]-1) + item[1])

    def process_pages(self, page_offset:int):
        """
        process_pages runs the XHTML text extraction for the whole document.

        :param page_offset: Offset for page number removal and logging
        :type page_offset: int
        :return: Text with HTML formatting for the whole document
        :rtype: str
        """
        self.log.debug('Entering method "process_pages"')
        self.page_text = []
        html = ''
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn+page_offset)
            content = self.extract_text_from_page(p)
            self.page_text.append(content)
            html += content
        return html

    def process_pages_separately(self, page_offset:int):
        """
        process_pages_separately runs the XHTML text extraction for the whole document. 
        It also adds additional h1 entries as page separator which makes it easier to 
        inspect the result manually.

        :param page_offset: Offset for page number removal and logging
        :type page_offset: int
        :return: Text with HTML formatting for the whole document with additional 
        page separation headings
        :rtype: str
        """
        self.log.debug('Entering method "process_pages_separately"')
        self.page_text = []
        html = ''
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn+page_offset)
            content = self.extract_text_from_page(p)
            self.page_text.append(content)
            html += f'\n\n<h1>====== Page {pn+page_offset:04d} ======</h1>\n\n'
            html += content
        return html

    def extract_text_from_page(self, page:Fitzpage):
        """
        extract_text_from_page runs the XHTML text extraction methods from the 
        Fitzpage class.

        :param page: A single page from the document
        :type page: Fitzpage
        :return: Extracted text with HTML format tags
        :rtype: str
        """
        self.log.debug('Entering method "extract_text_from_page"')
        page.get_xhtml()
        page.fix_xhtml_utf_characters()
        page.fix_xhtml_line_breaks()
        if not self.repeating_text_to_remove == []:
            for text in self.repeating_text_to_remove:
                page.remove_xhtml_repeating(text)
        page.remove_xhtml_page_number()
        return page.xhtml

    def detect_page_offset(self):
        """
        detect_page_offset tries to detect the page numbering offset that 
        the page number can be removed from the detected text.

        :return: Offset to be added to page number iterator.
        :rtype: int
        """
        # ! There is no good handling what happens if there are no page numbers detected
        self.log.debug('Entering method "detect_page_offset"')
        page_numbers = []
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn)
            p.get_block_text(False)
            numbers_on_page = []
            for paragraph in p.textblocks:
                # Find only strings that start with a number, see https://regextutorial.org/regex-for-numbers-and-ranges.php
                m = re.match(r'\d+', paragraph)
                if m is not None:
                    numbers_on_page.append(m.group(0))
                    # break
            page_numbers.append(numbers_on_page)
        # ? Return 0 if there are no pages
        if len(page_numbers) == 0:
            self.log.critical('Something went really wrong! Debugging needed!')
            return 0
        potential_offsets = []
        for pn, numbers in enumerate(page_numbers):
            if not len(numbers) == 1:
                continue
            potential_offsets.append(pn-int(numbers[0]))
        # Return 0 if no line starts with a number
        if len(potential_offsets) == 0:
            self.log.warning('Could not find any potential page numbers in document')
            return 0
        # For a discussion on this see https://stackoverflow.com/questions/6987285/find-the-item-with-maximum-occurrences-in-a-list
        most_probable_offset = max(potential_offsets, key=potential_offsets.count)
        self.log.info('Probable page offset: %d', most_probable_offset)
        return most_probable_offset

    def detect_repeating_text(self):
        """
        detect_repeating_text analyzes the full text to find paragraphs with repeating 
        content.
        There is a very high risk that this method detects too many repeating text 
        blocks! User interaction is highly recommended.

        :return: List of pairs of strings and occurences with the repeating texts
        :rtype: list
        """
        self.log.debug('Entering method "detect_repeating_text"')
        detection_threshold = 5  # How often must paragraph texts repeat to count?
        all_blocks = []
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn)
            p.get_block_text(False)
            if p.textblocks == []:
                continue
            for paragraph in p.textblocks:
                all_blocks.append(paragraph)
        unique_paragraphs = Counter(all_blocks)
        repeating_paragraphs = []
        for paragraph, num in unique_paragraphs.items():
            if num > detection_threshold:
                repeating_paragraphs.append((paragraph, num))
        return repeating_paragraphs
