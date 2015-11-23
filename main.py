import httplib2
import json
import os
import re

from netaddr import IPNetwork, IPAddress

from apiclient import discovery
import oauth2client
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache

from config import ALLOW_FROM, API_KEYS, INCLUDE_ORG_UNITS, EXCLUDE_ORG_UNITS, DOMAIN, ADMIN_USER

import webapp2

# AppAssertionCredentials does not work for admin SDK, because
# you need a JWT "sub" user to actually perform the requests.
# Also AppAssertionCredentials will not work with the dev server.

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.user'
]

NEED_SUB_USER = True

def getServiceAccountCredentials(scopes):
    if NEED_SUB_USER or os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
        secrets = json.load(open('service_account_secrets.json'))
        credentials = SignedJwtAssertionCredentials(secrets['client_email'], 
            secrets['private_key'], scope=scopes, sub=ADMIN_USER)
        return credentials
    else:
        return AppAssertionCredentials(scopes)

def findActiveUsersInOrgUnits(service, limit):
    usernames = [ ]
    for orgUnitPath in INCLUDE_ORG_UNITS:
        pageToken = None
        maxResults = 500
        if limit and maxResults > limit:
            maxResults = limit
        query = "orgUnitPath='%s' isSuspended=false" % orgUnitPath
        while True:
            results = service.users().list(customer='my_customer',
                domain=DOMAIN,
                fields='nextPageToken,users(orgUnitPath,primaryEmail)',
                query=query,
                maxResults=maxResults,
                pageToken=pageToken,
                orderBy='email').execute()
            pageToken = results.get('nextPageToken')
            for user in results['users']:
                orgUnit = user['orgUnitPath']
                if orgUnit not in EXCLUDE_ORG_UNITS:
                    username, domain = user['primaryEmail'].split('@')
                    usernames.append(username)
                    if limit and len(usernames) >= limit:
                        pageToken = None
                        break
            if not pageToken:
                break
    return usernames

def checkIp(app, request):
    request_ip = IPAddress(request.remote_addr)
    allow_from = app.config.get('allow_from')
    for cidr in allow_from:
        if request_ip in cidr:
            return True
    return  False

def checkApiKey(app, request):
    api_key = None
    auth_header = request.headers.get('authorization')
    if auth_header:
        print "AUTH %s" % auth_header
        m = re.match(r'Bearer\s+(.+)\s*', auth_header)
        if m:
            api_key = m.group(1)
    if not api_key:
        api_key = request.get('apikey')
    if api_key and api_key in app.config.get('api_keys'):
        return True
    return False


class IndexPage(webapp2.RequestHandler):
    def get(self):
        request_allowed = checkIp(self.app, self.request)
        if not request_allowed:
            self.abort(403)
            return
        authorized = checkApiKey(self.app, self.request)
        if not authorized:
            self.abort(401)
            return

        limit = self.request.get('limit')
        if limit:
            limit = int(limit)
        service = self.app.config.get('directory_service')
        usernames = findActiveUsersInOrgUnits(service, limit)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('\n'.join(usernames) + '\n')

# Google OAuth2 setup for service accounts, if we ever need to use it
credentials = getServiceAccountCredentials(SCOPES)

http = httplib2.Http(cache=memcache)
auth_http = credentials.authorize(http)
service = discovery.build('admin', 'directory_v1', http=auth_http)

# Add localhost if we are testing
allow_from = [ IPNetwork(x) for x in ALLOW_FROM ]
if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
    allow_from.append(IPNetwork('::1'))

config = { 'directory_service': service, 'allow_from': allow_from, 'api_keys': API_KEYS }

app = webapp2.WSGIApplication(routes=[
    ('/', IndexPage), ], 
    debug=True,
    config=config)
