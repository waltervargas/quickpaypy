"""
   Quickpaypy is a python library for talk with Quickpay.dk merchant

   :copyright: (c) 2014 Walter Vargas <walter@exds.co>
   :license: AGPLv3, see LICENSE for more details

"""

__author__ = "Walter Vargas"
__version__ = "0.0.1"

import httplib2
import urllib
import xml2dict
import hashlib

import pdb

class QuickPayWebServiceError(Exception):
    """Generic QuickPay WebService error class

    To catch these, you need to import it in you code e.g. :
    from quickpaypy import QuickPayWebServiceError
    """

    def __init__(self, msg, error_code=None):
        self.error_code = error_code
        self.msg = msg

    def __str__(self):
        return repr(self.msg)

class QuickPayWebService(object):
    """
    Interacts with QuickPay WebSerice API
    """

    def __init__(self, merchant, secret, api_key):
        """
        Create an instance of QuickPayWebService

        Example:
        from quickpaypy import QuickPayWebService

        quickpay = QuickPayWebService.new(merchant, secret, api_key)

        ...

        @param merchant: The QuickPayId
        @param secret: The MD5 secret code
        @param api_key: The API Key
        @param debug: Debug mode Activated (True) or deactivated (False)
        @param headers: Custom header, is a dict accepted by httplib2
        @param client_args: Dict of extra arguments accepted by httplib2
        """
        self._api_url = 'https://secure.quickpay.dk/api'
        self._api_protocol = '7'

        self.http_client = None

        # required args
        self._api_merchant = merchant
        self._api_secret = secret
        self._api_key = api_key

        # not required args
        self.debug = False
        self.client_args = {}

        # default headers
        self.headers = {
            'User-agent': 'X-QuickPaypy-Client-API-Version: 0.0.1',
            'Accept': 'application/json',
            'Content-type': 'application/x-www-form-urlencoded',
            }

    def _gen_md5_check(self, fields_ord, fields):
        """
        :param fields: A tuple with fields for make md5_check
        :type fields: tuple
        :returns: md5 hexdigest
        """
        str_check = ''
        for field in fields_ord:
            str_check += fields.get(field)

        md5_check = hashlib.md5(str_check).hexdigest()
        return md5_check


    def authorize(self, ordernumber, amount, currency, cardnumber, expirationdate, cvd, testmode=False, autocapture=False):
        """
        Make an authorize action

        Warning !!  You are only allowed to do authorizes through
        the Quickpay API if your setup has passed the full PCI
        certification.  Please use the Quickpay Payment Window
        instead.

        This message type is used when the merchant wants to validate refund card
        data against the card issuer and authorize a transaction. The transaction
        amount is only reserved at the card holder's account and not withdrawn
        from the account - unless the autocapture field is set
        :param ordernumber: A value by merchant's own choise. Must be unique for each transaction.
        :type ordernumber: str
        :param amount: The transaction amount in its smallest unit. In example, 1 EUR is written 100
        :type amount: int
        :param currency: The transaction currency as the 3-letter ISO 4217 alphabetical code.
        :type currency: st
        :param cardnumber: The return efund card number
        :type cardnumber: str
        :param expirationdate: The refund card expiration date (reg exp: /^[0-9]{4}$/ ie. 0914)
        :type expirationdate: str
        :param cvd: The refund card verification data
        :type cvd: str
        :param autocapture: If set to TRUE, the transaction will be captured automatically -
        provided that the authorze was succesful
        :type autocapture: bolean
        :returns: object An object with response fields according to the documentation
        """
        fields = {
            'protocol': self._api_protocol,
            'msgtype': 'authorize',
            'ordernumber': ordernumber,
            'amount': amount,
            'currency': currency,
            'cardnumber': cardnumber,
            'expirationdate': expirationdate,
            'cvd': cvd,
            'autocapture': str(int(autocapture)),
            'merchant': self._api_merchant,
            'apikey': self._api_key,
            'secret': self._api_secret,
            'testmode': str(int(testmode))
            }

        # tuple of fields for calculate md5_check
        fields_ord = (
            'protocol', 'msgtype', 'merchant',
            'ordernumber', 'amount', 'currency',
            'autocapture', 'cardnumber', 'expirationdate',
            'cvd', 'testmode', 'apikey', 'secret')

        md5_check = self._gen_md5_check(fields_ord, fields)

        fields.update({'md5check': md5_check})

        return self._execute(fields)


    def cancel(self, transaction):
        """
        This message type is used when the merchant wants to cancel the order.
        A cancellation will delete the reservation on the cardholders account.

        :param transaction: A transaction id from a previous transaction.
        :type transaction: str
        :returns: An object with response fields according to the documentation
        """

        fields = {
            'msgtype': 'cancel',
            'transaction': transaction
            }

        return self._execute(fields)


    def capture(self, transaction, amount, finalize=False):
        """
        This message type is used when the merchant wants to
        transfer part of or the entire transaction amount from the
        cardholders account.

        :param transaction: A transaction id from a previous transaction.
        :type transaction: str
        :param amount: The transaction amount in its smallest unit.
        In example, 1 EUR is written 100
        :type amount: int
        :param finalize: If set to TRUE, this will finalize multiple partial capture.
        When set transaction will go into a closed state and no more captures will be possible.
        :type finalize: bolean
        """

        fields = {
            'msgtype': 'capture',
            'transaction': transaction,
            'amount': amount,
            'finalize': int(finalize)
            }

        return self._execute(fields)

    def status_from_order(self,transaction):
        """
        This message type is used when the merchant wants to check the status of a transaction. 
        The response from this message type differs from the others as it contains the history 
        of the transaction as well.

        :param transaction: A transaction id from a previous transaction.
        :type transaction: str
        :returns: An object with response fields according to the documentation
        """

        fields = {
            'msgtype': 'status',
            'transaction': transaction,
            }

        return self._execute(fields)

    def _check_status_code(self, status_code, content):
        """
        Take the status code and throw an exception if:
          1. the server didn't return 200 or 201 HTTP code
          2. the server returns a message code != '000'
        :param status_code: status code returned by the server
        :returns: True or raise an exception QuickPayWebServiceError
        """
        message_by_code = {204: 'No content',
                           400: 'Bad Request',
                           401: 'Unauthorized',
                           404: 'Not Found',
                           405: 'Method Not Allowed',
                           500: 'Internal Server Error',}
        error_label = ('QuickPay error: %s %s')
        if status_code in (200, 201):
            content = xml2dict.xml2dict(content)
            res = content.get('response')
            if res.get('qpstat') != '000':
                code = res.get('qpstat')
                message = res.get('qpstatmsg')
                if res.get('chstat'):
                    message += " [" + res['chstat'] + "]: " + res['chstatmsg']
                raise QuickPayWebServiceError(error_label % (code, message))

            return True
            # else:
            #     response_code = payment_response.get('ResponseCode')
            #     description = payment_response.get('ResponseDescription')

            #     raise QuickPayWebServiceError(
            #         error_label % (response_code, description)
            #         )
        elif status_code == 401:
            raise QuickPayWebServiceError(error_label % (status_code, message_by_code[status_code], ''), status_code)
        elif status_code in message_by_code:
            raise QuickPayWebServiceError(error_label % (status_code, message_by_code[status_code], ''), status_code)
    
        
    def _execute(self, fields=None, add_headers=None):
        """
        Execute a request on the QuickPay Webservice

        :param fields: fields that make the request body
        :param add_headers: additional headers
        :return: tuple with (status code, header, content) of the response
        """
        if add_headers is None: add_headers = {}

        if self.http_client is None:
            self.http_client = httplib2.Http(**self.client_args)

        request_headers = self.headers.copy()
        request_headers.update(add_headers)

        params = urllib.urlencode(fields)

        header, content = self.http_client.request(
            self._api_url,
            'POST',
            params,
            request_headers
            )

        status_code = int(header['status'])
        self._check_status_code(status_code, content)
        content = xml2dict.xml2dict(content)
        return content, status_code, header

if __name__ == '__main__':

    from pprint import pprint

    merchant = '89898978'
    secret = '29p61DveBZ79c3144LW61lVz1qrwk2gfAFCxPyi5sn49m3Y3IRK5M6SN5d8a68u7'
    api_key = '3uNkazijf7e49nvA224894FtGIEmS6U31CcYV82519M5w733ypqQ56987T5XlWrD'
    quickpay = QuickPayWebService(merchant, secret, api_key)

    pprint(quickpay.authorize(
        ordernumber='444335566234234',
        amount='100',
        currency='DKK',
        cardnumber='4571000000000001',
        expirationdate='1609',
        cvd='123',
        testmode=True
    ))
