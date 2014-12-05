Quickpaypy
=========

quickpaypy is a library for Python to interact with QuickPay Web Service API.

Learn more about the QuickPay Web Service from http://doc.quickpay.dk/api.html

Installation
============

The easiest way to install quickpaypy (needs setuptools):

    easy_install quickpaypy

Or, better, using pip:

    pip install quickpaypy

If you do not have setuptools, download as a .tar.gz or .zip from
https://github.com/waltervargas/quickpaypy/archive/master.zip, unzip it and
run:

    python setup.py install


Usage
=====

    from quickpaypy import QuickPayWebServiceError, QuickPayWebService
    import random

    ordernumber = random.randrange(100000090, 1200000000)

    merchant = '89898978'
    secret = '29p61DveBZ79c3144LW61lVz1qrwk2gfAFCxPyi5sn49m3Y3IRK5M6SN5d8a68u7'
    api_key = '3uNkazijf7e49nvA224894FtGIEmS6U31CcYV82519M5w733ypqQ56987T5XlWrD'

    quickpay = QuickPayWebService(merchant, secret, api_key)

    # make authorize for 1 DKK
    resp = quickpay.authorize(
        ordernumber,
        amount='100',
        currency='DKK',
        cardnumber='4571000000000001',
        expirationdate='1609',
        cvd='123',
        testmode=True
    )

    pdb.set_trace()
    transaction = resp.get('content').get('transaction')

    quickpay.capture(transaction, '025')
    quickpay.capture(transaction, '025')
    quickpay.capture(transaction, '025')
    quickpay.capture(transaction, '025')
    resp = quickpay.status_from_transaction(transaction)
    pprint(resp)


Credits
========

Thanks to [Guewen Baconnier], this lib is based on prestapyt lib.

Copyright and License
=====================

quickpaypy is copyright (c) 2014 Walter Vargas

quickpaypy is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

quickpaypy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with quickpaypy. If not, see [GNU licenses](http://www.gnu.org/licenses/).

[Guewen Baconnier]: https://github.com/guewen