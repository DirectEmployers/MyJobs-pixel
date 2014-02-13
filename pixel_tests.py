from datetime import datetime, timedelta
import unittest
import uuid

from werkzeug.http import parse_cookie, parse_date

import pixel


class PixelTestCase(unittest.TestCase):
    def setUp(self):
        pixel.app.config['TESTING'] = True
        self.client = pixel.app.test_client()

    def test_aguid_cookie(self):
        response = self.client.get('/pixel.gif')

        # parse_cookie discards the expires portion, which we need to check;
        # split the cookie manually
        aguid, domain, expires, path = response.headers['Set-Cookie'].\
            split('; ')

        # aguid portion should be in the form "aguid="{uuid}";
        # Strip everything not between braces and parse the result as a uuid
        # to check if it is valid
        uuid.UUID(aguid.split('"')[1])

        self.assertTrue(domain.endswith('=.localhost'))

        # These two datetimes are not guaranteed to be exactly equal;
        # if we check the date portion (year, month, day), we can be
        # reasonably certain that the expiration is set correctly
        expiration = parse_date(expires.split('=')[1])
        expected_expiration = datetime.utcnow() + timedelta(days=365)
        self.assertEqual(expiration.date(), expected_expiration.date())

    def test_aguid_cookie_domain(self):
        for host in [('http://localhost', '.localhost'),
                     ('http://track.my.jobs', '.my.jobs'),
                     ('http://this.is.a.long.host.com', '.host.com')]:
            response = self.client.get('/pixel.gif',
                                       base_url=host[0])
            domain = parse_cookie(response.headers['Set-Cookie'])['Domain']
            self.assertEqual(domain, host[1])

    def test_retrieves_pixel(self):
        response = self.client.get('/pixel.gif')
        self.assertEqual(response.headers['Content-Type'], 'image/gif')
        self.assertEqual(response.data, pixel.PIXEL)

    def test_redirect_bad_requests(self):
        for path in ['/', '/admin', '/phpmyadmin/scripts/setup.php']:
            response = self.client.head(path)
            self.assertEqual(response.status_code, 301)
            self.assertEqual(response.headers['Location'],
                             'http://www.my.jobs')

if __name__ == '__main__':
    unittest.main()