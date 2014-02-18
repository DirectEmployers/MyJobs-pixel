from datetime import datetime, timedelta
import unittest
import uuid

from werkzeug.http import parse_cookie, parse_date

import pixel


class PixelTestCase(unittest.TestCase):

    def setUp(self):
        pixel.app.testing = True
        self.client = pixel.app.test_client()

    def get_cookie(self, response, cookie_name):
        # Return cookie for cookie name
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            c_key, c_value = cookie.split("; ")[0].split("=")
            if c_key == cookie_name:
                return cookie
        # Cookie not found
        return None

    def get_cookie_value(self, response, cookie_name):
        # Return cookie value for cookie name
        cookie = self.get_cookie(response, cookie_name)
        if cookie:
            c_key, c_value = cookie.split("; ")[0].split("=")
            return c_value
        # Cookie not found
        return None

    def check_cookie(self, response, cookie_name, cookie_value=''):
        # Checks for existence of a cookie and verifies the value of it
        cookies = response.headers.getlist('Set-Cookie')
        for cookie in cookies:
            c_key, c_value = cookie.split("; ")[0].split("=")
            if c_key == cookie_name:
                assert c_value == cookie_value
                return
        # Cookie not found
        assert False

    def test_setting_headers(self):
        """
        Making a request for pixel.gif should set both Set-Cookie and P3P
        headers
        """
        response = self.client.get('/pixel.gif')

        # parse_cookie discards the expires portion, which we need to check;
        # split the cookie manually
        aguid_cookie = self.get_cookie(response, 'aguid').split('; ')
        aguid, domain, expires, path = aguid_cookie

        # aguid portion should be in the form "aguid=uuid";
        # Split on '=' and parse the second part as a uuid
        # to check if it is valid
        uuid.UUID(aguid.split('=')[1])

        self.assertTrue(domain.endswith('=.localhost'))

        # These two datetimes are not guaranteed to be exactly equal;
        # if we check the date portion (year, month, day), we can be
        # reasonably certain that the expiration is set correctly
        expiration = parse_date(expires.split('=')[1])
        expected_expiration = datetime.utcnow() + timedelta(days=365)
        self.assertEqual(expiration.date(), expected_expiration.date())

        self.assertEqual(response.headers['P3P'], 'CP="ALL DSP COR CURa IND PHY UNR"')

    def test_aguid_cookie_domain(self):
        for host in [('http://localhost', '.localhost'),
                     ('http://track.my.jobs', '.my.jobs'),
                     ('http://this.is.a.long.host.com', '.host.com')]:
            response = self.client.get('/pixel.gif',
                                       base_url=host[0])
            domain = parse_cookie(response.headers['Set-Cookie'])['Domain']
            self.assertEqual(domain, host[1])

    def test_get_pixel(self):
        response = self.client.get('/pixel.gif')
        self.assertEqual(response.headers['Content-Type'], 'image/gif')
        self.assertEqual(response.headers['P3P'], 'CP="ALL DSP COR CURa IND PHY UNR"')
        self.assertEqual(response.data, pixel.PIXEL)

    def test_get_favicon(self):
        response = self.client.get('/favicon.ico')
        self.assertEqual(response.headers['Content-Type'], 'image/x-icon')
        self.assertEqual(response.headers['P3P'], 'CP="ALL DSP COR CURa IND PHY UNR"')
        self.assertEqual(response.data, pixel.FAVICON)

    def test_redirect_bad_requests(self):
        for path in ['/', '/admin', '/phpmyadmin/scripts/setup.php']:
            response = self.client.head(path)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['Location'],
                             'http://www.my.jobs%s' % path)

    def test_aguid_valid_cookie(self):
        """
        Tests that a valid aguid cookie is not replaced
        """
        self.client.set_cookie('localhost', 'aguid',
                               '83259f2911124311ab03b5bae64e7c73')

        cookie = [cookie for cookie in self.client.cookie_jar
                  if cookie.name == 'aguid'][0]

        # Prove aguid cookie is valid
        uuid.UUID(cookie.value)

        response = self.client.get('/pixel.gif')
        self.check_cookie(response, 'aguid',
                                    '83259f2911124311ab03b5bae64e7c73')

    def test_aguid_invalid_cookie(self):
        """
        Tests that an invalid aguid cookie is replaced with a valid cookie
        """
        self.client.set_cookie('localhost', 'aguid', 'notavalidaguid')

        cookie = [cookie for cookie in self.client.cookie_jar
                  if cookie.name == 'aguid'][0]

        with self.assertRaises(ValueError):
            uuid.UUID(cookie.value)

        response = self.client.get('/pixel.gif')
        uuid.UUID(self.get_cookie_value(response, 'aguid'))

    def test_myguid_valid_cookie(self):
        """
        Tests that a valid myguid cookie is not replaced
        """
        self.client.set_cookie('localhost', 'myguid',
                               '12349f2911124311ab03b5bae64e7c73')

        cookie = [cookie for cookie in self.client.cookie_jar
                  if cookie.name == 'myguid'][0]

        # Prove myguid cookie is valid
        uuid.UUID(cookie.value)

        response = self.client.get('/pixel.gif')
        self.check_cookie(response, 'myguid',
                                    '12349f2911124311ab03b5bae64e7c73')

    def test_myguid_invalid_cookie(self):
        """
        Tests that an invalid myguid cookie is deleted
        """
        self.client.set_cookie('localhost', 'myguid', 'notavalidaguid')

        cookie = [cookie for cookie in self.client.cookie_jar
                  if cookie.name == 'myguid'][0]

        with self.assertRaises(ValueError):
            uuid.UUID(cookie.value)

        response = self.client.get('/pixel.gif')

        # Assert cookie not found
        self.assertFalse(self.check_cookie(response, 'myguid'))

if __name__ == '__main__':
    unittest.main()
