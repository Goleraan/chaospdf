"""
 GNU GPL V3
 (c) 2023 Akram Radwan
 
 pathlib for adding and removing PDF files
 config for program configuration
 pdffiles for adding and removing PDF files
"""
from pathlib import Path
from config import Config
from pdffiles import PDFFiles

class TUI:
    """
     Text user interface that implements a menu structure for
     program configuration and running.
    """
    def __init__(self, cfg:Config):
        self.cfg = cfg

    def tui(self):
        """
        tui asks the questions for the interactive mode.

        :return: True if it should continue with the PDF extraction
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\n' +
                           '(1) Run PDF extraction\n' +
                           '(2) Input settings\n' +
                           '(3) Output settings\n' +
                           '(4) Text extraction settings\n' +
                           '(5) Image extraction settings\n' +
                           '(s) Settings files\n' +
                           '(0) Exit\n' +
                           '(c) Copyright and license information\n')
            match answer.lower():
                case '0':
                    return False
                case 'q':
                    return False
                case '1':
                    return True
                case '2':
                    if not self.tui_input():
                        return False
                    answer = ''
                case '3':
                    if not self.tui_output():
                        return False
                    answer = ''
                case '4':
                    if not self.tui_text():
                        return False
                    answer = ''
                case '5':
                    if not self.tui_image():
                        return False
                    answer = ''
                case 's':
                    self.tui_settings_files()
                case 'c':
                    self.print_license()
                case _:
                    answer = ''

    def tui_input(self):
        """
        tui_input shows the menu for input settings.

        :return: False to terminate the program
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\n' +
                           '(1) Add input directory, finds all PDF files in directory\n' +
                           '(2) Add PDF file\n' +
                           '(3) Remove PDF file\n' +
                           '(0) Return to main menu\n' +
                           '(q) Exit program\n')
            match answer:
                case '0':
                    return True
                case '1':
                    if not self.tui_input_directory():
                        return False
                    answer = ''
                case '2':
                    if not self.tui_add_pdf_file():
                        return False
                    answer = ''
                case '3':
                    if not self.tui_remove_pdf_file():
                        return False
                    answer = ''
                case 'q':
                    return False
                case _:
                    answer = ''

    def tui_output(self):
        """
        tui_output shows the menu for output settings.

        :return: False to terminate the program
        :rtype: bool
        """
        if self.cfg.cfg.fitz.export.create_sub_dirs:
            sub_dirs = 'Do not create sub directories for each PDF'
        else:
            sub_dirs = 'Create sub directories for each PDF'
        answer = ''
        while 1:
            answer = input('\n' +
                           '(1) Set output directory\n' +
                           '(2) ' + sub_dirs + '\n'
                           '(3) Reset output directory to PDF directory\n' +
                           '(0) Return to main menu\n' +
                           '(q) Exit program\n')
            match answer:
                case '0':
                    return True
                case '1':
                    self.cfg.cfg.fitz.export.use_pdf_output_dir = False
                    if not self.tui_output_directory():
                        return False
                    answer = ''
                case '2':
                    if self.cfg.cfg.fitz.export.create_sub_dirs:
                        sub_dirs = 'Create sub directories for each PDF'
                        print('Disabled creation of sub-directories')
                        self.cfg.cfg.fitz.export.create_sub_dirs = False
                    else:
                        sub_dirs = 'Do not create sub directories for each PDF'
                        print('Enabled creation of sub-directories')
                        self.cfg.cfg.fitz.export.create_sub_dirs = True
                    answer = ''
                case '3':
                    self.cfg.cfg.fitz.export.use_pdf_output_dir = True
                    print('Use location of PDF file(s) for output')
                    answer = ''
                case 'q':
                    return False
                case _:
                    answer = ''

    def tui_text(self):
        """
        tui_output shows the menu for text extraction settings.

        :return: False to terminate the program
        :rtype: bool
        """
        answer = ''
        if self.cfg.cfg.fitz.export.write_html:
            write_html = 'Do not write file with HTML code'
        else:
            write_html = 'Write file with HTML code'
        if self.cfg.cfg.fitz.export.write_text:
            write_text = 'Do not write file with plain text'
        else:
            write_text = 'Write file with plain text'
        if self.cfg.cfg.fitz.export.write_toc:
            write_toc = 'Do not write a separate file with the ' +\
                        'table of contents'
        else:
            write_toc = 'Write a separate file with the table of contents'
        if self.cfg.cfg.fitz.text.detect_page_offset:
            detect_offset = 'Do not try to detect the page number ' +\
                            'offset automatically'
        else:
            detect_offset = 'Try to detect the page number offset automatically'
        if self.cfg.cfg.fitz.text.remove_page_numbers:
            remove_page_numbers = 'Do not attempt to remove the page ' +\
                                  'numbers from the text'
        else:
            remove_page_numbers = 'Attempt to remove the page numbers ' +\
                                  'from HTML'
        while 1:
            answer = input('\n' +
                           '(1) ' + write_html + '\n' +
                           '(2) ' + write_text + '\n' +
                           '(3) ' + write_toc + '\n' +
                           '(4) ' + detect_offset + '\n' +
                           '(5) Set the page offset manually\n' +
                           '(6) ' + remove_page_numbers + '\n' +
                           '(7) Removal of repeating text' +
                           '(0) Return to main menu\n' +
                           '(q) Exit program\n')
            match answer:
                case '0':
                    return True
                case '1':
                    if self.cfg.cfg.fitz.export_write_html:
                        write_html = 'Write file with HTML code'
                        print('Disabled writing of HTML file(s)')
                        self.cfg.cfg.fitz.export.write_html = False
                    else:
                        write_html = 'Do not write file with HTML code'
                        print('Enabled writing of HTML file(s)')
                        self.cfg.cfg.fitz.export.write_html = True
                    answer = ''
                case '2':
                    if self.cfg.cfg.fitz.export.write_text:
                        write_text = 'Write file with plain text'
                        print('Disabled writing of plain text file(s)')
                        self.cfg.cfg.fitz.export.write_text = False
                    else:
                        write_text = 'Do not write file with plain text'
                        print('Enabled writing of plain text file(s)')
                        self.cfg.cfg.fitz.export.write_text = True
                    print('Enabled writing of plain text file(s)')
                    answer = ''
                case '3':
                    if self.cfg.cfg.fitz.export.write_toc:
                        write_toc = 'Write a separate file with the ' +\
                                    'table of contents'
                        print('Disabled writing of TOC file(s)')
                        self.cfg.cfg.fitz.export.write_toc = False
                    else:
                        write_toc = 'Do not write a separate file with ' +\
                                    'the table of contents'
                        print('Enabled writing of TOC file(s)')
                        self.cfg.cfg.fitz.export.write_toc = True
                    answer = ''
                case '4':
                    if self.cfg.cfg.fitz.text.detect_page_offset:
                        detect_offset = 'Try to detect the page number ' +\
                                        'offset automatically'
                        print('Disabled detection of page number offset')
                        self.cfg.cfg.fitz.text.detect_page_offset = False
                    else:
                        detect_offset = 'Do not try to detect the page ' +\
                                        'number offset automatically'
                        print('Enabled detection of page number offset')
                        self.cfg.cfg.fitz.text.detect_page_offset = True
                    print('Enabled detection of page number offset')
                    answer = ''
                case '5':
                    self.cfg.cfg.fitz.text.detect_page_offset = False
                    print('Disabled detection of page number offset')
                    if not self.tui_page_offset():
                        return False
                    answer = ''
                case '6':
                    if self.cfg.cfg.fitz.text.remove_page_numbers:
                        remove_page_numbers = 'Attempt to remove the page ' +\
                                              'numbers from HTML'
                        print('Disabled removal of page numbers from extracted HTML')
                        self.cfg.cfg.fitz.text.remove_page_numbers = False
                    else:
                        remove_page_numbers = 'Do not attempt to remove the ' +\
                                              'page numbers from HTML'
                        print('Enabled removal of page numbers from extracted HTML')
                        self.cfg.cfg.fitz.text.remove_page_numbers = True
                    answer = ''
                case '7':
                    if not self.tui_repeating_text():
                        return False
                    answer = ''
                case 'q':
                    return False
                case _:
                    answer = ''

    def tui_image(self):
        """
        tui_output shows the menu for image extraction settings.

        :return: False to terminate the program
        :rtype: bool
        """
        if self.cfg.cfg.fitz.images.write_doc_images:
            doc_extract = 'Do not extract images from whole document'
        else:
            doc_extract = 'Extract images from whole document'
        if self.cfg.cfg.fitz.images.write_page_images:
            page_extract = 'Do not extract images from each page'
        else:
            page_extract = 'Extract images from each page'
        answer = ''
        while 1:
            answer = input('\n' +
                           '(1) ' + doc_extract + '\n' +
                           '(2) ' + page_extract + '\n' +
                           '(3) Set the minimum image size\n' +
                           '(4) Set the minimum x dimension\n' +
                           '(5) Set the minimum y dimension\n' +
                           '(6) Set the minimum compression limit\n' +
                           '(0) Return to main menu\n' +
                           '(q) Exit program\n')
            match answer:
                case '0':
                    return True
                case '1':
                    if self.cfg.cfg.fitz.images.write_doc_images:
                        doc_extract = 'Extract images from whole document'
                        print('Disabled extraction of all images of the document')
                        self.cfg.cfg.fitz.images.write_doc_images = False
                    else:
                        doc_extract = 'Do not extract images from whole document'
                        print('Enabled extraction of all images of the document')
                        self.cfg.cfg.fitz.images.write_doc_images = True
                    print('Enabled extraction of all images of the document')
                    answer = ''
                case '2':
                    if self.cfg.cfg.fitz.images.write_page_images:
                        page_extract = 'Extract images from each page'
                        print(
                            'Disabled extraction of images from each page of the document')
                        self.cfg.cfg.fitz.images.write_page_images = False
                    else:
                        page_extract = 'Do not extract images from each page'
                        print(
                            'Enabled extraction of images from each page of the document')
                        self.cfg.cfg.fitz.images.write_page_images = True
                    answer = ''
                    print('\n\n*** This setting has no effect! ***\n\n')
                case '3':
                    if not self.tui_min_img_size():
                        return False
                    answer = ''
                case '4':
                    if not self.tui_min_x_dim():
                        return False
                    answer = ''
                case '5':
                    if not self.tui_min_y_dim():
                        return False
                    answer = ''
                case '6':
                    if not self.tui_min_compression_limit():
                        return False
                    answer = ''
                case 'q':
                    return False
                case _:
                    answer = ''

    def tui_input_directory(self):
        """
        tui_input_directory shows a menu to add all PDF files of a directory
        and its subdirectories to the list of files

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        files = PDFFiles(self.cfg)
        answer = ''
        while 1:
            answer = input('\nSpecify the path to a directory with ' +
                           'PDF files. It can be absolute or relative to ' +
                           'the current working directory.\n' +
                           'Subdirectories will be processed, too.\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            wd = Path(answer).absolute()
            if not wd.exists():
                print(f'Cannot find directory:\n{wd}')
                continue
            files.set_working_directory(wd)
            files.search_files()
            print('\nFiles for processing:')
            files.list_files()
            self.cfg.cfg.input.input_dir = str(wd)
            # self.cfg.cfg.input.input_files = files.filelist
            return True

    def tui_add_pdf_file(self):
        """
        tui_add_pdf_file shows a menu to add a single PDF file to the list.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        files = PDFFiles(self.cfg)
        answer = ''
        while 1:
            answer = input('\nSpecify the path to a PDF file. It can be ' +
                           'an absolute or relative path to the current ' +
                           'working directory.\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            file = Path(answer).absolute()
            if not file.exists():
                print(f'Cannot find file:\n{file}')
                continue
            files.add_file(Path(answer))
            self.cfg.cfg.input.input_files = files.filelist
            print('\nFiles for processing:')
            files.list_files()
            return True

    def tui_remove_pdf_file(self):
        """
        tui_remove_pdf_file shows a menu to remove a single PDF file from the list.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        files = PDFFiles(self.cfg)
        while 1:
            print('\nFiles marked for processing:')
            files.list_files()
            answer = input('\nSpecify the full path for the file that should ' +
                           'be removed from the list.\n' +
                           'Pay attention to capital letters!\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            if Path(answer).absolute() in files.filelist:
                files.remove_file(Path(answer))
            else:
                print(f'Cannot find specified file in list: {answer}')

    def tui_output_directory(self):
        """
        tui_output_directory shows a menu to specify a directory to save output files.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the path to a directory for saving ' +
                           'the output files. It can be an absolute or ' +
                           'relative path.\n' +
                           'Just type q to return to the previous menu.\n')
            print('\n\nWARNING! This setting has no effect!!\n\n')
            if answer.lower() == 'q':
                return True
            wd = Path(answer).absolute()
            if not wd.exists():
                print(f'Cannot find directory:\n{wd}')
                continue
            self.cfg.cfg.fitz.export.output_dir = str(wd)
            print(f'\nDirectory for output: {wd}')
            return True

    def tui_page_offset(self):
        """
        tui_page_offset shows a menu to specify a manual page offset.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the offset for PDF and book page ' +
                           'numbers. The first page is "0". If the pdf ' +
                           'page 5 shows the number 6, the offset is 2.\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            try:
                answer = int(answer)
            except ValueError as e:
                print('Enter an integer number!')
                print(e)
                continue
            self.cfg.cfg.fitz.text.page_offset = answer
            print(f'\nNew offset: {self.cfg.cfg.fitz.text.page_offset}')
            return True

    def tui_repeating_text(self):
        """
        tui_repeating_text not implemented!
        Should be a new menu to define:
        Attempt removing repeating headlines
        Attempt removing document title
        Attempt removing watermark
        Detect repeating text (with warning)

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        print('Method not implemented')
        return True

    def tui_min_img_size(self):
        """
        tui_min_img_size shows a menu to specify the minimum image size for
        extraction.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the minimum file size for embedded ' +
                           'images in Byte as integer number.\n' +
                           'Default value: 5000\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            try:
                answer = int(answer)
            except ValueError as e:
                print('Enter an integer number!')
                print(e)
                continue
            self.cfg.cfg.fitz.images.image_size_min = answer
            print(f'\nNew offset: {self.cfg.cfg.fitz.images.image_size_min}')
            return True

    def tui_min_x_dim(self):
        """
        tui_min_x_dim shows a menu to specify the minimum image dimension
        in X.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the minimum image dimension in X ' +
                           'in Pixel.\n' +
                           'Default value: 130\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            try:
                answer = int(answer)
            except ValueError as e:
                print('Enter an integer number!')
                print(e)
                continue
            self.cfg.cfg.fitz.images.image_dimension_x_min = answer
            print(f'\nNew offset: {self.cfg.cfg.fitz.images.image_dimension_x_min}')
            return True

    def tui_min_y_dim(self):
        """
        tui_min_y_dim shows a menu to specify the minimum image dimension
        in Y.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the minimum image dimension in Y ' +
                           'in Pixel.\n' +
                           'Default value: 130\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            try:
                answer = int(answer)
            except ValueError as e:
                print('Enter an integer number!')
                print(e)
                continue
            self.cfg.cfg.fitz.images.image_dimension_y_min = answer
            print(f'\nNew offset: {self.cfg.cfg.fitz.images.image_dimension_y_min}')
            return True

    def tui_min_compression_limit(self):
        """
        tui_min_compression_limit shows a menu to specify the minimum image
        compression limit.

        :return: True to return to the previous menu without aborting
        :rtype: bool
        """
        answer = ''
        while 1:
            answer = input('\nSpecify the minimum compression limit of ' +
                           'images. It is not recommended to change it!\n' +
                           'Default value: 0.05\n' +
                           'Just type q to return to the previous menu.\n')
            if answer.lower() == 'q':
                return True
            try:
                answer = int(answer)
            except ValueError as e:
                print('Enter an integer number!')
                print(e)
                continue
            self.cfg.cfg.fitz.images.image_compression_limit = answer
            print('\nNew offset:', self.cfg.cfg.fitz.images.image_compression_limit)
            return True

    def print_license(self):
        """
        print_license prints rudimentary license information
        """
        print()
        print('ChaosPDF - Text and image extraction from PDF files')
        print('Copyright (c) 2023  Akram Radwan')
        print()
        print('This program is free software: you can redistribute ' +
              'it and/or modify it under the terms of the GNU General ' +
              'Public License version 3 as published by the Free ' +
              'Software Foundation.')
        print()
        print('This program is distributed in the hope that it will ' +
              'be useful, but WITHOUT ANY WARRANTY; without even the ' +
              'implied warranty of MERCHANTABILITY or FITNESS FOR A ' +
              'PARTICULAR PURPOSE.  See the GNU General Public License ' +
              'for more details.')
        print()
        print('You should have received a copy of the GNU General Public ' +
              'License along with this program.')
        print('If not, see <https://www.gnu.org/licenses/>.')
        print()
        print('You can obtain the source code of the program from ' +
              '<https://github.com/Goleraan/chaospdf>')

    def tui_settings_files(self):
        """
        tui_settings_files shows the menu to interact with settings files.
        """
        answer = ''
        while 1:
            cfg_file = Path(self.cfg.cfg.config.config_dir,
                            self.cfg.cfg.config.config_file)
            if cfg_file.exists():
                cfg_exists = 'which does not exist.'
            else:
                cfg_exists = 'which can be found.'
            answer = input('\n' +
                           f'Current settings file: {cfg_file} {cfg_exists}\n'
                           '(1) Set settings file\n' +
                           '(2) Read settings file\n' +
                           '(3) Write settings file\n' +
                           '(0) Return to main menu\n')
            match answer.lower():
                case '0':
                    return
                case 'q':
                    return
                case '1':
                    self.tui_set_settings_file()
                case '2':
                    if cfg_file.exists():
                        print(f'Reading {str(cfg_file)}')
                        self.cfg.read_config()
                    else:
                        print(f'Cannot find {str(cfg_file)}')
                case '3':
                    cfg_file = Path(self.cfg.cfg.config.config_dir,
                                    self.cfg.cfg.config.config_file)
                    if cfg_file.exists():
                        overwrite = input(f'{str(cfg_file)} exists already!\n' +
                                           'Overwrite? (y/n)\n')
                        if overwrite.lower() == 'y':
                            self.cfg.write_config()
                            print(f'Wrote settings to {str(cfg_file)}\n')
                    elif Path(self.cfg.cfg.config.config_dir).exists():
                        self.cfg.write_config()
                        print(f'Wrote settings to {str(cfg_file)}\n')
                    else:
                        print(f'Cannot find path {self.cfg.cfg.config.config_dir}\n')
                case _:
                    answer = ''

    def tui_set_settings_file(self):
        """
        tui_set_settings_file sets the location of the settings file
        """
        print('Please provide the absolute or relative path to the settings file.\n'+
              'Examples:\n' +
              'D:/chaos/chaospdf.json\n'
              '..\\chaospdf.json\n')
        answer = input('Please provide the absolute or relative path to the settings file.\n' +
                        'Examples:\n' +
                        'D:/chaos/chaospdf.json\n'
                        '..\\chaospdf.json\n')
        config_dir = Path(answer).parent
        config_file = Path(answer).name
        self.cfg.cfg.config.config_dir = str(config_dir)
        self.cfg.cfg.config.config_file = config_file
        if Path(answer).suffix != '.json':
            print('Adding json file extension to name.')
            config_file = Path(config_file + '.json')
            self.cfg.cfg.config.config_file = config_file
        if not config_dir.exists():
            print(f'Warning, cannot find path {config_dir}\n')
        if Path(answer).exists():
            print(f'Found a configuration file {Path(answer)}\n')
