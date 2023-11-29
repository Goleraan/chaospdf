from pathlib import Path
import logging

class Outfile():
    def __init__(self, input_file:Path):
        self.log = logging.getLogger('file')
        self.log.debug('Startung outfiles initialization')
        self.basename = input_file.stem
        self.location = Path(input_file.absolute().parent, self.basename)

    def create_directory(self):
        self.log.debug('Entering method "create_directory"')
        if not Path(self.location).exists():
            Path(self.location).mkdir(parents=True)
            self.log.info('Created output directory: %s',
                          self.location)
        else:
            self.log.warning('Output directory exists already: %s',
                          self.location)
    
    def save_text(self, text:str, ext:str):
        self.log.debug('Entering method "save_text"')
        self.create_directory()
        outfile = Path(self.location, self.basename+ext)
        try:
            with open(outfile, 'w', encoding='utf-8') as fp:
                fp.write(text)
                self.log.info('File "%s" saved', outfile)
        except(OSError):
            print('Error (over)writing the file', outfile)
            self.log.error('Could not write file "%s"', outfile)

    def save_image(self):
        pass
