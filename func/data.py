import pandas as pd
from datetime import datetime, timedelta
from time import time

from func.utils import timeit

class FileFormatError(Exception):
    pass

class DataProxy(object):
    def __init__(self, cfg):
        self._cfg = cfg

    @timeit
    def get_factor_data(self):
        path = self._cfg.factor_path
        try:
            begin_date = self._cfg.begin
            end_date = self._cfg.end
            df = pd.read_pickle(path)
            df["trade_date"] = pd.to_datetime(df["trade_date"], format="%Y%m%d")
            df = df[(begin_date <= df.trade_date) & (df.trade_date <= end_date)]
        except Exception as e:
            raise FileFormatError(f"[{path}] with wrong format:[{e}]")
        return df
    
    @timeit
    def get_market_data(self):
        path = self._cfg.market_path
        try:
            begin_date = self._cfg.begin
            end_date = self._cfg.end
            df = pd.read_pickle(path)
            df = df[(begin_date <= df.trade_date) & (df.trade_date <= end_date + timedelta(days=1))]
        except Exception as e:
            raise FileExistsError(f"[{path}] with wrong format: [{e}]")
        return df