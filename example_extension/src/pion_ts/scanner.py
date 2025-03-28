"""Example scanner extension for pion.

This scanner is an example of how you can use the pion framework
to write a new scanner.
"""

import os
import tempfile
import typing
import zipfile

import pandas
import requests

from pion.common import interfaces


class Scanner(interfaces.Scanner):
    """Get data from World Bank data.

    The following illustrates example usage:

>>> from pion_ts import Scanner
>>> scnr = Scanner()
>>> fields = ['USA', 'DEU', 'EUU', 'JPN']
>>> data = scnr.get_data('NY.GDP.MKTP.CD', fields,
...                      '2019-01-01', '2023-12-31')
>>> print(data)  # doctest: +NORMALIZE_WHITESPACE
Country Code           USA           DEU           EUU           JPN
event_date
2019-12-31    2.153998e+13  3.957208e+12  1.580840e+13  5.117994e+12
2020-12-31    2.135410e+13  3.940143e+12  1.550470e+13  5.055587e+12
2021-12-31    2.368117e+13  4.348297e+12  1.749655e+13  5.034621e+12
2022-12-31    2.600689e+13  4.163596e+12  1.699533e+13  4.256411e+12
2023-12-31    2.772071e+13  4.525704e+12  1.859072e+13  4.204495e+12

    """

    base_url = "https://api.worldbank.org/v2/en/indicator"

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

        """
        url = f"{self.base_url}/{specifier}?downloadformat=csv"
        req = requests.get(url, timeout=self.timeout)
        self.raise_if_non_200(req)

        with tempfile.TemporaryDirectory() as temp_dir:
            zip_filename = os.path.join(temp_dir, 'world_bank_data.zip')

            with open(zip_filename, 'wb') as f:
                f.write(req.content)

            with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            extracted_files = os.listdir(temp_dir)
            csv_file = next(f for f in extracted_files if f.endswith(
                '.csv') and not f.startswith('Metadata_'))

            data_file = os.path.join(temp_dir, csv_file)

            df = pandas.read_csv(data_file, skiprows=3)
            df = df[['Country Code'] + [
                i for i in list(df) if i[0] in ('1','2')]].set_index(
                    'Country Code').T
            df.index = [pandas.Timestamp(int(i), 12, 31) for i in df.index]
            df.index.name = 'event_date'
        df = df.loc[(df.index >= start_date) & (df.index <= end_date)]
        if fields:
            df = df[fields]
        return df

    @classmethod
    def get_valid_fields(cls) -> typing.List[str]:
        "Return [] to indicate that fields are dynamic."

        return []
