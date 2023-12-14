# Main file to start the program
"""
 GNU GPL V3
 (c) 2023 Akram Radwan
 Contains code for image recovery with PyMuPDF by (c) 2018 Jorj X. McKie
 
 argparse for parsing the command line arguments
 pathlib for accessing files
 logging for handling the log file
 logger for log file configuration
 pdffiles for handling PDF files and file locations
 fitzdoc for handling PDF documents with PyMuPDF
 outfile for output file handling
 config for a general program configuration
 tui for the text menu
"""
import argparse
from pathlib import Path
import logging
import logging.config
from logger import Logger
from pdffiles import PDFFiles
from fitzdoc import Fitzdoc
from outfile import Outfile
from config import Config
from tui import TUI


def main(**args):
    print('ChaosPDF extraction tool version 0.1.2')
    print('Copyright (c) 2023  Akram Radwan')
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
    parser = argparse.ArgumentParser(
        description='Processes PDF files to extract text and images'
        )
    main()
