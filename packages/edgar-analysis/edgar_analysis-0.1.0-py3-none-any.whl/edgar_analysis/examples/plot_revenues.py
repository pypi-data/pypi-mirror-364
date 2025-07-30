"""plot_revenues.py"""

from edgar import set_identity
from edgar_analysis.main import CompanyAnalysis

import matplotlib.pyplot as plt

set_identity('gafzan@gmail.com')


def main():
    ticker = 'WMT'
    periods = 6
    freq = 'ttm'
    analyst = CompanyAnalysis(ticker=ticker)
    revenues = analyst.get_revenues(periods=periods, frequency=freq)
    print(revenues)
    print('Plotting the result...')
    revenues.plot()
    plt.show()


if __name__ == '__main__':
    main()
