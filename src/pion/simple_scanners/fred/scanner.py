"""Data scanner for St. Louis Fed (FRED) API.
"""

import logging as raw_logging  # use LOGGER not raw_logging (see below)
import doctest
import requests

import numpy
import pandas

from pion.common import interfaces


# Setup a logger for this module so easier to filter/find
# logging messages generated here.
LOGGER = raw_logging.getLogger(__name__)


class Scanner(interfaces.Scanner):
    """Scanner to download data from St. Louis Fed API
    """
    base_url = 'https://api.stlouisfed.org/fred'

    @classmethod
    def get_valid_fields(cls):
        "Return list of valid fields for this scanner."

        return ['close']

    @staticmethod
    def combine_data(frame_list):
        """Helper to splice together multiple frames into single series.
        """
        frame_list = [f for f in frame_list if not f.empty]
        sub_frames = []
        start_point = None
        for num, s_frame in enumerate(frame_list):
            if (num + 1) < len(frame_list):
                end_point = frame_list[num+1].index[0]
                s_frame = s_frame.loc[
                    [i < end_point for i in s_frame.index]]
            if start_point is not None:
                s_frame = s_frame.loc[[i > start_point for i in s_frame.index]]
            if not s_frame.empty:
                sub_frames.append(s_frame)
                start_point = sub_frames[-1].index[-1]
        result = pandas.concat(sub_frames)
        assert result.index.duplicated().sum() == 0
        return result

    def get_data(self, specifier, fields, start_date, end_date=None):
        """Implement get_data as required by parent class.

You can splice multiple series together via & (e.g., "DFF&SOFR").

See docs for the `_regr_test` method for example usage.        
        """
        start_date = start_date or self.to_ts(start_date)
        end_date = end_date or self.to_ts(end_date)
        if '&' in specifier:
            return self.combine_data([self.get_data(
                s, fields, start_date, end_date)
                                     for s in specifier.split('&')])
        valid_fields = self.get_valid_fields()
        for field in fields:
            assert field in valid_fields, f'field {field} not valid'
        params = {'series_id': specifier, 'api_key': self.get_api_key(),
                  'file_type': 'json'}
        url = f'{self.base_url}/series/observations'
        req = requests.get(url, params=params, timeout=self.timeout)
        self.raise_if_non_200(req)
        jdata = req.json()
        frame = pandas.DataFrame(jdata['observations'])[
            ['date', 'value']].rename(columns={
                'date': 'event_date', 'value': 'close'}).set_index(
                    'event_date')
        frame.index = pandas.to_datetime(frame.index)
        frame = frame.loc[frame.index >= start_date]
        if end_date is not None:
            frame = frame.loc[frame.index <= end_date]
        for field in fields:
            frame[field] = [self.float_or_nan(f) for f in frame[field]]

        return frame

    @staticmethod
    def float_or_nan(item):
        "Helper to convert input to float or nan if not possible"
        try:
            return float(item)
        except ValueError:
            return numpy.nan

    @staticmethod
    def _regr_test():
        """Example usage and regression test.

NOTE:  You will need an API key for FRED. You can either put that in
       the environment variable FRED_API_KEY or in ~/.FRED_API_KEY
       or pass it in to `__init__`.
        
>>> from pion.simple_scanners.fred import Scanner
>>> scnr = Scanner()
>>> dff_result = scnr.get_data('DFF', ['close'], '2000-01-01', '2000-01-06')
>>> print(dff_result[['close']])  # doctest: +NORMALIZE_WHITESPACE
            close
event_date
2000-01-01   3.99
2000-01-02   3.99
2000-01-03   5.43
2000-01-04   5.38
2000-01-05   5.41
2000-01-06   5.54

Note that some data sets will have NaN values because FRED
seems to want to explicitly tell you that they are missing
a value for certain dates:

>>> result = scnr.get_data('DGS10', ['close'],
...                        '1962-02-09', '1962-02-15')
>>> print(result[['close']])  # doctest: +NORMALIZE_WHITESPACE
            close
event_date
1962-02-09   4.05
1962-02-12    NaN
1962-02-13   4.03
1962-02-14   4.03
1962-02-15   4.02

We can auto-splice data series. For example, SOFR data starts on 2024-04-13
while Fed Funds starts much earlier. We can use the & character to
request spliced data and compare that to just SOFR:

>>> dff_sofr = scnr.get_data('DFF&SOFR', ['close'],
...                          '2018-04-02', '2018-04-04')
>>> sofr = scnr.get_data('SOFR', ['close'], '2018-04-02')
>>> print(dff_sofr)  # doctest: +NORMALIZE_WHITESPACE
            close
event_date
2018-04-02   1.68
2018-04-03   1.83
2018-04-04   1.74
>>> print(sofr.iloc[:4])  # doctest: +NORMALIZE_WHITESPACE
            close
event_date
2018-04-03   1.83
2018-04-04   1.74
2018-04-05   1.75
2018-04-06   1.75
"""


if __name__ == '__main__':
    doctest.testmod()
    print('Finished tests')
