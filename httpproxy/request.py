from __future__ import unicode_literals

import flask
import werkzeug.exceptions
import werkzeug.http
import werkzeug.datastructures
import werkzeug.utils

exc = werkzeug.exceptions


class RequestTraceMixin(object):

    @werkzeug.utils.cached_property
    def trace_id(self):
        return flask.current_app.tracer.id


class RequestProxyMixin(object):

    @werkzeug.utils.cached_property
    def proxy_authorization(self):
        header = self.environ.get('HTTP_PROXY_AUTHORIZATION')
        value = werkzeug.http.parse_authorization_header(header)
        if isinstance(value, tuple):
            username, password = value
            value = werkzeug.datastructures.Authorization('Basic', {
                'username': username,
                'password': password,
            })
        return value

    @werkzeug.utils.cached_property
    def has_proxy(self):
        try:
            self.proxy
        except exc.HTTPException:
            return False
        return True

    @werkzeug.utils.cached_property
    def proxy(self):
        factory = flask.current_app.config['HTTP_PROXY_FACTORY']
        proxy = factory(self)
        return proxy


class ProxyRequest(
    RequestTraceMixin,
    RequestProxyMixin,
    flask.Request,
):
    @property
    def want_form_data_parsed(self):
        # Notice: we do not want the reuqest body get parsed, otherwise, the
        # request.data will be empty if the request's body is POST encoding
        # or other stuff werkzeug can recognize
        return False
