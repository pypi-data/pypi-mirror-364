class Config:
    td_apikey     = None
    av_apikey     = None
    fred_apikey   = None
    bea_apikey    = None
    bls_apikey    = None
    email_address = None
    td_baseurl    = 'https://api.twelvedata.com/'
    av_baseurl    = 'https://www.alphavantage.co/query?function='
    fred_baseurl  = 'https://api.stlouisfed.org/fred/'
    sec_baseurl   = 'https://www.sec.gov/'
    bea_baseurl   = 'https://apps.bea.gov/api/data'

def set_config(td=None, av=None, cg=None, fmp=None, fred=None, email=None, bea=None, bls=None):
    Config.td_apikey     = td
    Config.av_apikey     = av
    Config.fred_apikey   = fred
    Config.email_address = email
    Config.bea_apikey    = bea
    Config.bls_apikey    = bls

