# Main file to start the program
"""Modules tbd"""
import logging
import logging.config
from logger import Logger
from pdffiles import PDFFiles
from pathlib import Path
from fitzdoc import Fitzdoc
from fitzpage import Fitzpage

def main(**args):
    # Initialize logging
    log=Logger()  # Initialization is necessary, might not be needed to assign to variable, though
    mainlog = logging.getLogger('main')
    mainlog.info('Start extraction session')
    files = PDFFiles()
    files.set_working_directory(Path('..'))
    files.search_files()
    files.list_files()
    for file in files.filelist:
        doc = Fitzdoc(file)
        # doc.print_file_info()
        page = Fitzpage(doc.doc[36], 36)
        #
        #page.get_plain_text(False)
        #print(page.text)
        #
        #page.get_block_text(False)
        # page.fix_text_ligature_spaces()
        # page.fix_text_line_breaks()
        # page.remove_text_page_number()
        # page.remove_text_repeating('DAS VERLASSENE BERGDORF')
        # page.remove_text_repeating('Die Träumer von Kaliyama')
        # print(page.text)
        #
        # page.get_xhtml()
        # page.fix_xhtml_utf_characters()
        # page.remove_xhtml_repeating('Die Träumer von Kaliyama')
        # page.remove_xhtml_repeating('DAS VERLASSENE BERGDORF')
        # page.remove_xhtml_page_number()
        # page.fix_xhtml_line_breaks()
        # print(page.xhtml)
        #
        # page.get_dict_text()
        # print(page.dicttext)
        #
        # page.get_images()
    mainlog.info('End extraction session')
    # Cleanup log

if __name__ == '__main__':
    main()
