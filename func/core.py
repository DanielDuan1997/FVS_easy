import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from os import path

from func.utils import timeit, log

class FactorValidator(object):
    def __init__(self, cfg, data_proxy):
        self._cfg = cfg
        self._data_proxy = data_proxy
        self.alpha_df = None
        self.result = None


    @timeit
    def run(self):
        self.prepare()
        self.compute()
        self.save()


    @timeit
    def prepare(self):
        data_proxy = self._data_proxy
        alpha_df = data_proxy.get_factor_data()

        market_df = data_proxy.get_market_data()

        df = pd.merge(alpha_df, market_df, how="right", on=["wind_code", "trade_date"])
        df.rename(columns={"adj_avg_price": "price"}, inplace=True)

        assert not df.empty, "No matching days between alpha dates and market dates"

        log("start finding stop limit stocks")
        lag = self._cfg.lag
        nxt_high_df = df.pivot(index="trade_date", columns="wind_code", values="high").shift(-lag).dropna(how="all")
        nxt_low_df = df.pivot(index="trade_date", columns="wind_code", values="low").shift(-lag).dropna(how="all")
        nxt_df = (nxt_low_df < nxt_high_df).stack().to_frame("limit_trade_status").reset_index()
        df = pd.merge(df, nxt_df, on=["trade_date", "wind_code"])
        log("finish finding stop limit stocks")

        df = self.cal_rtn_df(df)

        log("start filter out tradable stocks")
        df = df.loc[df["trade_status"], ["trade_date", "wind_code", "alpha", "rtn", "limit_trade_status"]]
        log("finished filter out tradable stocks")

        self.alpha_df = df.set_index(["trade_date", "wind_code"])


    @timeit
    def compute(self):
        def divide(grp_by_trade_date_df):
            rk = grp_by_trade_date_df.rank(method="first", ascending=True)
            return (rk * self._cfg.num_grp / rk.max()).fillna(-999).astype(int)

        df = self.alpha_df

        grp = df[["alpha"]].groupby(level="trade_date").apply(divide)

        grp_mask = df
        grp_mask["grp_id"] = grp["alpha"]

        grp_ret = []
        num_grp = self._cfg.num_grp
        for grp_id in range(num_grp):
            p = grp_mask.groupby(level="trade_date").apply(
                lambda x: x["rtn"].T.dot((x["grp_id"] == grp_id) & x["limit_trade_status"])
                    / (x["grp_id"] == grp_id).sum())
            p.index.names = ["trade_date"]
            p = p.to_frame("yield")
            p["group_id"] = grp_id
            grp_ret.append(p)
        agg_df = pd.concat(grp_ret, axis=0)
        agg_df.reset_index(inplace=True)
        agg_df = agg_df.pivot(index="trade_date", columns="group_id", values="yield")
        agg_df = agg_df.cumsum()
        agg_mean = agg_df.mean(axis=1)
        for grp_id in range(10):
            agg_df[grp_id] -= agg_mean
        agg_df.columns = pd.RangeIndex(start=1, stop=11, step=1)
        self.result = agg_df


    def save(self):
        sns.set_palette(sns.color_palette())
        sns.set_context('talk')
        sns.set_style('whitegrid')
        params = {
            'figure.figsize': [12, 8],
            'figure.dpi': 100,
            'xtick.labelsize': 18,
            'ytick.labelsize': 18,
            'axes.titlesize': 25,
            'axes.titlepad': 20,
            'axes.titleweight': 'bold',
            'axes.labelweight': 'bold',
            'axes.labelsize': 20,
            'axes.labelpad': 20
        }
        plt.rcParams.update(params)

        title = self._cfg.factor_path.split('/')[-1].split('.')[0]
        self.result.plot(title=title, fontsize=20).get_figure().savefig(
            path.join(self._cfg.report_root, title + '.jpg'))


    @timeit
    def cal_rtn_df(self, df):
        lag = self._cfg.lag
        forecast_period = self._cfg.forecast_period

        tbl = df.pivot(index="trade_date", columns="wind_code", values="price")
        tbl = tbl.shift(-lag)
        tbl = tbl.shift(-forecast_period) / tbl - 1
        tbl.dropna(how="all", inplace=True)
        tbl_df = tbl.stack().to_frame("rtn").reset_index()

        return pd.merge(df, tbl_df)
