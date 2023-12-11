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
    mainlog.info('End extraction session')
    # Cleanup log


if __name__ == '__main__':
    main()
