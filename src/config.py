"""
 GNU GPL V3
 (c) 2023 Akram Radwan
 
 pathlib for file access
 json for formatting
 pdffiles for adding and removing PDF files
 argparse for handling the argparse objects
"""
from pathlib import Path
import json
# import argparse  # ? Is this needed for evaluate_args?

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
            if Path('chaospdf.json').exists():
                self.read_config()
            self.default_config()
            self.cfg = json.loads(json.dumps(self.config), object_hook=Settings)

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
                                 'input_files': [],
                                 'input_dirs': ['.']},
                       'config': {'config_dir': str(Path('.').absolute()),
                                  'config_file': 'chaospdf.json',
                                  'interactive': True,
                                  'logging_level': 3}
                       }

    def __to_dict(self, settings_obj:Settings):
        """
        toDict turns a settings object back to a dictionary that it
        can be dumped into a json file

        :param settings_obj: Settings object
        :type settings_obj: Settings
        :raises TypeError: when the object cannot be converted to a
        dictionary
        :return: dictionary with all settings in the same hierarchy
        that is defined in the default settings dict
        :rtype: dict
        """
        settings_dict = vars(settings_obj)
        output_dict = {}
        if not isinstance(settings_dict, dict):
            raise TypeError(f'Dict expected but got {type(settings_dict)}')
        for key in settings_dict.keys():
            print(key, settings_dict[key])
            if isinstance(settings_dict[key], Settings):
                output_dict = output_dict | {key: self.__to_dict(settings_dict[key])}
            else:
                output_dict = output_dict | {key: settings_dict[key]}
        return output_dict

    def config_to_dict(self):
        """
        config_to_dict returns the configuration object into the configuration
        dictionary property
        """
        self.config = self.__to_dict(self.cfg)

    def read_config(self):
        """
        read_config reads the configuration file.
        """
        cfg_file = Path(self.cfg.config.config_dir,
                        self.cfg.config.config_file)
        with open(cfg_file, 'r', encoding='utf-8') as fp:
            self.config = json.load(fp)
            self.cfg = json.loads(json.dumps(self.config),
                                  object_hook=Settings)

    def write_config(self):
        """
        write_config writes the configuration file.
        """
        cfg_file = Path(self.cfg.config.config_dir,
                        self.cfg.config.config_file)
        self.config_to_dict()
        with open(cfg_file, 'w', encoding='utf-8') as fp:
            fp.write(json.dumps(self.config, sort_keys=True, indent=4))

    def print_config(self):
        """
        print_config prints the configuration to the console.
        Does not work.
        """
        print(json.dumps(self.cfg.__dict__))

    def evaluate_args(self, args):
        """
        evaluate_args evaluate arguments from main function
        """
        self.__evaluate_args_config(args)
        self.cfg.config.logging_level = args.verbosity
        self.cfg.config.interactive = args.menu
        self.cfg.fitz.export.write_all_images = not args.noimages
        self.cfg.fitz.export.write_text = not args.notext
        self.cfg.fitz.export.write_html = not args.nohtml
        self.cfg.fitz.export.write_toc = not args.notoc
        self.cfg.input.input_dirs = args.pdffolder

    def __evaluate_args_config(self, args):
        """
        __evaluate_args_config handles the configuration file command
        line argument

        :param args: command line arguments as object
        :type args: argparse.Namespace
        """
        if args.config:
            config_dir = Path(args.config).parent
            config_file = Path(args.config).name
            if Path(args.config).suffix != '.json':
                print('Adding json file extension to name.')
                config_file = Path(config_file + '.json')
            if not config_dir.exists():
                print(f'Warning, cannot find path {config_dir}\n')
            if Path(config_dir, config_file).exists():
                self.cfg.config.config_dir = config_dir
                self.cfg.config.config_file = config_file
                self.read_config()
            else:
                print(
                    f'Cannot find config file at {Path(config_dir, config_file)}')
