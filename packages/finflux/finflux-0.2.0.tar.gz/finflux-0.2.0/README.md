<!--README.md files serve as the main landing page on this directory's github repository. It is the first thing that a viewer sees when he or she enters the github repo.

-->
# FinFlux API

`finflux` offers financial and market data # FinFlux API

`finflux` offers financial and market data retrieval through multiple publicly available free REST JSON API endpoints found online in one aggregate Python library.


`finflux` utilizes both first-party and third-party APIs connected to the sources listed below.
- Yahoo Finance
- Twelve Data
- Alpha Vantage
- Securities and Exchange Commission (SEC)
- Organization for Economic Co-operation and Development (OECD)
- Board of Governors of the Federal Reserve System
- U.S. Department of the Treasury
- Bureau of Economic Analysis (BEA)
- Bureau of Labor Statistics (BLS)
- U.S. Census Bureau
- National Association of REALTORS® (NAR)
- Freddie Mac

## Installation and Setup

First, install `finflux` from PyPi using `pip` and import the library using `import`

```bash
pip install finflux
```

```python
import finflux as fin
```

Before accessing data retrieval functions, you must set your API keys and email address to use certain functions within the library that require an identifier. If no API key or email address is found when needed, a `MissingConfigObject` error will be raised.

Currently, functions utilizing Twelve Data, Alpha Vantage, SEC, FRED, BEA, and BLS APIs all require identifiers in the form of API keys (with the exception of the SEC, requiring an email address instead). Use the links below to retrieve API keys for each source.
- [Twelve Data](https://twelvedata.com/pricing)
- [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
- [Federal Reserve Economic Data](https://fred.stlouisfed.org/docs/api/api_key.html)
- [Bureau of Economic Analysis](https://apps.bea.gov/api/signup/)
- [Bureau of Labor Statistics](https://data.bls.gov/registrationEngine/)

After gaining access to all API keys pertaining to data of your choice, input the identifier strings through the `set_config` function.

```
fin.set_config(
    td = 'your_twelve_data_api_key',
    email = 'example@example.com',
    av = 'your_alpha_vantage_api_key',
    fred = 'your_FRED_api_key',
    bea = 'your_BEA_api_key',
    bls = 'your_BLS_api_key'
)
```

## Library Components (Classes and Methods)

- `finflux.equity('EQUITY_TICKER')`
    - `timeseries()`, `realtime()`, `statement()`, `quote()`, `info()`, `news()`, `filings()`, `eps()`, `analyst_estimates()`, `dividend()`, `split()`, `stats()`, `top()`
- `finflux.bond()`
    - `nonUS_10Y_sovereign()`, `US_treasury()`, `US_curve()`, `US_eod()`, `US_quote()`, `US_HQM_corporate()`
- `finflux.US_indic()`: 
    - `gdp()`, `price_index()`, `pce()`, `unemployment()`, `labor()`, `sentiment()`, `fed_rate()`, `housing()`

For a more detailed overview of each method, each class also has its own `help()` method, outlining each function's description, parameters, and API source.

```python
finflux.bond().help()
```

EXAMPLE #1: Retrieving table formatted annual income statement data in EUR in millions excluding units past the decimals for Apple Inc. (AAPL).

```python
finflux.equity('AAPL').statement(display='table', statement='income', currency='EUR', unit='million', decimal=False, interval='annual')
```