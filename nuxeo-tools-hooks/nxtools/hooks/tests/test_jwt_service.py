import flask
from flask.helpers import make_response
from jwt.exceptions import DecodeError
from mock.mock import patch
from nxtools import services
from nxtools.hooks.services.jwt_service import JwtService
from nxtools.hooks.tests import HooksTestCase


class JwtServiceTest(HooksTestCase):

    ACCESS_TOKEN = 'some_access_token'

    @property
    def app(self):
        return flask.Flask(__name__)

    def testJwtDecode(self):
        headers = {'Cookie': 'access_token=' + JwtServiceTest.ACCESS_TOKEN}

        with patch("jwt.decode", self.mocks.jwt_error), self.app.test_request_context(headers=headers):
            self.mocks.jwt_error.side_effect = DecodeError()
            self.assertFalse(services.get(JwtService).has_jwt())
            self.assertTrue(self.mocks.jwt_error.called)

        with patch("jwt.decode", self.mocks.jwt_decode), self.app.test_request_context(headers=headers):
            self.mocks.jwt_decode.return_value = {}
            self.assertTrue(services.get(JwtService).has_jwt())

    def testJwtEncode(self):
        with self.app.test_request_context(), patch("jwt.encode", self.mocks.jwt_encode):
            services.get(JwtService).encode()
            self.assertTrue(self.mocks.jwt_encode.called)

    def testOAuthValidate(self):
        jwt_service = services.get(JwtService)

        with self.app.test_request_context():
            self.assertFalse(jwt_service.has_jwt())
            jwt_service.set('gat', JwtServiceTest.ACCESS_TOKEN)

            self.assertTrue(jwt_service.has_jwt())
            self.assertEqual(JwtServiceTest.ACCESS_TOKEN, jwt_service.get('gat'))

    def testUpdateJwt(self):
        self.mocks.jwt_encode.return_value = JwtServiceTest.ACCESS_TOKEN
        with self.app.test_request_context(), patch("jwt.encode", self.mocks.jwt_encode):
            @JwtService.update_cookie
            def fake_controller():
                return make_response()

            response = self.app.process_response(fake_controller())

            cookie = u'access_token=some_access_token; HttpOnly; Path=/'

            for header in response.headers:
                key, value = header
                if 'Set-Cookie' == key and cookie in value:
                    return

            self.fail('Cannot find %s in %s' % (cookie, response.headers))