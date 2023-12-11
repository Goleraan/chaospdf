"""
 GNU GPL V3
 (c) 2023 Akram Radwan
 
 pathlib to find and access PDF files
 logging for logging
 config for program configuration
"""
from pathlib import Path
import logging
from config import Config

class PDFFiles():
    """
    PDFFiles provides methods to handle file paths and lists.
    """
    filelist = []
    check_success = False

    def __init__(self, cfg:Config):
        self.log = logging.getLogger('file')  # Log to console and file
        self.logf = logging.getLogger('filef')  # Log to file only
        self.log.info('Initializing file handling')
        self.working_directory = Path('.')
        self.cfg = cfg

    def check_files(self):
        """
        check_files Check if all files stored in the list self.filelist can be found

        :return: Success flag, False when there is at least one access error
        :rtype: Bool
        """
        self.log.debug('Entering method "check_files"')
        check_success = True
        if len(self.filelist) > 0:
            for item in self.filelist:
                if not item.exists():
                    check_success = False
                    self.log.warning('File %s not found', item)
                else:
                    self.logf.info('File %s exists', item)
        else:
            check_success = False
            self.log.error('No files defined for processing')
        return check_success

    def search_files(self):
        """
        search_files Search for PDF files in the working directory

        :return: True if PDF files were found
        :rtype: Bool
        """
        self.log.debug('Entering method "search_files"')
        search_success = False
        filelist = list(self.working_directory.glob('**/*.pdf'))
        if len(filelist) > 0:
            search_success = True
            for file in filelist:
                self.add_file(file)
        else:
            search_success = False
        return search_success

    def add_file(self, file:Path):
        """
        add_file Adds a specified file with its absolute path to the list of files for processing

        :param file: PDF file to add to the list
        :type file: Path
        :return: Returns True if the file could be added to the list or if it is in there already
        :rtype: Bool
        """
        self.log.debug('Entering method "add_file"')
        add_success = False  # Indicator if the file can be added to the list
        if file.exists():
            if file.absolute() in self.filelist:
                self.log.warning('File "%s" is in the list already', file)
            else:
                self.filelist.append(file.absolute())
                self.cfg.cfg.input.input_files.append(str(file.absolute()))
                self.log.info('Added file "%s" to filelist', file)
            add_success = True
        else:
            self.log.error('Cannot find file "%s"', file)
            add_success = False
        return add_success

    def remove_file(self, file:Path):
        """
        remove_file Removes a file from the list of files to process

        :param file: Path to a PDF file that is in the list already
        :type file: Path
        :return: True if the file could be removed or does not exist in the list anyway
        :rtype: Bool
        """
        self.log.debug('Entering method "remove_file"')
        remove_success = False
        if file.absolute() in self.filelist:
            self.filelist.remove(file.absolute())
            print(f'Trying to remove {file.absolute()}')
            if str(file.absolute()) in self.cfg.cfg.input.input_files:
                self.cfg.cfg.input.input_files.remove(str(file.absolute()))
            else:
                print('Something went wrong!!!')
                print('Files in pdffiles:')
                self.list_files()
                print('\nFiles in config:')
                for item in self.cfg.cfg.input.input_files:
                    print(item)
            remove_success = True
            self.log.info('Removed File "%s" from the list', file)
        else:
            if file in self.filelist:
                self.log.error('File "%s" exists in the list but at a ' +
                               'different location, did not remove file',
                               file)
                remove_success = False
            else:
                self.log.warning('File "%s" does not exist in the list', file)
                remove_success = True
        return remove_success

    def list_files(self):
        """
        list_files Prints the list of registered PDF files
        """
        self.log.debug('Entering method "list_files"')
        for item in self.filelist:
            if item.exists():
                print(item)
            else:
                print(f'{item} <<< NOT FOUND >>>')
                self.logf.warning('File %s not found', item)

    def set_working_directory(self, directory:Path):
        """
        set_working_directory Set the working directory to an absolute path

        :param directory: New working directory
        :type directory: Path
        """
        self.log.debug('Entering method "set_working_directory"')
        self.working_directory = directory.absolute()
        self.log.info('Update working directory to: "%s"', self.working_directory)
