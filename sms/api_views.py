__author__ = 'mukhar ranjan'

from django.http import HttpResponse
from rest_framework import status
from rest_framework.viewsets import ViewSet
from sms.util import send_message

class SendSms(ViewSet):
    """
    Api for sending sms
    """

    def send_sms(self, request):
        """
        This method will be used for storing the feedback data.
        :param request: Http request
        :return: Success/Failure in response
        """
        import pdb;pdb.set_trace()
        number_list = request.data.get('numbers')
        message = request.data.get('message')

        try:
            send_message(number_list, message)
            return HttpResponse("Sent", status.HTTP_200_OK)
        except Exception,e:
            return HttpResponse("Error", status.HTTP_503_SERVICE_UNAVAILABLE)

