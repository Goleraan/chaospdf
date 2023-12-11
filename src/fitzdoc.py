"""
 pathlib to access PDF files (in pdffiles)
 os for image output
 logging for logging and debugging
 re for analyzing text with regular expressions
 collections for finding unique items of lists
 fitz from pymupdf to process PDF documents
 fitzpage to handle individual PDF pages
 config to use the global configuration
 outfile for image output
"""
from pathlib import Path
import os
import logging
import re
from collections import Counter
import fitz
from fitzpage import Fitzpage
from config import Config
from outfile import Outfile

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
        self.html = ''
        self.text = ''
        self.config = Config().co

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
        self.html = ''
        self.text = ''
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn+page_offset)
            content = self.extract_text_from_page(p)
            self.page_text.append(content)
            self.html += content
            self.text += p.text
        return self.html

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
        self.html = ''
        self.text = ''
        for pn, page in enumerate(self.doc):
            p = Fitzpage(page, pn+page_offset)
            content = self.extract_text_from_page(p)
            self.page_text.append(content)
            if content:
                self.html += f'\n\n<h1>====== Page {pn+page_offset:04d} ======</h1>\n\n'
                self.html += content
            if p.text:
                self.text += f'\n\n====== Page {pn+page_offset:04d} ======\n\n'
                self.text += p.text
        return self.html

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
        if self.repeating_text_to_remove:
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
                # Find only strings that start with a number, see
                # https://regextutorial.org/regex-for-numbers-and-ranges.php
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
        # For a discussion on this see
        # https://stackoverflow.com/questions/6987285/find-the-item-with-maximum-occurrences-in-a-list
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
            if not p.textblocks:
                continue
            for paragraph in p.textblocks:
                all_blocks.append(paragraph)
        unique_paragraphs = Counter(all_blocks)
        repeating_paragraphs = []
        for paragraph, num in unique_paragraphs.items():
            if num > detection_threshold:
                repeating_paragraphs.append((paragraph, num))
        return repeating_paragraphs

    def extract_images(self):
        """Extract images from a PDF document and write them to the output directory.
        Inspired by https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-images/extract-from-xref.py
        License: GNU GPL V3
        (c) 2018 Jorj X. McKie
        
        Some parts are rewritten for the purpose of this method.
        """
        self.log.debug('Entering method "extract_images"')
        outfile = Outfile(self.file)
        output_dir = outfile.location
        #
        xref_count = self.doc.xref_length()
        softmasks = set()
        img_count = 0
        total_img_count = 0
        softmask_count = 0
        recover_count = 0
        remove_count = 0
        #
        # Loop over all cross references of the document
        for xref in range(1, xref_count):
            try:
                if self.doc.xref_get_key(xref, 'Subtype')[1] != '/Image':
                    # Skip all cross references that are not images
                    continue
            except RuntimeError as e:
                self.log.error('Error during image extraction for xref %s:\n%s', xref, e)
                continue

            total_img_count += 1

            if xref in softmasks:
                # Skip all cross references that are soft masks
                softmask_count += 1
                continue

            imgdict = self.doc.extract_image(xref)
            if not imgdict:
                # Skip all cross references of type image that are broken
                continue

            softmask = imgdict['smask']  # reference to a linked soft mask
            if softmask > 0:
                # Remember that there is a soft mask, could be referenced multiple times
                softmasks.add(softmask)
            #
            # Outsource some properties of the image dictionary for descriptive access
            extension = imgdict['ext']
            imgdata = imgdict['image']
            width = imgdict['width']
            height = imgdict['height']
            imgsize = len(imgdata)
            #
            if width <= self.config.fitz.images.image_dimension_x_min or\
               height <= self.config.fitz.images.image_dimension_y_min:
                # Skip image if an edge is too small
                continue
            if imgsize < self.config.fitz.images.image_size_min:
                # Skip image if its total file size is too small
                continue
            #
            # Recover the image transparency if there is a soft mask
            if softmask > 0:
                imgdict = self.recover_picture(self.doc, imgdict)
                if imgdict is None:
                    # Something went wrong, skip image
                    continue
                recover_count += 1
                extension = 'png'  # change file extension to png to consider transparency
                # Overwrite image data with recovered data that includes alpha channel
                imgdata = imgdict['image']
                samplesize = width * height * 3
                imgsize = len(imgdata)
            else:
                # There is no soft mask, no recovery needed
                samplesize = width * height * max(1, imgdict['colorspace'])
            #
            if imgsize / samplesize <= self.config.fitz.images.compression_limit:
                # Skip image if it's compressed to less than 5% (compression_limit) of its full size
                # These are typically unicolor images that are of no interest
                continue
            #
            # Write image
            imgname = str(xref) + '.' + extension
            outfile.save_fitz_image(imgdata, imgname)
            img_count += 1
        #
        # Remove all soft masks that were written as image file because they slipped
        # through the previous filter process
        if len(softmasks) > 0:
            remove_count = outfile.remove_fitz_softmasks(softmasks)
        #
        self.log.debug('Detected cross references: %d', xref_count)
        self.log.debug('Detected images: %d', total_img_count)
        self.log.debug('Detected soft mask images: %d', softmask_count)
        self.log.debug('Detected relevant images: %d', img_count)
        self.log.debug('Recovered transparency with soft masks: %d',
                       recover_count)
        self.log.debug('Cleanup of slipped soft masks: %d', remove_count)
        self.log.debug('Finished image extraction for %s', self.doc.name)

    def recover_picture(self, doc:fitz.Document, imgdict):
        """Code from: https://github.com/pymupdf/PyMuPDF-Utilities/blob/master/examples/extract-images/extract-from-xref.py
        GNU GPL V3
        (c) 2018 Jorj X. McKie
        
        Minor adjustment: removed unnecessary argument of cross reference.
        
        Recovers the pixelmap for a provided image dictionary by applying the soft mask
        (alpha channel) and making a single data structure out of it that it can be
        saved as PNG.

        Args:
            doc (fitz.Document): The PyMuPDF object for a PDF file.
            imgdict (dict): Dictionary for an image extracted from doc.

        Returns:
            dict: Updated dictionary for an image that includes the alpha channel information.
        """
        self.log.debug('Entering method "recover_picture"')
        smask = imgdict['smask']

        try:
            pix0 = fitz.Pixmap(imgdict['image'])
            mask = fitz.Pixmap(doc.extract_image(smask)['image'])
            pix = fitz.Pixmap(pix0, mask)
            if pix0.n > 3:
                ext = 'pam'
            else:
                ext = 'png'
            return {'ext': ext, 'colorspace': pix.colorspace.n, 'image': pix.tobytes(ext)}
        except Exception as e:
            self.log.error('Image recovery failed with:\n%s', e)
            return None
