import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

import copy
import datetime as dt
import numpy as np

def simulate(startdate, enddate, symbols, allocations):
    """
    A Python function that can simulate and assess the performance of a 4 stock portfolio.
    Inputs to the function include:
      Start date
      End date
      Symbols for for equities (e.g., GOOG, AAPL, GLD, XOM)
      Allocations to the equities at the beginning of the simulation (e.g., 0.2, 0.3, 0.4, 0.1)
    """

    # Get actual end timestamps for trading days on NYSE
    trading_duration = dt.timedelta(hours=16)
    trading_timestamps = du.getNYSEdays(startdate, enddate, trading_duration)

    # Get data from Yahoo
    data_provider = da.DataAccess('Yahoo', cachestalltime=0)
    data_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    data_list = data_provider.get_data(trading_timestamps, symbols, data_keys)
    data = dict(zip(data_keys, data_list))

    # Get 'close' prices and normalized then
    close_prices = data['close'].values
    normalized_close = close_prices / close_prices[0, :]

    # Compute portfolio by multiplying weights
    portfolio_prices = (allocations * normalized_close).sum(axis=1)

    # Compute daily returns for portfolio
    portfolio_rets = portfolio_prices.copy()
    tsu.returnize0(portfolio_rets)

    # Final statistics
    volatility = portfolio_rets.std()
    avg_return = portfolio_rets.mean()
    sharpe = tsu.get_sharpe_ratio(portfolio_rets)
    cum_return = np.prod(1 + portfolio_rets)

    return (volatility, avg_return, sharpe, cum_return)


def next_seq(sz, limit=10):
    """
    returns all possible sequences [a1, a2, ..., a{sz}] so that their sum is equal to limit
    """
    if sz == 1:
        return [[limit / 10.]]
    accum = list()
    for i in range(limit + 1):
        for n in next_seq(sz -1, i):
            accum = accum + [n + [(limit - i) / 10.]]
    return accum


def optimize(startdate, enddate, symbols):
    """
    Compute optimal portfolio for given symbols, startdate and enddate
    The method iterates over all possible portfolio weights at 0.1 increment
    """
    best_sharpe = -np.inf
    best_port = None
    best_alloc = None

    for allocation in next_seq(len(symbols)):
        port = simulate(startdate, enddate, symbols, allocation)
	print allocation, " -> ", port
        if port[2] > best_sharpe:
            best_sharpe = port[2]
            best_port = copy.deepcopy(port)
            best_alloc = copy.deepcopy(allocation)

    print best_port
    print best_alloc
