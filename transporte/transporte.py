#! /usr/bin/env python

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_qrcode import QRcode

from . import create_app

app = create_app()

limiter = Limiter(app, key_func=get_remote_address)

QRcode(app)

if app.config['DEBUG']:
    import logging
    import http.client

    http.client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


if __name__ == '__main__':
    app.run('0.0.0.0', debug=app.config['DEBUG'])
