"""Scanner for Bureau of Labor Statistics (BLS).
"""

import json
import typing

import pandas
import requests

from pion.common import interfaces


class Scanner(interfaces.Scanner):
    """Scanner for Bureau of Labor Statistics (BLS).
    """

    base_url = 'https://api.bls.gov/publicAPI/'

    @classmethod
    def get_valid_fields(cls) -> typing.List[str]:
        "Return list of valid fields for this scanner."

        return ['value']

    def get_header(self) -> typing.Dict[str, str]:
        """Get headers for web request
        """
        headers = {'Content-type': 'application/json'}
        return headers

    def get_data(self,
                 specifier: str,
                 fields: typing.Sequence[str],
                 start_date: pandas.Timestamp,
                 end_date: typing.Optional[pandas.Timestamp] = None
                 ) -> pandas.DataFrame:
        """Get the time series data.

    :arg specifier:   String to specify what data to get from scanner.

    :arg fields:      List of strings indicating fields to get.

    :arg start_date:  Earliest data for returned data.

    :arg end_date=None:  Latest date for returned data.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    :returns:   A pandas DataFrame containing requested data.

    ~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-~-

    PURPOSE:    Provide a common interface for use with pion data writers.

                The following illustrates example usage to get data for
                Consumer Price Index for All Urban Consumers (CPI-U),
                U.S. city average, all items, not seasonally adjusted.

>>> from pion.simple_scanners.bls import Scanner
>>> scnr = Scanner()
>>> data = scnr.get_data('CUUR0000SA0',  # series is CPI-U
...                     ['value'], '2011-01-01', end_date='2020-01-01')
>>> print(data)  # doctest: +ELLIPSIS
              value
2020-12-01  260.474
2020-11-01  260.229
2020-10-01  260.388
2020-09-01  260.280
2020-08-01  259.918
...             ...

        """
        api_key = self.get_api_key()
        endyear = self.to_ts(end_date).year if end_date else (
            pandas.Timestamp.today())
        data = {"seriesid": [specifier],
                "startyear": str(self.to_ts(start_date).year),
                "endyear": str(endyear)
                }
        if api_key:
            data['registrationkey'] = api_key
        req = requests.post(f'{self.base_url}/v2/timeseries/data/',
                            data=json.dumps(data), headers=self.get_header(),
                            timeout=self.timeout)
        if req.status_code != 200:
            raise ValueError(f'Invalid status code {req.status_code}'
                             f'; reason: {getattr(req, "reason", "unknown")}')
        json_data = json.loads(req.text)
        if json_data['status'] == 'REQUEST_NOT_PROCESSED':
            raise ValueError(f'BLS refused to process request: {req.text}')
        series = json_data['Results']['series'][0]['data']
        index = []
        value = []
        for item in series:
            if item['period'][0] == 'M':
                period = pandas.Timestamp(
                    year=int(item['year']),
                    month=int(item['period'][1:]),
                    day=1)
            else:
                raise ValueError(
                    f'Do not know how to manage period {period}')
            index.append(period)
            value.append(item['value'])
        return pandas.DataFrame({'value': value}, index=index)
