Unsupported opcode: DICT_MERGE (213)
# Source Generated with Decompyle++
# File: sessions.pyc (Python 3.10)

'''
requests.sessions
~~~~~~~~~~~~~~~~~

This module provides a Session object to manage and persist settings across
requests (cookies, auth, proxies).
'''
import os
import sys
import time
from collections import OrderedDict
from datetime import timedelta
from _internal_utils import to_native_string
from adapters import HTTPAdapter
from auth import _basic_auth_str
from compat import Mapping, cookielib, urljoin, urlparse
from cookies import RequestsCookieJar, cookiejar_from_dict, extract_cookies_to_jar, merge_cookies
from exceptions import ChunkedEncodingError, ContentDecodingError, InvalidSchema, TooManyRedirects
from hooks import default_hooks, dispatch_hook
from models import DEFAULT_REDIRECT_LIMIT, REDIRECT_STATI, PreparedRequest, Request
from status_codes import codes
from structures import CaseInsensitiveDict
from utils import DEFAULT_PORTS, default_headers, get_auth_from_url, get_environ_proxies, get_netrc_auth, requote_uri, resolve_proxies, rewind_body, should_bypass_proxies, to_key_val_list
if sys.platform == 'win32':
    preferred_clock = time.perf_counter
else:
    preferred_clock = time.time

def merge_setting(request_setting, session_setting, dict_class = (OrderedDict,)):
    '''Determines appropriate setting for a given request, taking into account
    the explicit setting on that request, and the setting in the session. If a
    setting is a dictionary, they will be merged together using `dict_class`
    '''
    if session_setting is None:
        return request_setting
    if None is None:
        return session_setting
    if not None(session_setting, Mapping) or isinstance(request_setting, Mapping):
        return request_setting
    merged_setting = None(to_key_val_list(session_setting))
    merged_setting.update(to_key_val_list(request_setting))
    none_keys = (lambda .0: [ k for k, v in .0 if v is None ])(merged_setting.items())
    for key in none_keys:
        del merged_setting[key]
    return merged_setting


def merge_hooks(request_hooks, session_hooks, dict_class = (OrderedDict,)):
    """Properly merges both requests and session hooks.

    This is necessary because when request_hooks == {'response': []}, the
    merge breaks Session hooks entirely.
    """
    if session_hooks is None or session_hooks.get('response') == []:
        return request_hooks
    if None is None or request_hooks.get('response') == []:
        return session_hooks
    return None(request_hooks, session_hooks, dict_class)


class SessionRedirectMixin:
    
    def get_redirect_target(self, resp):
        '''Receives a Response. Returns a redirect URI or ``None``'''
        if resp.is_redirect:
            location = resp.headers['location']
            location = location.encode('latin1')
            return to_native_string(location, 'utf8')

    
    def should_strip_auth(self, old_url, new_url):
        '''Decide whether Authorization header should be removed when redirecting'''
        old_parsed = urlparse(old_url)
        new_parsed = urlparse(new_url)
        if old_parsed.hostname != new_parsed.hostname:
            return True
        if None.scheme == 'http' and old_parsed.port in (80, None) and new_parsed.scheme == 'https' and new_parsed.port in (443, None):
            return False
        changed_port = None.port != new_parsed.port
        changed_scheme = old_parsed.scheme != new_parsed.scheme
        default_port = (DEFAULT_PORTS.get(old_parsed.scheme, None), None)
        if changed_scheme and old_parsed.port in default_port and new_parsed.port in default_port:
            return False
        if not None:
            pass
        return changed_scheme

    
    def resolve_redirects(self, resp, req, stream, timeout, verify, cert, proxies, yield_requests = (False, None, True, None, None, False), **adapter_kwargs):
        '''Receives a Response. Returns a generator of Responses or Requests.'''
        hist = []
        url = self.get_redirect_target(resp)
        previous_fragment = urlparse(req.url).fragment
    # WARNING: Decompyle incomplete

    
    def rebuild_auth(self, prepared_request, response):
        '''When being redirected we may want to strip authentication from the
        request to avoid leaking credentials. This method intelligently removes
        and reapplies authentication where possible to avoid credential loss.
        '''
        headers = prepared_request.headers
        url = prepared_request.url
        if 'Authorization' in headers and self.should_strip_auth(response.request.url, url):
            del headers['Authorization']
        new_auth = get_netrc_auth(url) if self.trust_env else None
        if new_auth is not None:
            prepared_request.prepare_auth(new_auth)
            return None

    
    def rebuild_proxies(self, prepared_request, proxies):
        '''This method re-evaluates the proxy configuration by considering the
        environment variables. If we are redirected to a URL covered by
        NO_PROXY, we strip the proxy configuration. Otherwise, we set missing
        proxy keys for this URL (in case they were stripped by a previous
        redirect).

        This method also replaces the Proxy-Authorization header where
        necessary.

        :rtype: dict
        '''
        headers = prepared_request.headers
        scheme = urlparse(prepared_request.url).scheme
        new_proxies = resolve_proxies(prepared_request, proxies, self.trust_env)
        if 'Proxy-Authorization' in headers:
            del headers['Proxy-Authorization']
        
        try:
            (username, password) = get_auth_from_url(new_proxies[scheme])
        finally:
            pass
        (username, password) = (None, None)
        if scheme.startswith('https') and username and password:
            headers['Proxy-Authorization'] = _basic_auth_str(username, password)

        return new_proxies

    
    def rebuild_method(self, prepared_request, response):
        '''When being redirected we may want to change the method of the request
        based on certain specs or browser behavior.
        '''
        method = prepared_request.method
        if response.status_code == codes.see_other and method != 'HEAD':
            method = 'GET'
        if response.status_code == codes.found and method != 'HEAD':
            method = 'GET'
        if response.status_code == codes.moved and method == 'POST':
            method = 'GET'
        prepared_request.method = method



class Session(SessionRedirectMixin):
    """A Requests session.

    Provides cookie persistence, connection-pooling, and configuration.

    Basic Usage::

      >>> import requests
      >>> s = requests.Session()
      >>> s.get('https://httpbin.org/get')
      <Response [200]>

    Or as a context manager::

      >>> with requests.Session() as s:
      ...     s.get('https://httpbin.org/get')
      <Response [200]>
    """
    __attrs__ = [
        'headers',
        'cookies',
        'auth',
        'proxies',
        'hooks',
        'params',
        'verify',
        'cert',
        'adapters',
        'stream',
        'trust_env',
        'max_redirects']
    
    def __init__(self):
        self.headers = default_headers()
        self.auth = None
        self.proxies = { }
        self.hooks = default_hooks()
        self.params = { }
        self.stream = False
        self.verify = True
        self.cert = None
        self.max_redirects = DEFAULT_REDIRECT_LIMIT
        self.trust_env = True
        self.cookies = cookiejar_from_dict({ })
        self.adapters = OrderedDict()
        self.mount('https://', HTTPAdapter())
        self.mount('http://', HTTPAdapter())

    
    def __enter__(self):
        return self

    
    def __exit__(self, *args):
        self.close()

    
    def prepare_request(self, request):
        """Constructs a :class:`PreparedRequest <PreparedRequest>` for
        transmission and returns it. The :class:`PreparedRequest` has settings
        merged from the :class:`Request <Request>` instance and those of the
        :class:`Session`.

        :param request: :class:`Request` instance to prepareUnsupported opcode: DICT_MERGE (213)
 with this
            session's settings.
        :rtype: requests.PreparedRequest
        """
        if not request.cookies:
            pass
        cookies = { }
        if not isinstance(cookies, cookielib.CookieJar):
            cookies = cookiejar_from_dict(cookies)
        merged_cookies = merge_cookies(merge_cookies(RequestsCookieJar(), self.cookies), cookies)
        auth = request.auth
        if not self.trust_env and auth and self.auth:
            auth = get_netrc_auth(request.url)
        p = PreparedRequest()
        p.prepare(request.method.upper(), request.url, request.files, request.data, request.json, merge_setting(request.headers, self.headers, CaseInsensitiveDict, **('dict_class',)), merge_setting(request.params, self.params), merge_setting(auth, self.auth), merged_cookies, merge_hooks(request.hooks, self.hooks), **('method', 'url', 'files', 'data', 'json', 'headers', 'params', 'auth', 'cookies', 'hooks'))
        return p

    
    def request(self, method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects, proxies, hooks, stream, verify, cert, json = (None, None, None, None, None, None, None, True, None, None, None, None, None, None)):
        """Constructs a :class:`Request <Request>`, prepares it and sends it.
        Returns :class:`Response <Response>` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query
            string for the :class:`Request`.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the
            :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the
            :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the
            :class:`Request`.
        :param files: (optional) Dictionary of ``'filename': file-like-objects``
            for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable
            Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How many seconds to wait for the server to send
            data before giving up, as a float, or a :ref:`(connect timeout,
            read timeout) <timeouts>` tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol or protocol and
            hostname to the URL of the proxy.
        :param hooks: (optional) Dictionary mapping hook name to one event or
            list of events, event must be callable.
        :param stream: (optional) whether to immediately download the response
            content. Defaults to ``False``.
        :param verify: (optional) Either a boolean, in which case it controls whether we verify
            the server's TLS certificate, or a string, in which case it must be a path
            to a CA bundle to use. Defaults to ``True``. When set to
            ``False``, requests will accept any TLS certificate presented by
            the server, and will ignore hostname mismatches and/or expired
            certificates, which will make your application vulnerable to
            man-in-the-middle (MitM) attacks. Setting verify to ``False``
            may be useful during local development or testing.
        :param cert: (optional) if String, path to ssl client cert file (.pem).
            If Tuple, ('cert', 'key') pair.
        :rtype: requests.Response
        """
        if not data:
            pass
        if not params:
            pass
        req = Request(method.upper(), url, headers, files, { }, json, { }, auth, cookies, hooks, **('method', 'url', 'headers', 'files', 'data', 'json', 'params', 'auth', 'cookies', 'hooks'))
        prep = self.prepare_request(req)
     Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
Unsupported opcode: DICT_MERGE (213)
   if not proxies:
            pass
        proxies = { }
        settings = self.merge_environment_settings(prep.url, proxies, stream, verify, cert)
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects }
        send_kwargs.update(settings)
    # WARNING: Decompyle incomplete

    
    def get(self, url, **kwargs):
        '''Sends a GET request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        kwargs.setdefault('allow_redirects', True)
    # WARNING: Decompyle incomplete

    
    def options(self, url, **kwargs):
        '''Sends a OPTIONS request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        kwargs.setdefault('allow_redirects', True)
    # WARNING: Decompyle incomplete

    
    def head(self, url, **kwargs):
        '''Sends a HEAD request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        kwargs.setdefault('allow_redirects', False)
    # WARNING: Decompyle incomplete

    
    def post(self, url, data, json = (None, None), **kwargs):
        '''Sends a POST request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param json: (optional) json to send in the body of the :class:`Request`.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def put(self, url, data = (None,), **kwargs):
        '''Sends a PUT request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def patch(self, url, data = (None,), **kwargs):
        '''Sends a PATCH request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param data: (optional) Dictionary, list of tuples, bytes, or file-like
            object to send in the body of the :class:`Request`.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def delete(self, url, **kwargs):
        '''Sends a DELETE request. Returns :class:`Response` object.

        :param url: URL for the new :class:`Request` object.
        :param \\*\\*kwargs: Optional arguments that ``request`` takes.
        :rtype: requests.Response
        '''
        pass
    # WARNING: Decompyle incomplete

    
    def send(self, request, **kwargs):
        '''Send a given PreparedRequest.

        :rtype: requests.Response
        '''
        kwargs.setdefault('stream', self.stream)
        kwargs.setdefault('verify', self.verify)
        kwargs.setdefault('cert', self.cert)
        if 'proxies' not in kwargs:
            kwargs['proxies'] = resolve_proxies(request, self.proxies, self.trust_env)
        if isinstance(request, Request):
            raise ValueError('You can only send PreparedRequests.')
        allow_redirects = kwargs.pop('allow_redirects', True)
        stream = kwargs.get('stream')
        hooks = request.hooks
        adapter = self.get_adapter(request.url, **('url',))
        start =Warning: block stack is not empty!
Unsupported opcode: MAP_ADD (188)
 preferred_clock()
    # WARNING: Decompyle incomplete

    
    def merge_environment_settings(self, url, proxies, stream, verify, cert):
        '''
        Check the environment and merge it with some settings.

        :rtype: dict
        '''
        if self.trust_env:
            no_proxy = proxies.get('no_proxy') if proxies is not None else None
            env_proxies = get_environ_proxies(url, no_proxy, **('no_proxy',))
            for k, v in env_proxies.items():
                proxies.setdefault(k, v)
            if verify is True or verify is None:
                if not os.environ.get('REQUESTS_CA_BUNDLE') and os.environ.get('CURL_CA_BUNDLE'):
                    pass
                verify = verify
        proxies = merge_setting(proxies, self.proxies)
        stream = merge_setting(stream, self.stream)
        verify = merge_setting(verify, self.verify)
        cert = merge_setting(cert, self.cert)
        return {
            'proxies': proxies,
            'stream': stream,
            'verify': verify,
            'cert': cert }

    
    def get_adapter(self, url):
        '''
        Returns the appropriate connection adapter for the given URL.

        :rtype: requests.adapters.BaseAdapter
        '''
        for prefix, adapter in self.adapters.items():
            if url.lower().startswith(prefix.lower()):
                return adapter
            raise InvalidSchema(f'''No connection adapters were found for {url!r}''')

    
    def close(self):
        '''Closes all adapters and as such the session'''
        for v in self.adapters.values():
            v.close()

    
    def mount(self, prefix, adapter):
        '''Registers a connection adapter to a prefix.

        Adapters are sorted in descending order by prefix length.
        '''
        self.adapters[prefix] = adapter
        keys_to_move = (lambda .0 = None: [ k for k in .0 if len(k) < len(prefix) ])(self.adapters)
        for key in keys_to_move:
            self.adapters[key] = self.adapters.pop(key)

    
    def __getstate__(self):
        state = (lambda .0 = None: pass# WARNING: Decompyle incomplete
)(self.__attrs__)
        return state

    
    def __setstate__(self, state):
        for attr, value in state.items():
            setattr(self, attr, value)



def session():
    '''
    Returns a :class:`Session` for context-management.

    .. deprecated:: 1.0.0

        This method has been deprecated since version 1.0.0 and is only kept for
        backwards compatibility. New code should use :class:`~requests.sessions.Session`
        to create a session. This may be removed at a future date.

    :rtype: Session
    '''
    return Session()

