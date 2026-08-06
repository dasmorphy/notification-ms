# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.generic_response import GenericResponse  # noqa: E501
from swagger_server.models.request_push_notification import RequestPushNotification  # noqa: E501
from swagger_server.models.response_error import ResponseError  # noqa: E501
from swagger_server.test import BaseTestCase


class TestFirebaseController(BaseTestCase):
    """FirebaseController integration test stubs"""

    def test_send_push_notification(self):
        """Test case for send_push_notification

        Envia una notificacion push
        """
        body = RequestPushNotification()
        response = self.client.open(
            '/send-push-notification',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
