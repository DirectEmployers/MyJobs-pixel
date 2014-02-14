from datetime import datetime, timedelta
from images.images import FAVICON, PIXEL
import uuid

from flask import Flask, make_response, request, redirect

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=365)

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


def check_or_set_cookie(request, response):
    """
    Validate existing cookie or set new cookie
    """
    try:
        uuid.UUID(request.cookies.get('aguid'))
    except:
        domain = get_cookie_domain(request.host)
        expires = datetime.utcnow() + app.permanent_session_lifetime
        response.set_cookie('aguid', str(uuid.uuid4()),
                            expires=expires,
                            domain=domain)


@app.route("/pixel.gif")
def pixel_gif():
    """
    Returns a tracking pixel with an attached anonymous cookie
    """
    response = make_response(PIXEL)
    response.headers['Content-Type'] = 'image/gif'
    check_or_set_cookie(request, response)
    return response


@app.route("/favicon.ico")
def favicon_ico():
    """
    Returns a tracking favicon.ico with an attached anonymous cookie
    """
    response = make_response(FAVICON)
    response.headers['Content-Type'] = 'image/x-icon'
    check_or_set_cookie(request, response)
    return response


@app.route("/", defaults={'path': ''})
@app.route("/<path:path>")
def redirect_all(path):
    """
    Redirects all other requests to www.my.jobs,
    keeping the requested path
    """
    return redirect("http://www.my.jobs/%s" % path, code=301)


if __name__ == "__main__":
    app.run()
