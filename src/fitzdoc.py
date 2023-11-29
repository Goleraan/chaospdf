"""
 fitz from pymupdf to process PDF documents
 pathlib to access PDF files (in pdffiles)
 logging for logging and debugging
"""
from pathlib import Path
import logging
import fitz
from fitzpage import Fitzpage

class Fitzdoc():
    def __init__(self, file:Path):
        self.log = logging.getLogger('doc')
        self.log.info('Initializing document for "%s"', file)
        self.file = file
        self.doc = fitz.open(self.file)
        self.encryption = self.check_encryption()
        if self.encryption:
            self.log.warning('Document "%s" is encryptet, processing stopped', self.file)
            return
        self.get_toc()

    def check_encryption(self):
        self.log.debug('Entering method "check_encryption"')
        encryption = self.doc.needs_pass
        if encryption:
            self.log.error('Document "%s" is encrypted and cannot be processed', self.file)
        else:
            self.log.info('Document "%s" is not encrypted and can be processed normally', self.file)
        return encryption

    def get_toc(self):
        self.log.debug('Entering method "get_toc"')
        self.toc = self.doc.get_toc()
        self.log.info('Read table of contents')

    def print_file_info(self):
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

    def process_pages(self, doc:fitz.Document, page_offset:int):
        html = ''
        for pn, page in enumerate(doc):
            p = Fitzpage(page, pn+page_offset)
            p.fix_xhtml_utf_characters()
            p.fix_xhtml_line_breaks()
            # page.remove_xhtml_repeating('Repeating text defined elsewhere')
            p.fix_xhtml_page_number()
            html += p.xhtml
        return html

    def extract_text_from_page(self, page:Fitzpage):
        p = Fitzpage()