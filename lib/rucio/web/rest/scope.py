#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2012
# - Vincent Garonne, <vincent.garonne@cern.ch>, 2012-2013

from json import dumps
from logging import getLogger, StreamHandler, DEBUG
from web import application, ctx, header, BadRequest, Created, InternalError, Unauthorized

from rucio.api.scope import add_scope, get_scopes, list_scopes
from rucio.api.authentication import validate_auth_token
from rucio.common.exception import AccountNotFound, Duplicate, RucioException
from rucio.common.utils import generate_http_error


logger = getLogger("rucio.scope")
sh = StreamHandler()
sh.setLevel(DEBUG)
logger.addHandler(sh)

urls = (
    '/', 'Scope',
    '/(.+)/scopes', 'Scopes',
    '/(.+)/limits', 'AccountLimits',
    '/(.+)', 'AccountParameter'
)


class Scope:
    """ create new rucio scopes. """

    def GET(self):
        """
        List all scopes.

        HTTP Success:
            200 Success
        """

        header('Content-Type', 'application/octet-stream')
        header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        header('Cache-Control', 'post-check=0, pre-check=0', False)
        header('Pragma', 'no-cache')

        auth_token = ctx.env.get('HTTP_X_RUCIO_AUTH_TOKEN')
        auth = validate_auth_token(auth_token)

        if auth is None:
            raise generate_http_error(401, 'CannotAuthenticate', 'Cannot authenticate with given credentials')

        return dumps(list_scopes())

    def PUT(self):
        raise BadRequest()

    def POST(self, account, scope):
        """
        Creates scope with given scope name.

        HTTP Success:
            201 Created

        HTTP Error:
            401 Unauthorized
            404 Not Found
            409 Conflict
            500 Internal Error

        :param Rucio-Auth-Account: Account identifier.
        :param Rucio-Auth-Token: as an 32 character hex string.
        :params Rucio-Account: account belonging to the new scope.
        """
        header('Content-Type', 'application/octet-stream')

        auth_token = ctx.env.get('HTTP_X_RUCIO_AUTH_TOKEN')

        auth = validate_auth_token(auth_token)

        if auth is None:
            raise Unauthorized()

        try:
            add_scope(scope, account)
        except Duplicate, e:
            raise generate_http_error(409, 'Duplicate', e.args[0][0])
        except AccountNotFound, e:
            raise generate_http_error(404, 'AccountNotFound', e.args[0][0])
        except RucioException, e:
            raise generate_http_error(500, e.__class__.__name__, e.args[0][0])
        except Exception, e:
            raise InternalError(e)

        raise Created()

    def DELETE(self):
        raise BadRequest()


class ScopeList:
    """ list scopes """

    def GET(self, account):
        """
        List all scopes for an account.

        HTTP Success:
            200 OK

        HTTP Error:
            401 Unauthorized
            404 Not Found
            500 InternalError

        :param Rucio-Account: Account identifier.
        :param Rucio-Auth-Token: as an 32 character hex string.
        :returns: A list containing all scope names for an account.
        """
        header('Content-Type', 'application/json')
        header('Cache-Control', 'no-cache, no-store, max-age=0, must-revalidate')
        header('Cache-Control', 'post-check=0, pre-check=0', False)
        header('Pragma', 'no-cache')

        auth_token = ctx.env.get('HTTP_X_RUCIO_AUTH_TOKEN')

        auth = validate_auth_token(auth_token)

        if auth is None:
            raise Unauthorized()

        try:
            scopes = get_scopes(account)
        except AccountNotFound, e:
            raise generate_http_error(404, 'AccountNotFound', e.args[0][0])
        except Exception, e:
            raise InternalError(e)

        if not len(scopes):
            raise generate_http_error(404, 'ScopeNotFound', 'no scopes found for account ID \'%s\'' % account)

        return dumps(scopes)

    def PUT(self):
        header('Content-Type', 'application/octet-stream')
        raise BadRequest()

    def POST(self):
        header('Content-Type', 'application/octet-stream')
        raise BadRequest()

    def DELETE(self):
        header('Content-Type', 'application/octet-stream')
        raise BadRequest()


"""----------------------
   Web service startup
----------------------"""

app = application(urls, globals())
application = app.wsgifunc()
