# Main file to start the program
"""Modules tbd"""
import logging
import logging.config
from logger import Logger
from pdffiles import PDFFiles
from pathlib import Path
from fitzdoc import Fitzdoc
from fitzpage import Fitzpage
from outfile import Outfile
from config import Config
from tui import TUI


def main(**args):
    print('ChaosPDF extraction tool version 0.1.1')
    # Initialize logging
    log = Logger()  # Initialization is necessary, might not be needed to assign to variable, though
    mainlog = logging.getLogger('main')
    mainlog.info('Start extraction session')
    cfg = Config()
    files = PDFFiles(cfg)
    files.set_working_directory(Path('.'))
    files.search_files()
    # files.list_files()
    # print(cfg.cfg.fitz.export.output_dir)
    # print(cfg.cfg.fitz.__dict__)
    if not TUI(cfg).tui():
        print('\nNo files processed\n')
        return
    print('If you see error messages, check the log file for more context')
    # config.print_config()
    for file in files.filelist:
        doc = Fitzdoc(file, cfg)
        out = Outfile(file, cfg)
        # Page offset
        if cfg.cfg.fitz.text.detect_page_offset:
            offset = doc.detect_page_offset()
        else:
            offset = cfg.cfg.fitz.text.page_offset
        # Extract HTML and text
        if cfg.cfg.fitz.text.page_separator:
            doc.process_pages_separately(offset)
        else:
            doc.process_pages(offset)
        # Write HTML and text files
        if cfg.cfg.fitz.export.write_html:
            out.save_text(doc.html, 'html')
        if cfg.cfg.fitz.export.write_text:
            out.save_text(doc.text, 'txt')
        if cfg.cfg.fitz.export.write_toc:
            out.save_text(doc.process_toc(offset), 'toc.txt')
        # Write images
        if cfg.cfg.fitz.images.write_doc_images:
            doc.extract_images()
        # return
        #
        # doc.print_file_info()
        # page = Fitzpage(doc.doc[45], 45)
        #
        # page.get_block_text(False)
        # page.fix_text_ligature_spaces()
        # page.fix_text_line_breaks()
        # page.remove_text_page_number()
        # page.remove_text_repeating('DAS VERLASSENE BERGDORF')
        # page.remove_text_repeating('Die Träumer von Kaliyama')
        # print(page.text)
        #
        # page.get_xhtml()
        # page.fix_xhtml_utf_characters()
        # page.fix_xhtml_line_breaks()
        # page.remove_xhtml_repeating('Die Träumer von Kaliyama')
        # page.remove_xhtml_repeating('DAS VERLASSENE BERGDORF')
        # page.remove_xhtml_page_number()
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
