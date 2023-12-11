"""
 pathlib to access the file system
 logging for log files
 config for program settings
"""
from pathlib import Path
import logging
from config import Config

class Outfile():
    """
    Outfile has methods for output file handling while considering the
    program settings.
    """
    def __init__(self, input_file:Path):
        self.log = logging.getLogger('file')
        self.log.debug('Startung outfiles initialization')
        self.config = Config().co
        self.basename = input_file.stem
        if self.config.fitz.export.use_pdf_output_dir:
            if self.config.fitz.export.create_sub_dirs:
                self.location = Path(input_file.absolute().parent, self.basename)
            else:
                self.location = Path(input_file.absolute().parent)
        else:
            self.location = Path(self.config.fitz.export.output_dir)

    def create_directory(self):
        """
        create_directory creates a new directory to store output files in
        """
        self.log.debug('Entering method "create_directory"')
        if not Path(self.location).exists():
            Path(self.location).mkdir(parents=True)
            self.log.info('Created output directory: %s',
                          self.location)
        else:
            self.log.warning('Output directory exists already: %s',
                          self.location)
    
    def save_text(self, text:str, ext:str):
        """
        save_text saves a string as UTF-8 encoded text file

        :param text: String to be saved to file
        :type text: str
        :param ext: File extension excluding the dot
        :type ext: str
        """
        self.log.debug('Entering method "save_text"')
        if self.config.fitz.export.use_pdf_output_dir:
            self.create_directory()
        outfile = Path(self.location, self.basename+'.'+ext)
        try:
            with open(outfile, 'w', encoding='utf-8') as fp:
                fp.write(text)
                self.log.info('File "%s" saved', outfile)
        except(OSError):
            print('Error (over)writing the file', outfile)
            self.log.error('Could not write file "%s"', outfile)

    def save_image(self):
        pass
