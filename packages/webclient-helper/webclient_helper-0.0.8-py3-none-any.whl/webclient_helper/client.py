__all__ = ['WebClient']


import inspect
import input_helper as ih
import webclient_helper as wh


class WebClient(object):
    """Interact with an API on the web

    If you need to obtain a token from a login endpoint, define a "login"
    method when you subclass WebClient and set self._token and self._token_type

    Example:

        def login(self):
            headers = {'Content-Type': 'application/json'}
            data = {'email': self._username, 'password': self._password}
            response = self.session.post(
                self._base_url + '/api/login',
                headers=headers,
                json=data
            )
            self._token = response.json().get('access_token')
            self._token_type = 'Bearer'
    """
    def __init__(self, username=None, password=None, token=None, token_type=None,
                 base_url='', user_agent=None, content_type='application/json',
                 extra_headers={}):
        """

        - username: if specified, set auth on session (requires password)
        - password: if specified, set auth on session (requires username)
        - token: if specified, use this token in the "Authorization" header
          (requires token_type)
        - token_type: if specified, use as part of the value in the
          "Authorization" header
        - base_url: base url for service/API that a subclass would interact with
        - user_agent: if specified, set "User-Agent" header
        - content_type: content type for requests
        - extra_headers: a dict of extra headers to set on the session

        If no login method is defined, any supplied username/password will be
        passed to new_requests_session (for basic auth)
        """
        self._username = username
        self._password = password
        self._token = token
        self._token_type = token_type
        self._base_url = base_url.strip('/')
        self._user_agent = user_agent
        self._content_type = content_type
        self._extra_headers = extra_headers
        self._history = []
        self.set_session()

    def login(self):
        pass

    @property
    def is_login_defined(self):
        """Return True if a login method is defined"""
        return inspect.getsource(self.login) != '    def login(self):\n        pass\n'

    def _set_auth_header(self):
        """Add "Authorization" header on session if self._token is set"""
        if self._token:
            self.session.headers.update({
                'Authorization': '{} {}'.format(self._token_type, self._token)
            })

    def set_session(self):
        """Get a new session object for self.session and invoke login method"""
        if self.is_login_defined:
            self.session = wh.new_requests_session(
                user_agent=self._user_agent,
                content_type=self._content_type,
                extra_headers=self._extra_headers
            )
            self.login()
        else:
            self.session = wh.new_requests_session(
                username=self._username,
                password=self._password,
                user_agent=self._user_agent,
                content_type=self._content_type,
                extra_headers=self._extra_headers
            )
        if self._token:
            assert self._token_type is not None, "self._token is set, but not self._token_type"
        self._set_auth_header()

    def OPTIONS(self, url, headers=None, debug=False, retry=False, **kwargs):
        """Send a OPTIONS request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'options',
            url,
            session=self.session,
            headers=headers,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'options',
                url,
                session=self.session,
                headers=headers,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def HEAD(self, url, headers=None, debug=False, retry=False, **kwargs):
        """Send a HEAD request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'head',
            url,
            session=self.session,
            headers=headers,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'head',
                url,
                session=self.session,
                headers=headers,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def GET(self, url, headers=None, params=None, debug=False, retry=False, **kwargs):
        """Send a GET request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - params: a dict with query string vars and values
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'get',
            url,
            session=self.session,
            headers=headers,
            params=params,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'get',
                url,
                session=self.session,
                headers=headers,
                params=params,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def POST(self, url, headers=None, data=None, json=None, debug=False, retry=False, **kwargs):
        """Send a POST request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - data: a dict to send in the body (non-JSON)
        - json: a dict to send in the body
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'post',
            url,
            session=self.session,
            headers=headers,
            data=data,
            json=json,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'post',
                url,
                session=self.session,
                headers=headers,
                data=data,
                json=json,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def PUT(self, url, headers=None, data=None, debug=False, retry=False, **kwargs):
        """Send a PUT request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - data: a dict to send in the body (non-JSON)
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'put',
            url,
            session=self.session,
            headers=headers,
            data=data,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'put',
                url,
                session=self.session,
                headers=headers,
                data=data,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def PATCH(self, url, headers=None, data=None, debug=False, retry=False, **kwargs):
        """Send a PATCH request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - data: a dict to send in the body (non-JSON)
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'patch',
            url,
            session=self.session,
            headers=headers,
            data=data,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'patch',
                url,
                session=self.session,
                headers=headers,
                data=data,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def DELETE(self, url, headers=None, debug=False, retry=False, **kwargs):
        """Send a DELETE request and return response object

        - url: url/endpoint
        - headers: dict of headers to update on the session before making request
        - debug: if True, enter debugger before returning
        - retry: if True and initial response is "401 Unauthorized", call
          self.set_session() and try again

        Other kwargs are passed to webclient_helper.session_method
        """
        if url.startswith('/') and self._base_url:
            url = self._base_url + url

        response = wh.session_method(
            'delete',
            url,
            session=self.session,
            headers=headers,
            debug=debug,
            **kwargs
        )
        if retry and response.status_code == 401:
            self.set_session()
            response = wh.session_method(
                'delete',
                url,
                session=self.session,
                headers=headers,
                debug=debug,
                **kwargs
            )

        self._history.append({
            'caller': inspect.getouterframes(inspect.currentframe(), 2)[1][3],
            'summary': wh.get_summary_from_response(response),
            'response': response
        })
        return response

    def history_explorer(self, return_selections=False):
        """Select responses from history to explore in ipython (if ipython installed)

        - return_selections: if True, return the selections from history
        """
        selected_responses = ih.make_selections(
            self._history,
            item_format='{summary} (called by {caller})',
            prompt='Select responses to inspect',
            wrap=False,
        )

        if selected_responses:
            ih.start_ipython(warn=True, selected_responses=selected_responses)
            if return_selections:
                return selected_responses
