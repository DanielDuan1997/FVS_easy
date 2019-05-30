import yaml

from func.config import Configuration
from func.data import DataProxy
from func.core import FactorValidator

if __name__ == '__main__':
    
    cfg_dct = yaml.load(open('param.yaml'), Loader=yaml.FullLoader)
    cfg = Configuration(cfg_dct)

    data_proxy = DataProxy(cfg)

    FactorValidator(cfg, data_proxy).run()
