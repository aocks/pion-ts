"""Common interfaces used in pion.
"""

import logging as raw_logging
import os
import typing

import pandas


# Setup a logger for this module so easier to filter/find
# logging messages generated here.
LOGGER = raw_logging.getLogger(__name__)


class Scanner:
    """An object to scan a data provider for time series data.

This represents an abstract interface that things can implement in order
to work with pion writers.
"""

    def __init__(self,
                 timeout: float = 60.0,
                 api_key: typing.Optional[str] = None,
                 scanner_name: typing.Optional[str] = None):
        """Initializer.

        :param timeout=60.0:  Optional timeout for classes which might
                              block and therefore need to timeout.

        :param api_key=None:  Optional API key to use for service.

        :param scanner_name:  Optional name for scanner (will be derived
                              from package containing module if not
                              provided).

        """
        self.timeout = timeout
        self.api_key = api_key
        self.scanner_name = scanner_name

        if not self.scanner_name:
            self.scanner_name = self.__class__.__module__.split(
                '.')[-2].upper()

    @classmethod
    def get_valid_fields(cls) -> typing.List[str]:
        """Return list of strings indicating fields available in `get_data`.
        """
        raise NotImplementedError

    @classmethod
    def to_ts(cls, my_date: typing.Union[pandas.Timestamp, str]
              ) -> pandas.Timestamp:
        """Parse date string to pandas Timestamp if necessary.

        Sub-classes can override to customize if necessary.
        """
        if my_date is None:
            return None
        if isinstance(my_date, pandas.Timestamp):
            return my_date
        return pandas.Timestamp(my_date)

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
        raise NotImplementedError

    def get_api_key(self):
        """Get API key from env var or file.

Sub-classes can call this to lookup the API key that was passed in
to `__init__` or try to find it from an environemnt variable with
a name like `{NAME}_API_KEY` or from the file `~/.{NAME}_API_KEY`
where `{NAME}` is the name of the scanner class.

        """
        if not self.api_key:
            evar = os.environ.get(f'{self.scanner_name}_API_KEY', None)
            if evar is not None and evar.strip():
                return evar.strip()
            home = os.environ.get('HOME', '')
            fname = os.path.join(home, f'.{self.scanner_name}_API_KEY')
            if os.path.exists(fname):
                with open(fname, 'r', encoding='utf8') as fdesc:
                    self.api_key = fdesc.read().strip()
                    LOGGER.info('Read API key from %s', fname)
        return self.api_key

    def raise_if_non_200(self, req):
        """Raise error if request response does not have code 200
        """
        if req.status_code != 200:
            raise ValueError(f'Bad status {req.status_code}; reason: ' +
                             str(getattr(req, 'reason', 'unknown')))
