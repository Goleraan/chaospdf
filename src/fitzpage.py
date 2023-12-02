"""
 logging for logging and debugging
 re for regex replacements
 fitz from pymupdf to process PDF documents
"""
import logging
import re
import fitz

class Fitzpage():
    """
    Fitzpage uses PyMuPDF to extract and process text from PDF documents. It offers various 
    helper functions to clean-up the extracted plain text or in xHTML format, which contains 
    some of the original formatting in old-school HTML without CSS.
    """
    def __init__(self, page:fitz.Page, index:int):
        self.log = logging.getLogger('page')
        self.log.debug('Initializing page %s', str(index))
        self.page = page
        self.pagenumber = str(self.page).split()[1]  # PDF page from document
        self.index = index  # Page number including offset
        self.text = ''  # Extracted text (by get_plain_text or get_block_text)
        self.textblocks = []  # Extracted text blocks by get_block_text
        self.html = ''  # Extracted HTML code by get_html
        self.xhtml = ''  # Extracted XHTML code by get_xhtml
        self.xhtml_ligatures = ''  # Extracted XHTML code by get_xhtml without
                                   # processing ligatures
                                   # NOT USED, CODE IS STILL IN BUT DISABLED
        self.dicttext = {}  # Extracted dictionary by get_dict
        self.executed = {'get_plain_text': False,
                         'get_block_text': False,
                         'fix_text_ligature_spaces': False,
                         'fix_text_line_breaks': False,
                         'remove_text_page_number': False,
                         'remove_text_repeating': False,
                         'repeating_text': [],
                         'get_html': False,
                         'get_dict_text': False,
                         'get_xhtml': False,
                         'fix_xhtml_ligature_spaces': False,
                         'remove_xhtml_repeating': False,
                         'repeating_xhtml': [],
                         'remove_xhtml_page_number': False,
                         'fix_xhtml_line_breaks': False,
                         'fix_xhtml_utf_characters': False}

    def get_plain_text(self, sorting:bool):
        """
        get_plain_text Extracts text from a PDF file in plain text format.

        :param sorting: True to attempt sorting the PDF elements from top to bottom
        :type sorting: bool
        :return: The detected text as one string
        :rtype: str
        """
        self.log.debug('Entering method "get_plain_text"')
        # Flags see https://pymupdf.readthedocs.io/en/latest/vars.html#textpreserve
        self.text = self.page.get_text('text',
                                       flags=fitz.TEXT_PRESERVE_WHITESPACE+
                                             fitz.TEXT_DEHYPHENATE,
                                       sort=sorting)
        if self.text == '':
            self.log.error('Could not detect any text in plain text '+
                           'format on page %s with index %s',
                           self.pagenumber, self.index)
        self.executed['get_plain_text'] = True
        return self.text

    def get_block_text(self, sorting:bool):
        """
        get_block_text Extracts text from a PDF file block by block or 
        paragraph by paragraph

        :param sorting: True to attempt sorting the PDF elements from top to bottom
        :type sorting: bool
        :return: The detected text as one string
        :rtype: str
        """
        self.log.debug('Entering method "get_block_text"')
        # Detect the text blocks
        blocks = self.page.get_text('blocks',
                                    flags=fitz.TEXT_PRESERVE_WHITESPACE+
                                          fitz.TEXT_DEHYPHENATE,
                                    sort=sorting)
        self.textblocks = []
        for block in blocks:
            # Remove page number
            # if block[4].startswith(str(self.index)) or block[4].endswith(str(self.index)):
            #     continue
            self.textblocks.append(block[4].replace('\n',''))
        if len(self.textblocks) == 0:
            self.log.error('Could not detect any text in block format '+
                           'on page %s with index %s, attempting to get plain text',
                           self.pagenumber, self.index)
            self.get_plain_text(sorting)
            return self.text
        # Convert the text blocks into a single string
        self.text = ''
        for block in self.textblocks:
            self.text += block
            # Special case: hyphenation at the end of a block
            # This might give unexpected results at the end of a page
            # because of a missing line break
            if self.text.endswith('-'):
                self.text = self.text[0:len(self.text)-1]
            else:
                self.text += '\n'
        self.text = self.text.replace('…', '...')
        self.executed['get_block_text'] = True
        return self.text

    def fix_text_ligature_spaces(self):
        """
        fix_text_ligature_spaces attempts to fix additional space characters after ligatures.
        It is not clear what causes the additional spaces, the PDF itself or PyMuPDF.
        For the tested PDFs, there was always an additional space after a ligature, regardless 
        of the flag fitz.TEXT_PRESERVE_LIGATURES.
        It is possible, that it removes too many spaces, if the ligature is at the end of the 
        line.
        It overwrites self.text with the corrected text but does not touch self.textblocks.

        :return: The corrected text
        :rtype: str
        """
        self.log.debug('Entering method "fix_text_ligature_spaces"')
        if not self._check_text_data():
            self.log.error('No plain text data available, aborting fix_text_ligature_spaces')
            return self.text
        # The implementation is not robust because there is only one space
        # at the end of the words like 'ist' or 'Stoff'
        # Only a spell checker could fix this issue for known words
        self.text = self.text.replace('ff ', 'ff')
        self.text = self.text.replace('fi ', 'fi')
        self.text = self.text.replace('fl ', 'fl')
        self.text = self.text.replace('ffi ', 'ffi')
        self.text = self.text.replace('ffl ', 'ffl')
        self.text = self.text.replace('ft ', 'ft')
        self.text = self.text.replace('st ', 'st')
        self.executed['fix_text_ligature_spaces'] = True
        return self.text

    def fix_text_line_breaks(self):
        """
        fix_text_line_breaks attempts to add paragraph line breaks by 
        looking for missing spaces after a period followed by a captial letter.
        It overwrites self.text with the corrected text but does not touch 
        self.textblocks.

        :return: Corrected text
        :rtype: str
        """
        self.log.debug('Entering method "fix_text_line_breaks"')
        if not self._check_text_data():
            self.log.error('No plain text data available, aborting fix_text_line_breaks')
            return self.text
        # Idea:
        #  - Find all appearances of strings like ".D", where a capital letter 
        #    follows a period
        #  - Save these in a list
        #  - In the original string, replace each of these with a line break 
        #    between the period and the letter
        # The implementation might run too many replace operations because of 
        # duplicate entries in the list. This should only increase the run time 
        # and not harm the text itself.
        breaks = re.findall(r'\.[A-ZÄÖÜ]', self.text)
        if len(breaks) > 0:
            for lb in breaks:
                self.text = self.text.replace(lb, lb[0]+'\n'+lb[1])
        self.executed['fix_text_line_breaks'] = True
        return self.text

    def remove_text_page_number(self):
        """
        remove_text_page_number attempts to remove page numbers within the detected text.
        It checks for three different conditions:
        1. The page number is at the beginning of the page, followed by a line break.
        2. The page number is at the end of the page, followed by a line break.
        3. The page number stands by itself with a line break before and after the number.
        It overwrites self.text with the corrected text but does not touch self.textblocks.

        :return: Corrected text
        :rtype: str
        """
        self.log.debug('Entering method "remove_text_page_number"')
        if not self._check_text_data():
            self.log.error('No plain text data available, aborting remove_text_page_number')
            return self.text
        # probably easier to do within get_block_text()
        if self.text.startswith(f'{self.index}\n'):
            self.log.debug('Found the page number at the beginning of the page')
            self.text = self.text[len(str(self.index))+1:]
        elif self.text.endswith(f'\n{self.index}'):
            self.log.debug('Found the page number at the end of the page')
            self.text = self.text[:-len(str(self.index))]  # does this work??
        else:
            self.log.debug('Attempting to remove the page number somewhere else on the page')
            self.text = self.text.replace(f'\n{self.index}\n', '')
        self.executed['remove_text_page_number'] = True
        return self.text

    def remove_text_repeating(self, text:str):
        """
        remove_text_repeating removes the specified string from the detected text, 
        if it is followed by a line break.
        This is useful to remove things like watermarks or chapter titles that 
        repeat on every page throughout a document.
        It overwrites self.text with the corrected text but does not touch self.textblocks.

        :param text: Text that should be removed from a page.
        :type text: str
        :return: Corrected page text
        :rtype: str
        """
        # probably easier to do within get_block_text()
        self.log.debug('Entering method "remove_text_repeating"')
        if not self._check_text_data():
            self.log.error('No plain text data available, aborting remove_text_repeating')
            return self.text
        self.text = self.text.replace(text+'\n', '')
        self.executed['remove_text_repeating'] = True
        self.executed['repeating_text'].append(text)
        return self.text

    def _check_text_data(self):
        """
        _check_text_data tests if a non-empty string is stored in self.text.
        The method should be used in other text processing methods to ensure 
        there is text available for processing.
        If there is no text available, it attempts to run get_block_text(False). 
        If that fails, it attempts to run get_plain_text(False) to extract some 
        text. If that fails, too, it returns False, otherwise True for a 
        successful check.

        :return: True when self.text is not empty, False if it's ''
        :rtype: bool
        """
        self.log.debug('Entering method "_check_text_data"')
        check_success = False
        if self.text == '':
            self.log.warning('No previously extracted text detected, '+
                             'attempting to extract text as blocks')
            self.get_block_text(False)
            check_success = True
            if self.text == '':
                self.log.warning('Could not extract any text in block '+
                                 'text format from page %s with index %s, '+
                                 'attempting plain text detection',
                                 self.pagenumber, self.index)
                self.get_plain_text(False)
                if self.text == '':
                    self.log.error('Could not extract any text in plain '+
                                   'text format from page %s with index %s',
                                   self.pagenumber, self.index)
                    check_success = False
        else:
            check_success = True
        self.log.info('Result of _check_text_data: %s', check_success)
        return check_success

    def get_html(self):
        """
        get_html extracts text from a PDF file in HTML format.
        The output contains all formatting statements, which makes the result difficult 
        to process further without cleaning up the code.

        :return: The extracted text with HTML code including formatting.
        :rtype: str
        """
        self.log.debug('Entering method "get_html"')
        self.html = self.page.get_text('html',
                                       flags=fitz.TEXT_PRESERVE_WHITESPACE+
                                             fitz.TEXT_DEHYPHENATE)
        self.executed['get_html'] = True
        return self.html

    def get_dict_text(self):
        """
        get_dict_text extracts the text with all formatting and positions as dictionary.
        Mostly useless for standard text extraction tasks.

        :return: Dictionary of all text elements on a page.
        :rtype: dict
        """
        self.log.debug('Entering method "get_dict_text"')
        self.dicttext = self.page.get_text('dict',
                                           flags=fitz.TEXT_PRESERVE_LIGATURES+
                                                 fitz.TEXT_PRESERVE_WHITESPACE+
                                                 fitz.TEXT_DEHYPHENATE)
        self.executed['get_dict_text'] = True
        return self.dicttext

    def get_xhtml(self):
        """
        get_xhtml extracts text from a PDF document in XHTML format.
        This format seems to be the most useful to get all the text with 
        formatting. Paragraphs within a text block are NOT detected and 
        must be recovered later from self.text with fix_xhtml_line_breaks().

        :return: Text with basic HTML formatting.
        :rtype: str
        """
        self.log.debug('Entering method "get_xhtml"')
        # self.xhtml = self.page.get_text('xhtml',
        #                                 flags=fitz.TEXT_PRESERVE_WHITESPACE+
        #                                       fitz.TEXT_DEHYPHENATE)
        self.xhtml = self.page.get_text('xhtml',
                                        flags=fitz.TEXT_PRESERVE_LIGATURES+
                                              fitz.TEXT_PRESERVE_WHITESPACE+
                                              fitz.TEXT_DEHYPHENATE)
        # self.xhtml_ligatures = self.page.get_text('xhtml',
        #                                           flags=fitz.TEXT_PRESERVE_LIGATURES+
        #                                                 fitz.TEXT_PRESERVE_WHITESPACE+
        #                                                 fitz.TEXT_DEHYPHENATE)
        if self.xhtml == '':
            self.log.error('Could not detect any text in xhtml format '+
                           'on page %s with index %s',
                           self.pagenumber, self.index)
            return self.xhtml
        self.xhtml = self.xhtml.replace('<div id="page0">\n', '')
        self.xhtml = self.xhtml.replace('</div>\n', '')
        self.xhtml = self.xhtml.replace('-</p>\n<p>', '')
        # self.xhtml_ligatures = self.xhtml_ligatures.replace('<div id="page0">\n', '')
        # self.xhtml_ligatures = self.xhtml_ligatures.replace('</div>\n', '')
        # self.xhtml_ligatures = self.xhtml_ligatures.replace('-</p>\n<p>', '')
        self.executed['get_xhtml'] = True
        return self.xhtml

    def fix_xhtml_ligature_spaces(self):
        """
        fix_xhtml_ligature_spaces tries to remove additional space characters after 
        ligatures. This is not very robust and might remove too many spaces when the 
        ligature is at the end of a word.
        It seems to be better to use the option fitz.TEXT_PRESERVE_LIGATURES in get_xhtml 
        and replace the ligatures with the method fix_xhtml_utf_characters.
        It overwrites self.xhtml with the corrected text.

        :return: Corrected text
        :rtype: str
        """
        self.log.debug('Entering method "fix_xhtml_ligature_spaces"')
        if not self._check_xhtml_data():
            self.log.error('No xhtml data available, aborting fix_xhtml_ligature_spaces')
            return self.xhtml
        self.log.warning('It is recommended to run fix_xhtml_utf_characters '+
                         'to fix ligatures together with the '+
                         'fitz.TEXT_PRESERVE_LIGATURES flag in get_xhtml')
        self.xhtml = self.xhtml.replace('ff ', 'ff')
        self.xhtml = self.xhtml.replace('fi ', 'fi')
        self.xhtml = self.xhtml.replace('fl ', 'fl')
        self.xhtml = self.xhtml.replace('ffi ', 'ffi')
        self.xhtml = self.xhtml.replace('ffl ', 'ffl')
        self.xhtml = self.xhtml.replace('ft ', 'ft')
        self.xhtml = self.xhtml.replace('st ', 'st')
        self.executed['fix_xhtml_ligature_spaces'] = True
        return self.xhtml

    def remove_xhtml_repeating(self, text:str):
        """
        remove_xhtml_repeating tries to remove the provided string from the extracted text. 
        The string should be located on its own line, like it is the case for repeated 
        chapter headings or watermarks.
        The method removes the text if it stands by itself, when it is within a heading, or 
        within paragraph tags. This also removes the real heading, though.
        It overwrites self.xhtml with the corrected text.

        :param text: Text that should be removed.
        :type text: str
        :return: Corrected text
        :rtype: str
        """
        # probably easier to do within get_xhtml()
        self.log.debug('Entering method "remove_text_repeating"')
        if not self._check_xhtml_data():
            self.log.error('No xhtml data available, aborting remove_xhtml_repeating')
            return self.xhtml
        self.xhtml = self.xhtml.replace(text+'\n', '')
        self.xhtml = re.sub(text+r'\n', '', self.xhtml)
        self.xhtml = re.sub(r'<h[1-6]>'+text+r'</h[1-6]>\n', '', self.xhtml)
        self.xhtml = re.sub(r'<h[1-6]><b>'+text+r'</b></h[1-6]>\n', '', self.xhtml)
        self.xhtml = re.sub(r'<h[1-6]><i>'+text+r'</i></h[1-6]>\n', '', self.xhtml)
        self.xhtml = re.sub(r'<p>'+text+r'</p>\n', '', self.xhtml)
        self.xhtml = re.sub(r'<p><b>'+text+r'</b></p>\n', '', self.xhtml)
        self.xhtml = re.sub(r'<p><i>'+text+r'</i></p>\n', '', self.xhtml)
        self.executed['remove_xhtml_repeating'] = True
        self.executed['repeating_xhtml'].append(text)
        return self.xhtml

    def remove_xhtml_page_number(self):
        """
        remove_xhtml_page_number tries to remove the page number from the extracted text.
        If the page number stands by itself in a line, or within arbitrary tags, it is 
        deleted.
        The method also removes empty lines which are not needed within HTML code.
        It overwrites self.xhtml with the corrected text.

        :return: Corrected text
        :rtype: str
        """
        self.log.debug('Entering method "remove_xhtml_page_number"')
        if not self._check_xhtml_data():
            self.log.error('No xhtml data available, aborting remove_xhtml_page_number')
            return self.xhtml
        xhtml = ''
        for line in self.xhtml.split('\n'):
            if line == str(self.index):
                continue
            elif '>'+str(self.index)+'<' in line:
                continue
            elif line == '':
                continue
            else:
                xhtml += line+'\n'
        self.xhtml = xhtml
        self.executed['remove_xhtml_page_number'] = True
        return self.xhtml

    def _xhtml_replacements(self):
        """
        _xhtml_replacements helper method for fix_xhtml_line_breaks()
        It removes incorrect paragraphs due to multi-column layout.
        It also removes unnecessary HTML tags.
        """
        self.xhtml = self.xhtml.replace(' </p>\n<p>', ' ')  # Fix multi-column-layout
        self.xhtml = self.xhtml.replace(' </p><p>', ' ')
        self.xhtml = self.xhtml.replace('<b> </b>', '')  # Remove unnecessary tags
        self.xhtml = self.xhtml.replace('<i> </i>', '')  # Remove unnecessary tags

    def _xhtml_inline_headings(self):
        """
        _xhtml_inline_headings adds additional line breaks for in-line headings 
        in HTML format. Helper method for fix_xhtml_line_breaks().
        """
        missing_line_breaks = [(hits.start(0), hits.end(0))
                               for hits in re.finditer(r'</h[1-6]><p>', self.xhtml)]
        out = ''
        if len(missing_line_breaks) > 0:
            start = 0
            for first, last in missing_line_breaks:
                out += self.xhtml[start:first+5]+'\n'
                start = first+5
            out += self.xhtml[start:]
        if out != '':
            self.xhtml = out
        # splithtml = self.xhtml.split('\n')
        # inline_heading_count = self.xhtml.count('><p>')
        # # Fix in-line headings in text
        # if inline_heading_count > 0:
        #     for html_paragraph in splithtml:
        #         if html_paragraph.startswith('<h') and html_paragraph.endswith('</p>'):
        #             endpos = html_paragraph.find('</')
        #             sub = html_paragraph[:endpos]
        #             startpos = sub.rfind('>')
        #             sub = sub[startpos+1:]
        #             pos = self.text.find(sub)
        #             self.text = self.text[:pos+len(sub)]+'\n'+self.text[pos+len(sub):]
        #     self.xhtml = self.xhtml.replace('><p>', '>\n<p>')  # Fix in-line headings in HTML

    def _xhtml_line_breaks_text_processing(self):
        """
        _xhtml_line_breaks_text_processing applies the same text processing operations 
        to a block text detection as they are applied to the xhtml steps. This is 
        needed as first step of three to add the paragraphs within a text block that 
        the xhtml extraction cannot recover by itself.
        """
        self.get_block_text(False)
        if (self.executed['fix_xhtml_utf_characters'] or
            self.executed['fix_xhtml_ligature_spaces']):
            self.fix_text_ligature_spaces()
        self.fix_text_line_breaks()
        if self.executed['remove_xhtml_page_number']:
            self.remove_text_page_number()
        if self.executed['remove_xhtml_repeating']:
            for text in self.executed['repeating_xhtml']:
                self.remove_text_repeating(text)

    def _xhtml_line_breaks_recover_breaks(self):
        """
        _xhtml_line_breaks_recover_breaks recovers the paragraph line breaks by 
        splitting text and html by line breaks. It looks for the list items that 
        start and end with paragraph tags in the html code and counts the period 
        characters in both, text and html. If there is a mismatch, it recovers the 
        missing paragraph + line break in the html-derived list.
        In the end, both lists should have the same length.

        :return: The list for the html code with one heading or paragraph for each 
        list item
        :rtype: list
        """
        # Column breaks with hyphenation between them
        # The fitz.TEXT_DEHYPHENATE will merge the columns together on text 
        # extraction but not for XHTML extraction. Column breaks without 
        # hyphenation stay separate in both and must be treated later
        self.xhtml = self.xhtml.replace('-</i></p>\n<p><i>', '')
        self.xhtml = self.xhtml.replace('-</b></p>\n<p><b>', '')
        splittext = self.text.split('\n')
        splithtml = self.xhtml.split('\n')
        for i, text_paragraph in enumerate(splittext):
            if i >= len(splithtml):
                self.log.error('Mismatch in text and HTML number of paragraphs in '+
                               'fix_xhtml_line_breaks for line %s', i)
                break
            if splithtml[i].endswith('</p>'):
                # Count the number of periods in both texts.
                # Direct text length comparison does not work because there can be 
                # offsets due to the text operations like ligature handling.
                period_count_text = text_paragraph.count('.')
                period_count_html = splithtml[i].count('.')
                period_positions = []
                # If the HTML code contains more periods, it's missing in-block paragraphs.
                # They can be recovered by the using the positions of the periods.
                case1 = (period_count_text < period_count_html) and (
                         period_count_text > 0)
                case2 = splithtml[i].endswith(':</p>') and not (
                        text_paragraph.endswith(':')) and (
                        period_count_text > 0)
                case3 = text_paragraph.endswith('.') and not (
                        splithtml[i].endswith('.</p>') or (
                            splithtml[i].endswith('.</i></p>')) or (
                            splithtml[i].endswith('.</b></p>'))) and (
                        period_count_text > 0)
                if case1 or case2 or case3:
                    for pos, char in enumerate(splithtml[i]):
                        if char == '.':
                            period_positions.append(pos)
                    if i+1 < len(splithtml):
                        splithtml.insert(i+1, '<p>'+splithtml[i][period_positions[period_count_text-1]+2:])
                    else:
                        splithtml.append('<p>'+splithtml[i][period_positions[period_count_text-1]+2:])
                    splithtml[i] = splithtml[i][:period_positions[period_count_text-1]+1]+'</p>'
                # elif splithtml[i].endswith(':</p>') and not text_paragraph.endswith(':'):
                #     for pos, char in enumerate(splithtml[i]):
                #         if char == '.':
                #             period_positions.append(pos)
                #     splithtml.insert(i+1, '<p>'+splithtml[i][period_positions[period_count_text-1]+2:])
                #     splithtml[i] = splithtml[i][:period_positions[period_count_text-1]+1]+'</p>'
                # elif text_paragraph.endswith('.') and not (splithtml[i].endswith('.</p>') or splithtml[i].endswith('.</i></p>') or splithtml[i].endswith('.</b></p>')):
                #     for pos, char in enumerate(splithtml[i]):
                #         if char == '.':
                #             period_positions.append(pos)
                #     splithtml.insert(i+1, '<p>'+splithtml[i][period_positions[period_count_text-1]+2:])
                #     splithtml[i] = splithtml[i][:period_positions[period_count_text-1]+1]+'</p>'
        if len(splittext) != len(splithtml):
            self.log.error('After recovering the in-block paragraphs in '+
                           '_xhtml_inline_headings() which is called from '+
                           'fix_xhtml_line_breaks(), there is a mismatch in '+
                           'the number of paragraphs but they should be the same!\n'+
                           'Paragraphs in text format: %s\n'+
                           '%s'+
                           'Paragraphs in HTML format: %s'+
                           '%s',
                           len(splittext), self.text , len(splithtml), self.xhtml)
        # Only for testing:
        # print(f'Final length text: {len(splittext)} - html: {len(splithtml)}')
        # for i in range(0,len(splittext)):
        #     print('=== TEXT ===')
        #     print(splittext[i])
        #     print('=== HTML ===')
        #     if i < len(splithtml):
        #         print(splithtml[i])
        #     print()
        return splithtml

    def TESTING_xhtml_line_breaks_recover_breaks(self):
        """
        _xhtml_line_breaks_recover_breaks recovers the paragraph line breaks by 
        splitting text and html by line breaks. It looks for the list items that 
        start and end with paragraph tags in the html code and counts the period 
        characters in both, text and html. If there is a mismatch, it recovers the 
        missing paragraph + line break in the html-derived list.
        In the end, both lists should have the same length.

        :return: False if there was an error during paragraph recovery
        :rtype: bool
        """
        # Column breaks with hyphenation between them
        # The fitz.TEXT_DEHYPHENATE will merge the columns together on text 
        # extraction but not for XHTML extraction. Column breaks without 
        # hyphenation stay separate in both and must be treated later
        self.xhtml = self.xhtml.replace('-</i></p>\n<p><i>', '')
        self.xhtml = self.xhtml.replace('-</b></p>\n<p><b>', '')
        # self.xhtml = self.xhtml.replace(' </p>\n<p>', ' ')
        # Analyze the text line by line
        html_len = len(self.xhtml)
        text_len = len(self.text)
        character_count = max(text_len, html_len)
        self.text_new = ''
        self.xhtml_new = ''
        # Go through the text
        self.html_offset = 0
        self.text_offset = 0
        text_out_of_range = False
        html_out_of_range = False
        continue_index = 0
        for i in range(0, character_count):
            # Security check to not run out of range in either of the strings!
            if i >= text_len:
                text_out_of_range = True
                continue_index = i
                break
            if i >= html_len:
                html_out_of_range = True
                continue_index = i
                break
            # Check and add characters
            repeat_check = True
            while repeat_check:
                self.i_text = i + self.text_offset
                self.i_html = i + self.html_offset
                self.ct = self.text[self.i_text]
                self.ch = self.xhtml[self.i_html]
                # if self.ch == '.':
                #     print(i)
                if i == 1224:
                    print(i)
                # Skip over HTML tags
                self._keep_html_tag(html_len)
                self.i_html = i + self.html_offset
                self.ch = self.xhtml[self.i_html]
                repeat_check = self._add_characters()
        if text_out_of_range:
            for i in range(continue_index, character_count):
                if i+self.html_offset >= character_count:
                    break
                self.xhtml_new += self.xhtml[i+self.html_offset]
                self.text_new += '\n'
        if html_out_of_range:
            print('ERROR, HTML code is too short!!!')
            return False
        self.xhtml = self.xhtml_new
        self.text = self.text_new
        return True

    def _add_characters(self):
        # The order of the checks is important to cover the 
        # column breaks. Space must be before line break
        if self.ch == self.ct:
            self.text_new += self.ct
            self.xhtml_new += self.ch
            return False
        elif self.ch == ' ' and not self.ct == ' ':
                    # HTML has space, text not > add space to text
                    # Text character must be processed again
            self.text_new += self.ch
            self.xhtml_new += self.ch
            self.html_offset += 1
            return True
        elif self.ct == ' ' and not self.ch == ' ':
            self.text_new += self.ch
            self.xhtml_new += self.ch
            self.text_offset += 1
            return True
        elif self.ch == '\n' and not self.ct == '\n':
            # HTML line breaks > add line break to text
            self.text_new += self.ch
            self.xhtml_new += self.ch
            self.html_offset += 1
            # self._keep_next_html_tag()
            # test_next_char = True
            # while test_next_char:
            #     self.ch = self.xhtml[self.i_html+1]
            #     # self.html_offset += 1
            #     begin = self.i_html+1
            #     if self.ch == '<':
            #         for ci in range(begin, len(self.xhtml)):
            #             self.ch = self.xhtml[ci]
            #             self.xhtml_new += self.ch
            #             self.html_offset += 1
            #             self.i_html += 1
            #             if self.ch == '>':
            #                 break
            #     else:
            #         test_next_char = False
            return True
        elif self.ct == '\n' and not self.ch == '\n':
            # Text line breaks > add line break to HTML
            self._keep_next_html_tag()
            return False
        elif self.ch == '-' and not self.ct == '-':
            # Handling of layout error when a headline repeats on every 
            # page and is somewhere inside the text with hyphenation
            self.text_new += self.ch
            self.xhtml_new += self.ch
            self.html_offset += 1
            return True
        else:
            # TODO mismatch is not handled robustly
            self.text_new += self.ch
            self.xhtml_new += self.ch
            return False

    def _keep_next_html_tag(self):
        test_next_char = True
        while test_next_char:
            self.ch = self.xhtml[self.i_html]
            if self.ch == '<':
                for ci in range(self.i_html, len(self.xhtml)):
                    self.ch = self.xhtml[ci]
                    self.xhtml_new += self.ch
                    self.html_offset += 1
                    # TODO THIS DOES NOT SEEM RIGHT
                    self.i_html += 1  # ??
                    if self.ch == '>':
                        break
            else:
                test_next_char = False
        self.text_new += self.ct
        self.xhtml_new += self.ct

    def _keep_html_tag(self, html_len):
        if self.ch == '<':
            self.search_tag_close = False
            for ci in range(self.i_html,html_len):
                self.ch = self.xhtml[ci]
                if self.ch == '<' or self.search_tag_close:
                    self.xhtml_new += self.ch
                    self.html_offset += 1
                    self.search_tag_close = True
                else:
                    break
                if self.ch == '>':
                    self.search_tag_close = False

    def _xhtml_line_breaks_assemble_html(self, splithtml:list):
        """
        _xhtml_line_breaks_assemble_html takes the output of 
        _xhtml_line_beraks_recover_breaks() to re-assemble the HTML code 
        as a single text string.

        :param splithtml: List of HTML code lines as strings
        :type splithtml: list
        """
        self.xhtml = ''
        for line in splithtml:
            if line == '\n' or line == '\r\n' or line == '':
                continue
            self.xhtml += line+'\n'

    def fix_xhtml_line_breaks(self):
        """
        fix_xhtml_line_breaks adds additional paragraphs that PyMuPDF ignores 
        during XHTML extraction.
        The paragraphs exist for block text extractions. By comparing the output 
        of both methods it is possible to get a clean output with multiple 
        paragraphs.

        :return: Cleaned up HTML code with multiple paragraphs
        :rtype: str
        """
        self.log.debug('Entering method "fix_xhtml_line_breaks"')
        if not self._check_xhtml_data():
            self.log.error('No xhtml data available, aborting fix_xhtml_line_breaks')
            return self.xhtml
        # Text needed later, for empty page the process can be stopped here
        if not self._check_text_data():
            self.log.error('No text data available, aborting fix_xhtml_line_breaks')
            return self.xhtml

        # self._xhtml_line_breaks_text_processing()
        self.get_block_text(False)
        self.fix_text_ligature_spaces()
        self.TESTING_xhtml_line_breaks_recover_breaks()
        # splithtml = self._xhtml_line_breaks_recover_breaks()
        # self._xhtml_line_breaks_assemble_html(splithtml)
        self._xhtml_inline_headings()
        self._xhtml_replacements()  # Fixes for multi-column layout and unnecessary tags
        #
        # Add additional line breaks due to paragraphs
        # First, get the block text without sorting, like it's done for XHTML
        # and apply the same text processing options
        # self._xhtml_line_breaks_text_processing()
        # Second, find the line breaks and split the HTML
        # Third, assemble the full HTML again

        self.executed['fix_xhtml_line_breaks'] = True
        return self.xhtml

    def fix_xhtml_utf_characters(self):
        """
        fix_xhtml_utf_characters replaces the HTML codes for non-ASCII characters with 
        unicode characters in the extracted XHTML data for easier processing.
        It modifies self.xhtml directly.

        :return: Corrected HTML using unicode instead of ASCII
        :rtype: str
        """
        self.log.debug('Entering method "fix_xhtml_utf_characters"')
        if not self._check_xhtml_data():
            self.log.error('No xhtml data available, aborting fix_xhtml_utf_characters')
            return self.xhtml
        # Replacements: https://de.wikipedia.org/wiki/Hilfe:Sonderzeichenreferenz
        self.xhtml = self.xhtml.replace('&amp;', '&')
        self.xhtml = self.xhtml.replace('&#x21;', '!')
        self.xhtml = self.xhtml.replace('&#x23;', '#')
        self.xhtml = self.xhtml.replace('&#x24;', '$')
        self.xhtml = self.xhtml.replace('&#x25;', '%')
        self.xhtml = self.xhtml.replace('&#x26;', '&')
        self.xhtml = self.xhtml.replace('&#x27;', "'")
        self.xhtml = self.xhtml.replace('&#x28;', '(')
        self.xhtml = self.xhtml.replace('&#x29;', ')')
        self.xhtml = self.xhtml.replace('&#x2a;', '*')
        self.xhtml = self.xhtml.replace('&#x2b;', '+')
        self.xhtml = self.xhtml.replace('&#x2c;', ',')
        self.xhtml = self.xhtml.replace('&#x2e;', '.')
        self.xhtml = self.xhtml.replace('&#x2f;', '/')
        self.xhtml = self.xhtml.replace('&#x3a;', ':')
        self.xhtml = self.xhtml.replace('&#x3b;', ';')
        self.xhtml = self.xhtml.replace('&#x3d;', '=')
        self.xhtml = self.xhtml.replace('&#x3f;', '?')
        self.xhtml = self.xhtml.replace('&#x40;', '@')
        self.xhtml = self.xhtml.replace('&#x5b;', '[')
        self.xhtml = self.xhtml.replace('&#x5d;', ']')
        self.xhtml = self.xhtml.replace('&#x5c;', '\\')
        self.xhtml = self.xhtml.replace('&#xa0;', ' ')
        self.xhtml = self.xhtml.replace('&#xa1;', '¡')
        self.xhtml = self.xhtml.replace('&#xa2;', '¢')
        self.xhtml = self.xhtml.replace('&#xa3;', '£')
        self.xhtml = self.xhtml.replace('&#xa4;', '¤')
        self.xhtml = self.xhtml.replace('&#xa5;', '¥')
        self.xhtml = self.xhtml.replace('&#xa6;', '¦')
        self.xhtml = self.xhtml.replace('&#xa7;', '§')
        self.xhtml = self.xhtml.replace('&#xa8;', '¨')
        self.xhtml = self.xhtml.replace('&#xa9;', '©')
        self.xhtml = self.xhtml.replace('&#xaa;', 'ª')
        self.xhtml = self.xhtml.replace('&#xab;', '«')
        self.xhtml = self.xhtml.replace('&#xac;', '¬')
        self.xhtml = self.xhtml.replace('&#xae;', '®')
        self.xhtml = self.xhtml.replace('&#xaf;', '¯')
        self.xhtml = self.xhtml.replace('&#xb0;', '°')
        self.xhtml = self.xhtml.replace('&#xb1;', '±')
        self.xhtml = self.xhtml.replace('&#xb2;', '²')
        self.xhtml = self.xhtml.replace('&#xb3;', '³')
        self.xhtml = self.xhtml.replace('&#xb4;', '´')
        self.xhtml = self.xhtml.replace('&#xb5;', 'µ')
        self.xhtml = self.xhtml.replace('&#xb6;', '¶')
        self.xhtml = self.xhtml.replace('&#xb7;', '·')
        self.xhtml = self.xhtml.replace('&#xb8;', '¸')
        self.xhtml = self.xhtml.replace('&#xb9;', '¹')
        self.xhtml = self.xhtml.replace('&#xba;', 'º')
        self.xhtml = self.xhtml.replace('&#xbb;', '»')
        self.xhtml = self.xhtml.replace('&#xbc;', '¼')
        self.xhtml = self.xhtml.replace('&#xbd;', '½')
        self.xhtml = self.xhtml.replace('&#xbe;', '¾')
        self.xhtml = self.xhtml.replace('&#xbf;', '¿')
        self.xhtml = self.xhtml.replace('&#xc0;', 'À')
        self.xhtml = self.xhtml.replace('&#xc1;', 'Á')
        self.xhtml = self.xhtml.replace('&#xc2;', 'Â')
        self.xhtml = self.xhtml.replace('&#xc3;', 'Ã')
        self.xhtml = self.xhtml.replace('&#xc4;', 'Ä')
        self.xhtml = self.xhtml.replace('&#xc5;', 'Å')
        self.xhtml = self.xhtml.replace('&#xc6;', 'Æ')
        self.xhtml = self.xhtml.replace('&#xc7;', 'Ç')
        self.xhtml = self.xhtml.replace('&#xc8;', 'È')
        self.xhtml = self.xhtml.replace('&#xc9;', 'É')
        self.xhtml = self.xhtml.replace('&#xca;', 'Ê')
        self.xhtml = self.xhtml.replace('&#xcb;', 'Ë')
        self.xhtml = self.xhtml.replace('&#xcc;', 'Ì')
        self.xhtml = self.xhtml.replace('&#xcd;', 'Í')
        self.xhtml = self.xhtml.replace('&#xce;', 'Î')
        self.xhtml = self.xhtml.replace('&#xcf;', 'Ï')
        self.xhtml = self.xhtml.replace('&#xd0;', 'Ð')
        self.xhtml = self.xhtml.replace('&#xd1;', 'Ñ')
        self.xhtml = self.xhtml.replace('&#xd2;', 'Ò')
        self.xhtml = self.xhtml.replace('&#xd3;', 'Ó')
        self.xhtml = self.xhtml.replace('&#xd4;', 'Ô')
        self.xhtml = self.xhtml.replace('&#xd5;', 'Õ')
        self.xhtml = self.xhtml.replace('&#xd6;', 'Ö')
        self.xhtml = self.xhtml.replace('&#xd7;', '×')
        self.xhtml = self.xhtml.replace('&#xd8;', 'Ø')
        self.xhtml = self.xhtml.replace('&#xd9;', 'Ù')
        self.xhtml = self.xhtml.replace('&#xda;', 'Ú')
        self.xhtml = self.xhtml.replace('&#xdb;', 'Û')
        self.xhtml = self.xhtml.replace('&#xdc;', 'Ü')
        self.xhtml = self.xhtml.replace('&#xdd;', 'Ý')
        self.xhtml = self.xhtml.replace('&#xde;', 'Þ')
        self.xhtml = self.xhtml.replace('&#xdf;', 'ß')
        self.xhtml = self.xhtml.replace('&#xe0;', 'à')
        self.xhtml = self.xhtml.replace('&#xe1;', 'á')
        self.xhtml = self.xhtml.replace('&#xe2;', 'â')
        self.xhtml = self.xhtml.replace('&#xe3;', 'ã')
        self.xhtml = self.xhtml.replace('&#xe4;', 'ä')
        self.xhtml = self.xhtml.replace('&#xe5;', 'å')
        self.xhtml = self.xhtml.replace('&#xe6;', 'æ')
        self.xhtml = self.xhtml.replace('&#xe7;', 'ç')
        self.xhtml = self.xhtml.replace('&#xe8;', 'è')
        self.xhtml = self.xhtml.replace('&#xe9;', 'é')
        self.xhtml = self.xhtml.replace('&#xea;', 'ê')
        self.xhtml = self.xhtml.replace('&#xeb;', 'ë')
        self.xhtml = self.xhtml.replace('&#xec;', 'ì')
        self.xhtml = self.xhtml.replace('&#xed;', 'í')
        self.xhtml = self.xhtml.replace('&#xee;', 'î')
        self.xhtml = self.xhtml.replace('&#xef;', 'ï')
        self.xhtml = self.xhtml.replace('&#xf0;', 'ð')
        self.xhtml = self.xhtml.replace('&#xf1;', 'ñ')
        self.xhtml = self.xhtml.replace('&#xf2;', 'ò')
        self.xhtml = self.xhtml.replace('&#xf3;', 'ó')
        self.xhtml = self.xhtml.replace('&#xf4;', 'ô')
        self.xhtml = self.xhtml.replace('&#xf5;', 'õ')
        self.xhtml = self.xhtml.replace('&#xf6;', 'ö')
        self.xhtml = self.xhtml.replace('&#xf7;', '÷')
        self.xhtml = self.xhtml.replace('&#xf8;', 'ø')
        self.xhtml = self.xhtml.replace('&#xf9;', 'ù')
        self.xhtml = self.xhtml.replace('&#xfa;', 'ú')
        self.xhtml = self.xhtml.replace('&#xfb;', 'û')
        self.xhtml = self.xhtml.replace('&#xfc;', 'ü')
        self.xhtml = self.xhtml.replace('&#xfd;', 'ý')
        self.xhtml = self.xhtml.replace('&#xfe;', 'þ')
        self.xhtml = self.xhtml.replace('&#xff;', 'ÿ')
        self.xhtml = self.xhtml.replace('&#x152;', 'Œ')
        self.xhtml = self.xhtml.replace('&#x153;', 'œ')
        self.xhtml = self.xhtml.replace('&#x101;', 'ā')
        self.xhtml = self.xhtml.replace('&#x113;', 'ē')
        self.xhtml = self.xhtml.replace('&#x11b;', 'ě')
        self.xhtml = self.xhtml.replace('&#x12b;', 'ī')
        self.xhtml = self.xhtml.replace('&#x14d;', 'ō')
        self.xhtml = self.xhtml.replace('&#x16b;', 'ū')
        self.xhtml = self.xhtml.replace('&#x1ce;', 'ǎ')
        self.xhtml = self.xhtml.replace('&#x1d0;', 'ǐ')
        self.xhtml = self.xhtml.replace('&#x1d2;', 'ǒ')
        self.xhtml = self.xhtml.replace('&#x1d4;', 'ǔ')
        self.xhtml = self.xhtml.replace('&#x1d6;', 'ǖ')
        self.xhtml = self.xhtml.replace('&#x1d8;', 'ǘ')
        self.xhtml = self.xhtml.replace('&#x1da;', 'ǚ')
        self.xhtml = self.xhtml.replace('&#x1dc;', 'ǜ')
        self.xhtml = self.xhtml.replace('&#x391;', 'Α')
        self.xhtml = self.xhtml.replace('&#x392;', 'Β')
        self.xhtml = self.xhtml.replace('&#x393;', 'Γ')
        self.xhtml = self.xhtml.replace('&#x394;', 'Δ')
        self.xhtml = self.xhtml.replace('&#x395;', 'Ε')
        self.xhtml = self.xhtml.replace('&#x396;', 'Ζ')
        self.xhtml = self.xhtml.replace('&#x397;', 'Η')
        self.xhtml = self.xhtml.replace('&#x398;', 'Θ')
        self.xhtml = self.xhtml.replace('&#x399;', 'Ι')
        self.xhtml = self.xhtml.replace('&#x39a;', 'Κ')
        self.xhtml = self.xhtml.replace('&#x39b;', 'Λ')
        self.xhtml = self.xhtml.replace('&#x39c;', 'Μ')
        self.xhtml = self.xhtml.replace('&#x39d;', 'Ν')
        self.xhtml = self.xhtml.replace('&#x39e;', 'Ξ')
        self.xhtml = self.xhtml.replace('&#x39f;', 'Ο')
        self.xhtml = self.xhtml.replace('&#x3a0;', 'Π')
        self.xhtml = self.xhtml.replace('&#x3a1;', 'Ρ')
        self.xhtml = self.xhtml.replace('&#x3a3;', 'Σ')
        self.xhtml = self.xhtml.replace('&#x3a4;', 'Τ')
        self.xhtml = self.xhtml.replace('&#x3a5;', 'Υ')
        self.xhtml = self.xhtml.replace('&#x3a6;', 'Φ')
        self.xhtml = self.xhtml.replace('&#x3a7;', 'Χ')
        self.xhtml = self.xhtml.replace('&#x3a8;', 'Ψ')
        self.xhtml = self.xhtml.replace('&#x3a9;', 'Ω')
        self.xhtml = self.xhtml.replace('&#x3b1;', 'α')
        self.xhtml = self.xhtml.replace('&#x3b2;', 'β')
        self.xhtml = self.xhtml.replace('&#x3b3;', 'γ')
        self.xhtml = self.xhtml.replace('&#x3b4;', 'δ')
        self.xhtml = self.xhtml.replace('&#x3b5;', 'ε')
        self.xhtml = self.xhtml.replace('&#x3b6;', 'ζ')
        self.xhtml = self.xhtml.replace('&#x3b7;', 'η')
        self.xhtml = self.xhtml.replace('&#x3b8;', 'θ')
        self.xhtml = self.xhtml.replace('&#x3b9;', 'ι')
        self.xhtml = self.xhtml.replace('&#x3ba;', 'κ')
        self.xhtml = self.xhtml.replace('&#x3bb;', 'λ')
        self.xhtml = self.xhtml.replace('&#x3bc;', 'μ')
        self.xhtml = self.xhtml.replace('&#x3bd;', 'ν')
        self.xhtml = self.xhtml.replace('&#x3be;', 'ξ')
        self.xhtml = self.xhtml.replace('&#x3bf;', 'ο')
        self.xhtml = self.xhtml.replace('&#x3c0;', 'π')
        self.xhtml = self.xhtml.replace('&#x3c1;', 'ρ')
        self.xhtml = self.xhtml.replace('&#x3c2;', 'ς')
        self.xhtml = self.xhtml.replace('&#x3c3;', 'σ')
        self.xhtml = self.xhtml.replace('&#x3c4;', 'τ')
        self.xhtml = self.xhtml.replace('&#x3c5;', 'υ')
        self.xhtml = self.xhtml.replace('&#x3c6;', 'φ')
        self.xhtml = self.xhtml.replace('&#x3c7;', 'χ')
        self.xhtml = self.xhtml.replace('&#x3c8;', 'ψ')
        self.xhtml = self.xhtml.replace('&#x3c9;', 'ω')
        self.xhtml = self.xhtml.replace('&#x3d0;', 'ϐ')
        self.xhtml = self.xhtml.replace('&#x3d1;', 'ϑ')
        self.xhtml = self.xhtml.replace('&#x3d2;', 'ϒ')
        self.xhtml = self.xhtml.replace('&#x3d5;', 'ϕ')
        self.xhtml = self.xhtml.replace('&#x3d6;', 'ϖ')
        self.xhtml = self.xhtml.replace('&#x3d7;', 'ϗ')
        self.xhtml = self.xhtml.replace('&#x3d8;', 'Ϙ')
        self.xhtml = self.xhtml.replace('&#x3d9;', 'ϙ')
        self.xhtml = self.xhtml.replace('&#x3da;', 'Ϛ')
        self.xhtml = self.xhtml.replace('&#x3db;', 'ϛ')
        self.xhtml = self.xhtml.replace('&#x3dc;', 'Ϝ')
        self.xhtml = self.xhtml.replace('&#x3dd;', 'ϝ')
        self.xhtml = self.xhtml.replace('&#x3de;', 'Ϟ')
        self.xhtml = self.xhtml.replace('&#x3df;', 'ϟ')
        self.xhtml = self.xhtml.replace('&#x3f0;', 'ϰ')
        self.xhtml = self.xhtml.replace('&#x3f1;', 'ϱ')
        self.xhtml = self.xhtml.replace('&#x3f7;', 'Ϸ')
        self.xhtml = self.xhtml.replace('&#x3f8;', 'ϸ')
        self.xhtml = self.xhtml.replace('&#x3ba;', 'Ϻ')
        self.xhtml = self.xhtml.replace('&#x3fb;', 'ϻ')
        self.xhtml = self.xhtml.replace('&#x2032;', '′')
        self.xhtml = self.xhtml.replace('&#x2033;', '″')
        self.xhtml = self.xhtml.replace('&#x2044;', '⁄')
        self.xhtml = self.xhtml.replace('&#x2111;', 'ℑ')
        self.xhtml = self.xhtml.replace('&#x2118;', '℘')
        self.xhtml = self.xhtml.replace('&#x211c;', 'ℜ')
        self.xhtml = self.xhtml.replace('&#x2135;', 'ℵ')
        self.xhtml = self.xhtml.replace('&#x2200;', '∀')
        self.xhtml = self.xhtml.replace('&#x2202;', '∂')
        self.xhtml = self.xhtml.replace('&#x2203;', '∃')
        self.xhtml = self.xhtml.replace('&#x2205;', '∅')
        self.xhtml = self.xhtml.replace('&#x2207;', '∇')
        self.xhtml = self.xhtml.replace('&#x2208;', '∈')
        self.xhtml = self.xhtml.replace('&#x2209;', '∉')
        self.xhtml = self.xhtml.replace('&#x220b;', '∋')
        self.xhtml = self.xhtml.replace('&#x220f;', '∏')
        self.xhtml = self.xhtml.replace('&#x2211;', '∑')
        self.xhtml = self.xhtml.replace('&#x2212;', '−')
        self.xhtml = self.xhtml.replace('&#x2217;', '∗')
        self.xhtml = self.xhtml.replace('&#x221a;', '√')
        self.xhtml = self.xhtml.replace('&#x221d;', '∝')
        self.xhtml = self.xhtml.replace('&#x221e;', '∞')
        self.xhtml = self.xhtml.replace('&#x2220;', '∠')
        self.xhtml = self.xhtml.replace('&#x2227;', '∧')
        self.xhtml = self.xhtml.replace('&#x2228;', '∨')
        self.xhtml = self.xhtml.replace('&#x2229;', '∩')
        self.xhtml = self.xhtml.replace('&#x222a;', '∪')
        self.xhtml = self.xhtml.replace('&#x222b;', '∫')
        self.xhtml = self.xhtml.replace('&#x2234;', '∴')
        self.xhtml = self.xhtml.replace('&#x223c;', '∼')
        self.xhtml = self.xhtml.replace('&#x2245;', '≅')
        self.xhtml = self.xhtml.replace('&#x2248;', '≈')
        self.xhtml = self.xhtml.replace('&#x2260;', '≠')
        self.xhtml = self.xhtml.replace('&#x2261;', '≡')
        self.xhtml = self.xhtml.replace('&#x2264;', '≤')
        self.xhtml = self.xhtml.replace('&#x2265;', '≥')
        self.xhtml = self.xhtml.replace('&#x2282;', '⊂')
        self.xhtml = self.xhtml.replace('&#x2283;', '⊃')
        self.xhtml = self.xhtml.replace('&#x2284;', '⊄')
        self.xhtml = self.xhtml.replace('&#x2286;', '⊆')
        self.xhtml = self.xhtml.replace('&#x2287;', '⊇')
        self.xhtml = self.xhtml.replace('&#x2295;', '⊕')
        self.xhtml = self.xhtml.replace('&#x2297;', '⊗')
        self.xhtml = self.xhtml.replace('&#x22a5;', '⊥')
        self.xhtml = self.xhtml.replace('&#x22c5;', '⋅')
        self.xhtml = self.xhtml.replace('&#x25ca;', '◊')
        self.xhtml = self.xhtml.replace('&#x2011;', '‑')
        self.xhtml = self.xhtml.replace('&#x2013;', '–')
        self.xhtml = self.xhtml.replace('&#x2014;', '—')
        self.xhtml = self.xhtml.replace('&#x2018;', '‘')
        self.xhtml = self.xhtml.replace('&#x2019;', '’')
        self.xhtml = self.xhtml.replace('&#x201a;', '‚')
        self.xhtml = self.xhtml.replace('&#x201c;', '“')
        self.xhtml = self.xhtml.replace('&#x201d;', '”')
        self.xhtml = self.xhtml.replace('&#x201e;', '„')
        self.xhtml = self.xhtml.replace('&#x2020;', '†')
        self.xhtml = self.xhtml.replace('&#x2021;', '‡')
        self.xhtml = self.xhtml.replace('&#x2022;', '•')
        self.xhtml = self.xhtml.replace('&#x202f;', ' ')
        self.xhtml = self.xhtml.replace('&#x2030;', '‰')
        self.xhtml = self.xhtml.replace('&#x2039;', '‹')
        self.xhtml = self.xhtml.replace('&#x203a;', '›')
        self.xhtml = self.xhtml.replace('&#x20ac;', '€')
        self.xhtml = self.xhtml.replace('&#x2122;', '™')
        self.xhtml = self.xhtml.replace('&#x25cf;', '♠')
        self.xhtml = self.xhtml.replace('&#x2663;', '♣')
        self.xhtml = self.xhtml.replace('&#x2665;', '♥')
        self.xhtml = self.xhtml.replace('&#x2666;', '♦')
        self.xhtml = self.xhtml.replace('&#x2026;', '...')
        # Ligatures
        self.xhtml = self.xhtml.replace('&#xfb00; ', 'ff')
        self.xhtml = self.xhtml.replace('&#xfb01; ', 'fi')
        self.xhtml = self.xhtml.replace('&#xfb02; ', 'fl')
        self.xhtml = self.xhtml.replace('&#xfb03; ', 'ffi')
        self.xhtml = self.xhtml.replace('&#xfb04; ', 'ffl')
        self.xhtml = self.xhtml.replace('&#xfb05; ', 'ft')
        self.xhtml = self.xhtml.replace('&#xfb06; ', 'st')
        self.xhtml = self.xhtml.replace('&#xfb00;', 'ff')
        self.xhtml = self.xhtml.replace('&#xfb01;', 'fi')
        self.xhtml = self.xhtml.replace('&#xfb02;', 'fl')
        self.xhtml = self.xhtml.replace('&#xfb03;', 'ffi')
        self.xhtml = self.xhtml.replace('&#xfb04;', 'ffl')
        self.xhtml = self.xhtml.replace('&#xfb05;', 'ft')
        self.xhtml = self.xhtml.replace('&#xfb06;', 'st')
        self.executed['fix_xhtml_utf_characters'] = True
        return self.xhtml

    def _check_xhtml_data(self):
        """
        _check_xhtml_data determines if xhtml data is available.

        :return: True if the text could be extracted in XHTML format.
        :rtype: bool
        """
        self.log.debug('Entering method "_check_xhtml_data"')
        check_success = False
        if self.xhtml == '':
            self.log.warning('No text detected in xhtml format, '+
                             'attempting to extract text as xhtml')
            self.get_xhtml()
            check_success = True
            if self.xhtml == '':
                self.log.error('Could not extract any text in xhtml format '+
                               'from page %s with index %s',
                               self.pagenumber, self.index)
                check_success = False
        else:
            check_success = True
        # Instead of the last else-statement, but pretty much useless for the intended use
        # of the method to continue or abort the fix_xhtml or replace_xhtml methods.
        # else:
        #     if len(self.textblocks) == 0:
        #         self.log.warning('No text detected in plain text format, '+
        #                          'attempting to detect text blocks')
        #         self.get_block_text(False)
        #         check_success = True
        #         if self.text == '':
        #             self.log.error('Could not extract any text in from page '+
        #                            '%s with index %s',
        #                            self.pagenumber, self.index)
        #             check_success = False
        #     else:
        #         check_success = True
        self.log.info('Result of _check_xhtml_data: %s', check_success)
        return check_success

    def get_images(self):
        """
        get_images To be created
        """
        self.log.debug('Entering method "get_images"')
        images = self.page.get_images()
        print(f'Number of referenced images on page: {len(images)}')

    def get_tables(self):
        """
        get_tables is experimental and should not be used.
        """
        self.log.debug('Entering method "get_tables"')
        tables = self.page.find_tables()
        print(f'Potential tables: {len(tables.tables)}')
        if len(tables.tables) > 0:
            for table in tables.tables:
                print(f'Header: {table.header}')
                print(f'Columns: {table.col_count}')
                print(f'Rows: {table.row_count}')
                print('Content:')
                print(table.extract())
