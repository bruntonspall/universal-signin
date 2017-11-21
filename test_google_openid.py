import unittest
import google_openid
import collections

class TestGoogleClient(unittest.TestCase):
    def test_isGoogleDomain(self):
        App = collections.namedtuple('App', 'config')
        app = App({"CLIENT_ID":"", "CLIENT_SECRET":""})
        client = google_openid.OpenIdConnectClient(app)

        self.assertTrue(client.detectGoogleSuite("brunton-spall.co.uk"))
        self.assertFalse(client.detectGoogleSuite("microsoft.com"))
