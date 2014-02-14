from datetime import datetime, timedelta
import uuid

from flask import Flask, make_response, request, redirect

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=365)

PIXEL = "\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff" + \
        "\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00" + \
        "\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"


def get_cookie_domain(host):
    """
    Sets a domain-wide cookie for the current domain

    Assumptions:
    - Domain tld is not two-level (.com, not .co.uk)
    - Code is not being accessed via hostname (testing on localhost)

    Inputs:
    :host: Address that this project was accessed through

    Outputs:
    :host: Trimmed version of input :host: suitable as a domain-wide cookie
    """
    # Strip out port number, if any (likely on localhost)
    host = host.split(':')[0]

    # According to assumptions, these must be domain and tld
    host = host.split('.')[-2:]

    return '.' + '.'.join(host)


@app.route("/pixel.gif")
def return_gif():
    """
    Returns a tracking pixel with an attached anonymous cookie
    """
    response = make_response(PIXEL)
    response.headers['Content-Type'] = 'image/gif'
    aguid = request.cookies.get('aguid') or '{%s}' % (uuid.uuid4(),)

    host = request.host
    host = get_cookie_domain(host)

    expires = datetime.utcnow() + app.permanent_session_lifetime
    response.set_cookie('aguid', aguid,
                        expires=expires,
                        domain=host)

    return response


@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def redirect_all(path):
    """
    Redirects all requests not for pixel.gif to www.my.jobs, keeping the
    requested path
    """
    return redirect("http://www.my.jobs/%s" % path, code=301)


if __name__ == "__main__":
    app.run()