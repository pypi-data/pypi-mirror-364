import fs_helper as fh
import requests
import time
import warnings
from json import JSONDecodeError
from urllib.parse import urlparse
try:
    ModuleNotFoundError
except NameError:
    class ModuleNotFoundError(ImportError):
        pass

try:
    from bs4 import BeautifulSoup, FeatureNotFound
    import os.path
except (ImportError, ModuleNotFoundError):
    BeautifulSoup = None


logger = fh.get_logger(__name__)


def get_domain(url):
    """Return the domain of a url"""
    return urlparse(url).netloc.replace('www.', '')


def new_requests_session(username=None, password=None, user_agent=None,
                         content_type=None, extra_headers={}):
    """Return a new requests Session object

    - username: if specified, set auth on session (requires password)
    - password: if specified, set auth on session (requires username)
    - user_agent: if specified, set "User-Agent" header on session
    - content_type: if specified, set "Content-Type" header on session
    - extra_headers: a dict of extra_headers to set on the session

    Both username and password required to set auth (for basic auth)
    """
    if username and not password:
        raise Exception('You must specify a password if passing a username')
    elif password and not username:
        raise Exception('You must specify a username if passing a password')
    session = requests.Session()
    if user_agent:
        extra_headers['User-Agent'] = user_agent
    if content_type:
        extra_headers['Content-Type'] = content_type
    if username and password:
        session.auth = (username, password)
    session.headers.update(extra_headers)
    logger.debug('New session created')
    return session


def get_summary_from_response(response):
    """Return a string of info from a response object"""
    message_parts = [
        str(response.status_code),
        response.request.method,
        response.request.url,
        'in {} seconds'.format(response.elapsed.total_seconds()),
    ]
    return ' '.join(message_parts)


def session_method(method, url, session=None, headers=None, debug=False, **kwargs):
    """Send a request and return response object

    - method: options, head, get, post, put, patch, delete
    - url: url/endpoint
    - session: a session object
    - headers: dict of headers to update on the session before making request
    - debug: if True, enter debugger before returning
    - kwargs: any additional optional kwargs that requests.Session.request takes
        - params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        - data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        - json: (optional) json to send in the body of the
            :class:`Request`.
        - cookies: (optional) Dict or CookieJar object to send with the
            :class:`Request`.
        - files: (optional) Dictionary of ``'filename': file-like-objects``
            for multipart encoding upload.
        - auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        - timeout: (optional) How long to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        - allow_redirects: (optional) Set to True by default.
        - proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        - stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        - verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        - cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
    """
    session = session or new_requests_session()
    if headers:
        session.headers.update(headers)
    try:
        response = session.request(method, url, **kwargs)
    except Exception as err:
        logger.error('Could not access {} ... {}'.format(repr(url), repr(err)))
        if debug == True:
            import pdb; pdb.set_trace()
            print('See "method", "session"')
        return
    logger.debug(get_summary_from_response(response))
    if debug == True:
        import pdb; pdb.set_trace()
        print('See "response"')
    return response


def get_soup(url_file_or_string, xml=False, session=None, warn=True):
    """Fetch url (or open a file, or read string) and return a BeautifulSoup object (or None)

    - url_file_or_string: a string that is either a url to fetch, a file to read,
      or a string containing HTML/XML content
        - may also be bytes that are utf-8 encoded
    - xml: if True, parse content as XML instead of HTML (requires lxml)
    - session: a session object
    - warn: if True, issue a warning if bs4 package is not installed
    """
    if BeautifulSoup is None:
        if warn:
            warnings.warn('The "beautifulsoup4" package is not installed!')
        return
    first_ten_chars = url_file_or_string[:10]
    try:
        first_ten_chars = first_ten_chars.decode('utf-8')
    except AttributeError:
        pass
    markup = ''
    if os.path.isfile(url_file_or_string):
        with open(url_file_or_string, 'r') as fp:
            markup = fp.read()
    elif '://' in first_ten_chars:
        resp = session_method('get', url_file_or_string, session)
        markup = resp.content
    else:
        markup = url_file_or_string

    if markup:
        if xml:
            try:
                return BeautifulSoup(markup, 'lxml-xml')
            except FeatureNotFound:
                return BeautifulSoup(markup)
        else:
            try:
                return BeautifulSoup(markup, 'lxml')
            except FeatureNotFound:
                return BeautifulSoup(markup)


def download_file(url, localfile='', session=None):
    """Download file using `requests` with stream enabled

    - url: a string
    - localfile: a string
    - session: a session object

    See: http://stackoverflow.com/questions/16694907/
    """
    session = session or new_requests_session()
    localfile = localfile or fh.lazy_filename(url)

    for sleeptime in [5, 10, 30, 60]:
        try:
            logger.info('Saving {} to {}'.format(repr(url), repr(localfile)))
            r = session_method('get', url, stream=True)
            with open(localfile, 'wb') as fp:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        fp.write(chunk)
                        fp.flush()

            break
        except Exception as e:
            logger.error('{}... sleeping for {} seconds'.format(repr(e), sleeptime))
            session.close()
            time.sleep(sleeptime)
            session = new_requests_session()


from .client import *
