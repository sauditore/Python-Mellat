import datetime
from suds.client import Client

__author__ = 'Saeed Auditore info@auditore.org'
name = 'Mellat API'
identifier = 1
properties = ["userName", "userPassword", "terminalId"]


class BMLPaymentAPI(object):
    def __init__(self, username=None, password=None, terminal_id=None):
        """
        Bank Mellat Payment APIs
        @param username: terminal username
        @param password: terminal password
        @param terminal_id: terminal id (must convert to int)
        @return: None
        """
        if username is None:
            raise Exception('Username is empty')
        if password is None:
            raise Exception('Password is empty')
        if terminal_id is None:
            raise Exception('Terminal ID is empty')
        if not isinstance(terminal_id, int):
            raise Exception('Invalid terminal_id type. int type expected!')
        self.userName = username
        self.userPassword = password
        self.terminalId = terminal_id
        self.service_address = 'https://bpm.shaparak.ir/pgwchannel/services/pgw?wsdl'
        self.payment_address = 'https://bpm.shaparak.ir/pgwchannel/startpay.mellat'
        self.namespace = 'http://interfaces.core.sw.bps.com/'

    @staticmethod
    def __get_local_data__():
        local_date = str(datetime.date.today()).replace('-', '')
        local_time = str(datetime.datetime.now().time()).replace(':', '')[0: 6]
        return local_date, local_time

    def request_pay_ref(self, order_id, price, call_back_address, additional_data=None):
        """
        Request a key for payment
        @param order_id: Invoice Number or a unique int number
        @param price: int price
        @param call_back_address: website callback handler
        @param additional_data: additional data to send. max 100 chars
        @return: True and Ref number to send to client
        """
        if not isinstance(order_id, int):
            raise Exception('Invalid order_id! int type expected')
        if not isinstance(price, int):
            raise Exception('Invalid price! int type expected!')
        if not isinstance(call_back_address, str):
            raise Exception('Invalid call_back_address', 'str type expected')
        if additional_data is not None:
            if not isinstance(additional_data, str):
                raise Exception('Invalid additional_data! str Type expected!')
            if len(additional_data) > 99:
                raise Exception('additional_data is too int. max is 100 chars.')
        else:
            additional_data = ''
        local_date, local_time = self.__get_local_data__()
        try:
            client = Client(self.service_address)
            rid = client.service.bpPayRequest(terminalId=self.terminalId,
                userName=self.userName,
                userPassword=self.userPassword,
                orderId=order_id,
                amount=price,
                localDate=local_date,
                localTime=local_time,
                additionalData=additional_data,
                callBackUrl=call_back_address,
                payerId=0)
            if ',' in rid and rid.partition(',')[0] == '0':
                return rid[2:]
            else:
                print(rid)
                return False
        except Exception as e:
            print(e.message)
            return False

    def verify_payment(self, order_id, ref_id):
        """
        After payment is Done you must call this method to verify it
        @param order_id: order id sent in the payment request method
        @param ref_id: Ref id sent from bank
        @return: True, Ref Number
        """
        try:
            client = Client(self.service_address)
            res = client.service.bpVerifyRequest(terminalId=self.terminalId,
                                         userName=self.userName,
                                         userPassword=self.userPassword,
                                         orderId=order_id,
                                         saleOrderId=order_id,
                                         saleReferenceId=ref_id)
            return True, res
        except Exception as e:
            return False, e.message

    def settle_payment(self, order_id, ref_id):
        try:
            client = Client(self.service_address)
            res = client.service.bpSettleRequest(terminalId=self.terminalId,
                                         userName=self.userName,
                                         userPassword=self.userPassword,
                                         orderId=order_id,
                                         saleOrderId=order_id,
                                         saleReferenceId=ref_id)
            return True, res
        except Exception as e:
            return False, e.message

    def check_state(self, order_id, ref_id):
        if not isinstance(order_id, int):
            raise Exception('Invalid order_id. int type expected!')
        if not isinstance(ref_id, int):
            raise Exception('Invalid ref_id. int type expected!')
        try:
            client = Client(self.service_address)
            res = client.service.bpInquiryRequest(terminalId=self.terminalId,
                                          userName=self.userName,
                                          userPassword=self.userPassword,
                                          orderId=order_id,
                                          saleOrderId=order_id,
                                          saleReferenceId=ref_id)
            return True, res
        except Exception as e:
            return False, e.message

    def undo_payment(self, order_id, ref_id):
        if not isinstance(order_id, int):
            raise Exception('Invalid order_id. int type expected!')
        if not isinstance(ref_id, int):
            raise Exception('Invalid ref_id. int type expected!')
        try:
            client = Client(self.service_address)
            res = client.service.bpReversalRequest(terminalId=self.terminalId,
                                           userName=self.userName,
                                           userPassword=self.userPassword,
                                           orderId=order_id,
                                           saleOrderId=order_id,
                                           saleReferenceId=ref_id)
            return True, res
        except Exception as e:
            return False, e.message

    def get_payment_address(self):
        return self.payment_address
