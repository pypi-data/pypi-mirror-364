from finflux.base_var import Config

import yfinance as yf # type: ignore
import numpy as np # type: ignore
import requests # type: ignore
import pandas as pd # type: ignore
import matplotlib.pyplot as plt # type: ignore
from datetime import timedelta, datetime

#------------------------------------------------------------------------------------------
class InvalidParameterError(Exception):
    def __init__(self, msg):
        self.msg = msg

class InvalidSecurityError(Exception):
    def __init__(self, msg: str):
        self.msg = msg

class MissingConfigObject(Exception):
    def __init__(self, msg: str):
        self.msg = msg

#------------------------------------------------------------------------------------------
class bond:
#------------------------------------------------------------------------------------------
    def help(self):
        output = '''
class bond():
 |  nonUS_10Y_sovereign()---10Y sovereign bond yields for non-US countries
 |      country     :str        =None       [KR, AT, CL, CZ, GR, FI, ZA, NL, SK, NZ, LU, PL, SI, CH, DE, CA, JP, DK, BE, FR, NO, PT, IT, GB, ES, IE, AU, SE, MX, HU, IS]
 |      period      :str        =5y         [1y, 2y, 5y, 10y, max]
 |      -----api(s): FRED(OECD)
 |
 |  US_treasury()-----------US treasury bond yield daily timeseries
 |      maturity    :str        =10y        [6mo, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y]
 |      period      :str        =5y         [6mo, 1y, 2y, 5y, 10y, ytd, max]
 |      -----api(s): FRED(Board of Governers)
 |      
 |  US_curve()--------------US treasury bond yield curve (EOD, 3MO, 6MO)
 |      display     :str        =graph      [json, table, graph]
 |      -----api(s): FRED(Board of Governers)
 |      
 |  US_eod()----------------US treasury bond eod yield
 |      display     :str        =json       [json, pretty]
 |      maturity    :str        =10y        [6mo, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y]
 |      -----api(s): FRED(Board of Governers)
 |      
 |  US_quote()--------------US treasury bond quote: TTM high/low, percent change (5d, 1m, 6m, ytd, 1y, 5y), SMAs
 |      display     :str        =json       [json, pretty]
 |      maturity    :str        =10y        [6mo, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y]
 |      -----api(s): FRED(Board of Governers)
 |
 |  US_HQM_corporate()------US high quality (A, AA, AA) corporate bond yield monthly timeseries
 |      maturity    :str        =10y        [6mo, 1y, 2y, 3y, 5y, 7y, 10y, 20y, 30y]
 |      period      :str        =5y         [6mo, 1y, 2y, 5y, 10y, ytd, max]
 |      -----api(s): FRED(US Treasury)
'''

        print(output)
#------------------------------------------------------------------------------------------
    def nonUS_10Y_sovereign(self, country: str = None, period: str = '5y'): 
        valid_params = {'valid_country': ['KR', 'AT', 'CL', 'CZ', 'GR', 'FI', 'ZA', 'NL', 'SK', 'NZ', 'LU', 'PL', 'SI', 'CH', 'DE', 'CA', 'JP', 'DK', 'BE', 'FR', 'NO', 'PT', 'IT', 'GB', 'ES', 'IE', 'AU', 'SE', 'MX', 'HU', 'IS'],
                        'valid_period': ['1y', '2y', '5y', '10y', 'max']}
        
        #South Korea, Austria, Chile, Czechia, Greece, Finland, South Africa, Netherlands, Slovakia, New Zealand, Luxembourg, Poland, Slovenia, Switzerland, Germany, Canada, Japan, Denmark, Belgium, France, Norway, Portugal, Italy, United Kingdom, Spain, Ireland, Australia, Sweden, Mexico, Hungary, Iceland

        params = {'country': country,
                  'period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        
        ISO_3166 = {
            'KR': 'South Korea',
            'AT': 'Austria',
            'US': 'United States',
            'CL': 'Chile',
            'CZ': 'Czech Republic',
            'GR': 'Greece',
            'FI': 'Finland',
            'ZA': 'South Africa',
            'NL': 'Netherlands',
            'SK': 'Slovak Republic',
            'NZ': 'New Zealand',
            'LU': 'Luxembourg',
            'PL': 'Poland',
            'SI': 'Slovenia',
            'CH': 'Switzerland',
            'DE': 'Germany',
            'CA': 'Canada',
            'JP': 'Japan',
            'DK': 'Denmark',
            'BE': 'Belgium',
            'FR': 'France',
            'NO': 'Norway',
            'PT': 'Portugal',
            'IT': 'Italy',
            'GB': 'United Kingdom',
            'ES': 'Spain',
            'IE': 'Ireland',
            'AU': 'Australia',
            'SE': 'Sweden',
            'MX': 'Mexico',
            'HU': 'Hungary',
            'IS': 'Iceland'
        }

        FRED_IDs = {}
        for ISO in ISO_3166.keys():
            FRED_IDs[ISO] = f'IRLTLT01{ISO}M156N'

        period_points = {
            '1y': -12,
            '2y': -24,
            '5y': -60,
            '10y': -120,
        }

        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[country]

        FRED_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_bond = requests.get(FRED_url).json()
        #----------------------------------------------------------------------------------

        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
        
        #PARAMETER - PERIOD ================================================================
        data = {}
        if period == 'max':
            for data_point in FRED_bond['observations']:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)
        else:
            for data_point in FRED_bond['observations'][period_points[period]:]:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        output = pd.DataFrame.from_dict(data, orient='index', columns=[f'{ISO_3166[country]} 10Y'])
        output.index = pd.to_datetime(output.index)

        return output
#------------------------------------------------------------------------------------------
    def US_treasury(self, maturity: str = '10y', period: str = '5y'): 
        valid_params = {'valid_maturity': ['6mo', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y'],
                        'valid_period' : ['6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']}
        
        params = {'maturity': maturity,
                  'valid_period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        FRED_IDs = {
            '6mo': 'DGS6MO',
            '1y': 'DGS1',
            '2y': 'DGS2',
            '3y': 'DGS3',
            '5y': 'DGS5',
            '7y': 'DGS7',
            '10y': 'DGS10',
            '20y': 'DGS20',
            '30y': 'DGS30'
        }    

        period_points = {
            '6mo': -126,
            '1y': -252,
            '2y': -504,
            '5y': -1260,
            '10y': -2520,
        }

        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[maturity]

        FRED_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_yield = requests.get(FRED_url).json()

        current_year = pd.Timestamp.now().year
        #----------------------------------------------------------------------------------

        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
        
        #PARAMETER - PERIOD ================================================================  
        data = {}
        if period == 'max':
            for data_point in FRED_yield['observations']:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        elif period == 'ytd':
            for data_point in FRED_yield['observations'][-260:]:
                if data_point['date'][0:4] == str(current_year):
                    data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        else:
            for data_point in FRED_yield['observations'][period_points[period]:]:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        output = pd.DataFrame.from_dict(data, orient='index', columns=[f'US {maturity.upper()}'])
        output.index = pd.to_datetime(output.index)

        return output
#------------------------------------------------------------------------------------------
    def US_curve(self, display: str = 'graph'):
        valid_params = {'valid_display': ['json', 'table', 'graph']}
        
        params = {'display': display}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
        
        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        six_m = bond().US_treasury(maturity='6mo', period='6mo')
        one_y = bond().US_treasury(maturity='1y', period='6mo')
        two_y = bond().US_treasury(maturity='2y', period='6mo')
        three_y = bond().US_treasury(maturity='3y', period='6mo')
        five_y = bond().US_treasury(maturity='5y', period='6mo')
        seven_y = bond().US_treasury(maturity='7y', period='6mo')
        ten_y = bond().US_treasury(maturity='10y', period='6mo')
        twenty_y = bond().US_treasury(maturity='20y', period='6mo')
        thirty_y = bond().US_treasury(maturity='30y', period='6mo')

        yield_list = [six_m, one_y, two_y, three_y, five_y, seven_y, ten_y, twenty_y, thirty_y]
        #----------------------------------------------------------------------------------
        
        #JSON FORMAT DATA
        curve_data = {}

        for dataframe in yield_list:
            curve_data[f'{dataframe.columns[0]}'] = {
                '6mo': float(dataframe.iloc[0].iloc[0]),
                '3mo': float(dataframe.iloc[63].iloc[0]),
                'eod': float(dataframe.iloc[-1].iloc[0])
            }

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = curve_data
        elif display == 'table':
            output = pd.DataFrame.from_dict(curve_data, orient='index')
            output.columns = output.columns.str.upper()
        elif display == 'graph':
            maturities = []
            for i in list(curve_data.keys()):
                maturities.append(i[2:])

            six_m_yields = []
            three_m_yields = []
            eod_yields = []

            for maturity in curve_data.keys():
                six_m_yields.append(curve_data[maturity]['6mo'])
                three_m_yields.append(curve_data[maturity]['3mo'])
                eod_yields.append(curve_data[maturity]['eod'])

            fig, ax = plt.subplots()
            ax.plot(maturities, six_m_yields, label='6MO', color='#A7CBE8', linewidth=2.5)
            ax.plot(maturities, three_m_yields, label='3MO', color='#2171B5', linewidth=2.5)
            ax.plot(maturities, eod_yields, label='EOD', color='#1F4E79', linewidth=2.5)

            ax.set_xlabel('Maturity Date')
            ax.set_ylabel('Yield (%)')
            ax.set_title('US Treasury Bond Yield Curve')

            ax.legend()
            
            output = None
            plt.show()

        return output
#------------------------------------------------------------------------------------------
    def US_eod(self, display: str = 'json', maturity: str = '10y'): 
        valid_params = {'valid_display': ['json', 'pretty'],
                        'valid_maturity': ['6mo', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']}
        
        params = {'display': display,
                  'maturity': maturity,}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")
            
        FRED_IDs = {
            '6mo': 'DGS6MO',
            '1y': 'DGS1',
            '2y': 'DGS2',
            '3y': 'DGS3',
            '5y': 'DGS5',
            '7y': 'DGS7',
            '10y': 'DGS10',
            '20y': 'DGS20',
            '30y': 'DGS30'
        }
        
        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[maturity]

        FRED_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_yield = requests.get(FRED_url).json()
        #----------------------------------------------------------------------------------

        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False

        #JSON FORMAT DATA
        eod_data = {
            'country': 'United States',
            'maturity': maturity.upper(),
            'date': FRED_yield['observations'][-1]['date'],
            'yield': (float(FRED_yield['observations'][-1]['value']) if is_numeric(FRED_yield['observations'][-1]['value']) else np.nan)
        }

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = eod_data
            return output
        if display == 'pretty':
            output = f''' COUNTRY - United States
MATURITY - {eod_data['maturity']}
    DATE - {eod_data['date']}
   YIELD - {eod_data['yield']}'''
            print(output)
#------------------------------------------------------------------------------------------
    def US_quote(self, display: str = 'json', maturity: str = '10y'): 
        valid_params = {'valid_display': ['json', 'pretty'],
                        'valid_maturity': ['6mo', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']}
        
        params = {'display': display,
                  'maturity': maturity}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATIONS--------------------------------------------------------------
        US_timeseries = bond().US_treasury(maturity=maturity, period='10y')
        
        US_eod = bond().US_eod(display='json', maturity=maturity)['yield']
        
        current_year = pd.Timestamp.now().year
        #-----------------------------------------------------------------------------------
        
        #JSON FORMAT DATA
        quote_data = {
            'identifier': f'US {maturity.upper()} Treasury Bond Yield',
            'ttm': {
                'high': round(float((US_timeseries.iloc[-252:].max()).iloc[0]),2),
                'low': round(float((US_timeseries.iloc[-252:].min()).iloc[0]),2)
            },
            'percent change': {
                '5y': float(((US_eod/US_timeseries.iloc[-1260]) - 1).iloc[0] if pd.notna(US_timeseries.iloc[-1260].iloc[0]) else ((US_eod/US_timeseries.iloc[-1260]) - 1).iloc[1]),
                '1y': float(((US_eod/US_timeseries.iloc[-252]) - 1).iloc[0] if pd.notna(US_timeseries.iloc[-252].iloc[0]) else ((US_eod/US_timeseries.iloc[-252]) - 1).iloc[1]),
                'ytd': float(((US_eod/US_timeseries[US_timeseries.index.year == current_year].iloc[0]) - 1).iloc[0] if pd.notna(US_timeseries[US_timeseries.index.year == current_year].iloc[0].iloc[0]) else ((US_eod/US_timeseries[US_timeseries.index.year == current_year].iloc[1]) - 1).iloc[0]),
                '6m': float(((US_eod/US_timeseries.iloc[-126]) - 1).iloc[0] if pd.notna(US_timeseries.iloc[-126].iloc[0]) else ((US_eod/US_timeseries.iloc[-126]) - 1).iloc[1]),
                '1m': float(((US_eod/US_timeseries.iloc[-21]) - 1).iloc[0] if pd.notna(US_timeseries.iloc[-21].iloc[0]) else ((US_eod/US_timeseries.iloc[-21]) - 1).iloc[1]),
                '5d': float(((US_eod/US_timeseries.iloc[-5]) - 1).iloc[0] if pd.notna(US_timeseries.iloc[-5].iloc[0]) else ((US_eod/US_timeseries.iloc[-5]) - 1).iloc[1])
            },
            '50d average price': float((US_timeseries.iloc[-50:].mean()).iloc[0]),
            '200d average price': float((US_timeseries.iloc[-200:].mean()).iloc[0])
        }

        #PARAMETER - DISPLAY ===============================================================
        if display == 'json':
            output = quote_data
            return output
        elif display == 'pretty':
            output = f'''
{quote_data['identifier']} Quote

TTM HIGH/LOW----------------------------
         HIGH --  {round(quote_data['ttm']['high'],2):,}
          LOW --  {round(quote_data['ttm']['low'],2):,}
PERCENT CHANGE--------------------------
       5 YEAR -- {' ' if pd.isna(quote_data['percent change']['5y']) or quote_data['percent change']['5y']>0 else ''}{round(quote_data['percent change']['5y'] * 100,2)}%
       1 YEAR -- {' ' if pd.isna(quote_data['percent change']['1y']) or quote_data['percent change']['1y']>0 else ''}{round(quote_data['percent change']['1y'] * 100,2)}%
          YTD -- {' ' if pd.isna(quote_data['percent change']['ytd']) or quote_data['percent change']['ytd']>0 else ''}{round(quote_data['percent change']['ytd'] * 100,2)}%
      6 MONTH -- {' ' if pd.isna(quote_data['percent change']['6m']) or quote_data['percent change']['6m']>0 else ''}{round(quote_data['percent change']['6m'] * 100,2)}%
      1 MONTH -- {' ' if pd.isna(quote_data['percent change']['1m']) or quote_data['percent change']['1m']>0 else ''}{round(quote_data['percent change']['1m'] * 100,2)}%
        5 DAY -- {' ' if pd.isna(quote_data['percent change']['5d']) or quote_data['percent change']['5d']>0 else ''}{round(quote_data['percent change']['5d'] * 100,2)}%
MOVING AVERAGES-------------------------
 50 DAY YIELD --  {round(quote_data['50d average price'],2)}
200 DAY YIELD --  {round(quote_data['200d average price'],2)}
'''
            print(output)
#------------------------------------------------------------------------------------------
    def US_HQM_corporate(self, maturity: str = '10y', period: str = '5y'): 
        valid_params = {'valid_maturity': ['6mo', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y'],
                        'valid_period' : ['6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']}
        
        params = {'maturity': maturity,
                  'valid_period': period}

        for param_key, param_value, valid_param in zip(params.keys(), params.values(), valid_params.values()):
            if param_value not in valid_param:
                raise InvalidParameterError(f"Invalid {param_key} parameter '{param_value}'. "
                                            f"Please choose a valid parameter: {', '.join(valid_param)}")

        FRED_IDs = {
            '6mo': 'HQMCB6MT',
            '1y': 'HQMCB1YR',
            '2y': 'HQMCB2YR',
            '3y': 'HQMCB3YR',
            '5y': 'HQMCB5YR',
            '7y': 'HQMCB7YR',
            '10y': 'HQMCB10YR',
            '20y': 'HQMCB20YR',
            '30y': 'HQMCB30YR'
        }    

        period_points = {
            '6mo': -126,
            '1y': -252,
            '2y': -504,
            '5y': -1260,
            '10y': -2520,
        }

        if Config.fred_apikey is None:
            raise MissingConfigObject('Missing fred_apikey. Please set your FRED api key using the set_config() function.')
        
        #RAW DATA/OBSERVATION--------------------------------------------------------------
        id = FRED_IDs[maturity]

        FRED_url = f'https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={Config.fred_apikey}&file_type=json'
        FRED_bond = requests.get(FRED_url).json()

        current_year = pd.Timestamp.now().year
        #----------------------------------------------------------------------------------
        def is_numeric(str):
            try:
                float(str)
                return True
            except ValueError:
                return False
        
        #PARAMETER - PERIOD ================================================================  
        data = {}
        if period == 'max':
            for data_point in FRED_bond['observations']:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        elif period == 'ytd':
            for data_point in FRED_bond['observations'][-260:]:
                if data_point['date'][0:4] == str(current_year):
                    data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        else:
            for data_point in FRED_bond['observations'][period_points[period]:]:
                data[data_point['date']] = (float(data_point['value']) if is_numeric(data_point['value']) else np.nan)

        output = pd.DataFrame.from_dict(data, orient='index', columns=[f'US HQM {maturity.upper()}'])
        output.index = pd.to_datetime(output.index)

        return output
#------------------------------------------------------------------------------------------