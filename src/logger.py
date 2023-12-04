"""Required standard modules:
     logging for configuration of loggers
     json for reading and writing configuration files
     pathlib for accessing files
"""
import logging  # Standard logging module
import logging.config
import json
from pathlib import Path

class Logger():
    logpath = Path('.')  # Path to the logfile
    config = {}  # Dictionary for the logging configuration
    debugoutput = True  # Should be set to False after implementation is complete

    def __init__(self):
        self.restore_default_settings()
        self.local_settings_dir = Path('.')
        self.local_settings_file = Path(self.local_settings_dir, 'log.json')

    def restore_default_settings(self):
        """
        restore_default_settings Initializes the root logger and applies default settings for the individual components
        """
        logging.basicConfig(level=logging.NOTSET)
        self.config = {'version': 1,
                       'disable_existing_loggers': False,
                       'formatters': {'default_format': 
                           {'format': '%(asctime)s:%(name)s:%(levelname)s:%(message)s'}},
                       'handlers': {'console': {'class': 'logging.StreamHandler',
                                                'formatter': 'default_format',
                                                'level': logging.ERROR,
                                                'stream': 'ext://sys.stdout'},
                                    'file': {'class': 'logging.FileHandler',
                                             'formatter': 'default_format',
                                             'filename': f'{Path(self.logpath, "chaospdf.log")}',
                                             'level': 'DEBUG'}},
                       'loggers': {'root': {'handlers': ['console', 'file']},
                                   'main': {'handlers': ['console', 'file'],
                                            'propagate': False},
                                   'file': {'handlers': ['console', 'file'],
                                            'propagate': False},
                                   'filef': {'handlers': ['file'],
                                            'propagate': False},
                                   'doc': {'handlers': ['console', 'file'],
                                           'propagate': False},
                                   'page': {'handlers': ['console', 'file'],
                                            'propagate': False},
                                   'img': {'handlers': ['console', 'file'],
                                           'propagate': False},
                                   'config': {'handlers': ['console', 'file'],
                                              'propagate': False}}}
        logging.config.dictConfig(self.config)

    def print_config(self):
        """
        print_config Prints the configuration of the class to the console, NOT to a log file!
        """
        print(f'debugoutput: {self.debugoutput}')
        print(f'logpath: {self.logpath}')
        print(self.config)

    def read_settings(self, settings_file:Path):
        """
        read_settings Reads the settings for the log file configuration from a json file

        :param settings_file: Path and filename for the configuration file, ideally written by the write_settings method
        :type settings_file: Path
        :return: Indicator if reading the file was successful
        :rtype: Bool
        """
        success = True
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as fp:
                config = json.load(fp)
                self.config.update(config)
                if self.debugoutput:
                    for item in config:
                        print(item)
                success = True
        elif self.debugoutput:
            print(f'Cannot find settings file at {settings_file}')
            success = False
        else:
            success = False
        return success

    def write_settings(self, settings_file:Path):
        """
        write_settings Writes the settings for the log file configuration into a json file

        :param settings_file: Path and filename for the configuration file
        :type settings_file: Path
        :return: Indicator if writing the file was successful
        :rtype: Bool
        """
        success = True
        if settings_file.exists():
            try:
                settings_file.unlink()
            except OSError as e:
                success = False
                print(f'{e}\nwhile overwriting settings file for log configuration: {settings_file}')
        if success:
            with open(settings_file, 'w', encoding='utf-8') as fp:
                json.dump(self.config, fp, indent=4)
        return success
