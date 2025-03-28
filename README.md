
# Introduction

This project provides a basic interface and tools for downloading
time series data (and possibly storing them in a database).

The motivation is that there are lots of different sites which allow
you to download data but they all have different formats, conventions,
and so on.

Instead of everyone having to learn the details of each sites download
API, wouldn't it be nice if there was a reasonably standardized approach?

For example, imagine you want to get the effective Federal Funds Rate
from the Federal Reserve Bank of St. Louis (FRED) and you want to
get the CPI from the Bureau of Labor Statistics (BLS). Using pion,
you can do something like the following:

```

>>> from pion.simple_scanners.bls import Scanner as BLSScanner
>>> scnr = BLSScanner()
>>> data = scnr.get_data('CUUR0000SA0',  # series is CPI-U
...                     ['value'], '2011-01-01', end_date='2020-01-01')
>>> print(data)  # doctest: +ELLIPSIS
              value
2020-12-01  260.474
2020-11-01  260.229
2020-10-01  260.388
2020-09-01  260.280
2020-08-01  259.918
...

```

Similiarly, if you want to use FRED you can do something in the same
way but just using a different scanner even though FRED uses different
formats, requires an API key, etc.:

```

>>> import os
>>> api_key = open(os.path.expanduser('~/.FRED_API_KEY')).read().strip()
>>> from pion.simple_scanners.fred import Scanner as FREDScanner
>>> scnr = FREDScanner(api_key=api_key)
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

```

In both examples above, you simply import the Scanner class for the
desired data feed and call the `get_data` method in a consistent way
(pass the key specifying the data series you want, the fields you
want, and the dates).

## API Keys

Some scanners will require API keys (e.g., FRED) and others may need
API keys if you want to do more than a few requests (e.g., BLS). In
general, you can either pass API keys in to `__init__` for the scanner
or provide in an environemnt variable with a name like
`{NAME}_API_KEY` or in the file `~/.{NAME}_API_KEY` where `{NAME}` is
the name of the scanner class.

# Installation

Install via the usual methods (e.g., `pip install pion`).

# Examples

If you want to write your own scanners, see the examples in the
`pion/simple_scanners` directory. Alternatively, if you want to create
a semi-stand-alone project which depends on `pion` but provides
scanners that one could publish to pypi and install with pip, see the
project in https://github.com/aocks/pion-ts/tree/master/example_extension.
