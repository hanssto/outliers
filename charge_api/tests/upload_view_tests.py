from StringIO import StringIO

from unittest import TestCase

import mock

from charge_api import app
from charge_api.views import CHARGES_FILENAME


@mock.patch("charge_api.views.process_charge_list")
class UploadViewTestCase(TestCase):

    def setUp(self):

        self.client = app.test_client()
        self.url = "/upload"

        self.base_args = {
            "data": {
                "charges_file": (StringIO("[]"), "foo.json"),
            },
            "headers": {
              "Content-Type": "multipart/form-data",
            },
        }

    def test_no_file_returns_400(self, process_mock):

        del self.base_args["data"]
        res = self.client.post(self.url, **self.base_args)
        self.assertEqual(res.status_code, 400)
        self.assertIn("No '%s' passed." % CHARGES_FILENAME, res.data)
        self.assertFalse(process_mock.called)

    def test_invalid_json_returns_400(self, process_mock):

        file_data = (StringIO("[{]}"), "foo.json")
        self.base_args["data"][CHARGES_FILENAME] = file_data
        res = self.client.post(self.url, **self.base_args)
        self.assertEqual(res.status_code, 400)
        self.assertIn("Invalid JSON data.", res.data)
        self.assertFalse(process_mock.called)

    def test_invalid_data_returns_400(self, process_mock):

        # Data isn't validated yet.
        self.fail()

    def test_valid_data_returns_redirect(self, process_mock):

        process_mock.return_value = ([], [])
        res = self.client.post(self.url, **self.base_args)
        process_mock.assert_called_once_with([])
        self.assertEqual(res.status_code, 302)
