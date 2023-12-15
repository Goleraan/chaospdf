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


def main(args):
    print('ChaosPDF extraction tool version 0.2.0')
    print('Copyright (c) 2023  Akram Radwan')
    # Initialize logging
    cfg = Config()
    cfg.evaluate_args(args)
    log = Logger(cfg)  # Initialization is necessary, might not be needed to assign to variable, though
    mainlog = logging.getLogger('main')
    mainlog.info('Start extraction session')
    files = PDFFiles(cfg)
    for folder in cfg.cfg.input.input_dirs:
        if Path(folder).exists():
            files.set_working_directory(Path(folder))
            files.search_files()
        else:
            mainlog.error('Cannot find directory %s', folder)
    if cfg.cfg.config.interactive:
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
        description='Processes PDF files to extract text and images',
        prefix_chars='-/'
        )
    parser.add_argument('-v', '--verbosity',
                        default=1,
                        type=int,
                        choices=range(0,5),
                        help='Verbosity: 0 only critical errors\n' +
                             '           1 all normal errors (default)\n' +
                             '           2 all warnings\n' +
                             '           3 all information\n' +
                             '           4 debugging')
    parser.add_argument('-m', '--menu',
                        action='store_true',
                        help='Opens a text menu for detailed settings.')
    parser.add_argument('-c', '--config',
                        default='chaospdf.json',
                        help='Use specific configuration file.')
    parser.add_argument('-p', '--pdffolder',
                        action='extend',
                        nargs='+',
                        type=str,
                        default=['.'],
                        help='List of directories to search for PDF files.\n' +
                        'The list always contains the current working directory!')
    parser.add_argument('-ni', '--noimages',
                        action='store_false',
                        help='Do not extract images.')
    parser.add_argument('-nt', '--notext',
                        action='store_false',
                        help='Do not extract plain text.')
    parser.add_argument('-nh', '--nohtml',
                        action='store_false',
                        help='Do not extract HTML text.')
    parser.add_argument('-nc', '--notoc',
                        action='store_false',
                        help='Do not extract the table of contents.')
    args = parser.parse_args()
    # args = parser.parse_args(['-p', '..'])  # Development only!
    main(args)
