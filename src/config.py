"""
 GNU GPL V3
 (c) 2023 Akram Radwan
 
 pathlib for file access
 json for formatting
 pdffiles for adding and removing PDF files
"""
from pathlib import Path
import json

class Settings:
    """
     Helper class to turn a dictionary into an object hierarchy
    """

    def __init__(self, settings: dict):
        self.__dict__.update(settings)


class Config():
    """
    Config handles the management of the settings.
    NOT FULLY IMPLEMENTED!
    Not all settings have an effect in other classes!
    """
    config = {}
    cfg = object()

    def __init__(self):
        if not self.config:
            self.default_config()
            self.cfg = json.loads(json.dumps(self.config), object_hook=Settings)
        self.config_file = Path(self.config['config']['config_dir'],
                                self.config['config']['config_file'])

    def default_config(self):
        """
        default_config sets the default settings.
        """
        self.config = {'fitz': {'export': {'write_html': True,
                                           'write_text': True,
                                           'write_toc': True,
                                           'write_all_images': True,
                                           'write_page_images': False,
                                           'create_sub_dirs': True,
                                           'use_pdf_output_dir': True,
                                           'output_dir': str(Path('.').absolute())},
                                'images': {'write_doc_images': True,
                                           'write_page_images': False,
                                           'image_size_min': 5000,
                                           'image_dimension_x_min': 130,
                                           'image_dimension_y_min': 130,
                                           'compression_limit': 0.05},
                                'text': {'remove_page_numbers': True,
                                         'remove_repeating_text': False,
                                         'detect_page_offset': True,
                                         'page_offset': 0,
                                         'page_separator': True}
                                },
                       'input': {'input_dir': str(Path('.').absolute()),
                                 'input_files': []},
                       'config': {'config_dir': str(Path('.').absolute()),
                                  'config_file': 'chaospdf.json'}
                       }

    def read_config(self):
        """
        read_config reads the configuration file.
        """
        with open(self.config_file, 'r', encoding='utf-8') as fp:
            self.config = json.load(fp)
            self.cfg = json.loads(json.dumps(self.config), object_hook=Settings)

    def write_config(self):
        """
        write_config writes the configuration file.
        """
        with open(self.config_file, 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(self.config, sort_keys=True, indent=4))

    def print_config(self):
        """
        print_config prints the configuration to the console.
        Does not work.
        """
        print(json.dumps(self.cfg.__dict__))

    def evaluate_args(self):
        """
        evaluate_args evaluate arguments from main function
        """
        print("Method not implemented")
