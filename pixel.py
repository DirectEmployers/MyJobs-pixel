from datetime import datetime, timedelta
from images.images import FAVICON, PIXEL
import uuid

from flask import Flask, make_response, request, redirect

app = Flask(__name__)
app.permanent_session_lifetime = timedelta(days=365)


def add_headers(response, aguid='', myguid=''):
    """
    Adds custom user agent and query string headers, appends aguid and
    myguid cookie values to query string header
    """
    ua = request.headers.get('User-Agent', '-')
    response.headers['X-User-Agent'] = ua.replace(' ', '+')

    qs = request.query_string
    cookie_qs = 'aguid=%s&myguid=%s' % (aguid, myguid)
    if qs:
        qs += '&%s' % cookie_qs
    else:
        qs = cookie_qs
    response.headers['X-Uri-Query'] = qs


def get_cookie_domain():
    """
    Determines the root domain for a domain-wide cookie

    Assumptions:
    - Domain tld is not two-level (.com, not .co.uk)
    - Code is not being accessed via hostname (testing on localhost)

    Outputs:
    :domain: domain for domain-wide cookie
    """
    # Strip out port number and get root domain and TLD
    domain = request.host.split(':')[0].split('.')[-2:]

    # Add dot prefix for domain-wide cookie format
    return '.' + '.'.join(domain)


def update_or_set_cookie(response):
    """
    Determines if there is an aguid or myguid cookie with the current request

    Updates cookie value if it is not valid
    Updates cookie expiration if it already exists and is valid
    Sets a domain-wide aguid cookie if there is not one
    Adds P3P Policy

    Outputs:
    :return_cookies: Dict containing aguid and myguid (if it exists) cookies
    """
    # Add P3P Policy
    response.headers['P3P'] = 'CP="ALL DSP COR CURa IND PHY UNR"'

    expires = datetime.utcnow() + app.permanent_session_lifetime
    domain = get_cookie_domain()

    try:
        # Validate aguid cookie
        aguid = uuid.UUID(request.cookies.get('aguid'))
    except (ValueError, TypeError):
        # Set new aguid value
        aguid = uuid.uuid4()
    finally:
        # Update expiration or set aguid cookie
        response.set_cookie('aguid', aguid.hex,
                            expires=expires, domain=domain)

    return_cookies = {'aguid': aguid.hex}

    try:
        # Validate myguid cookie
        myguid = uuid.UUID(request.cookies.get('myguid'))
    except ValueError:
        # Delete invalid myguid cookie
        response.set_cookie('myguid', '', expires=0, domain=domain)
    except TypeError:
        # Nothing to do since myguid does not exist
        pass
    else:
        # Update myguid cookie expiration
        response.set_cookie('myguid', myguid.hex,
                            expires=expires, domain=domain)
        return_cookies['myguid'] = myguid.hex

    return return_cookies


@app.route("/pixel.gif")
def pixel_gif():
    """
    Returns a tracking pixel with an attached anonymous cookie
    """
    response = make_response(PIXEL)
    response.headers['Content-Type'] = 'image/gif'
    cookies = update_or_set_cookie(response)
    add_headers(response, **cookies)
    return response


@app.route("/favicon.ico")
def favicon_ico():
    """
    Returns a tracking favicon.ico with an attached anonymous cookie
    """
    response = make_response(FAVICON)
    response.headers['Content-Type'] = 'image/x-icon'
    cookies = update_or_set_cookie(response)
    add_headers(response, **cookies)
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
