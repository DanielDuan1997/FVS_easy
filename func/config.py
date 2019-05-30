from os import makedirs, path
from datetime import datetime

class Configuration(object):
    def __init__(self, conf_dct):
        assert isinstance(conf_dct, dict), \
            f"expect dict, got {type(conf_dct)}"
        self.__dict__.update(conf_dct)
        self.begin = datetime.strptime(str(self.begin), "%Y%m%d")
        self.end = datetime.strptime(str(self.end), "%Y%m%d")
        if not path.exists(self.report_root):
            makedirs(self.report_root)