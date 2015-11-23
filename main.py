import httplib2
import json
import os

from apiclient import discovery
import oauth2client
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.appengine import AppAssertionCredentials
from google.appengine.api import memcache

from config import INCLUDE_ORG_UNITS, EXCLUDE_ORG_UNITS, DOMAIN, ADMIN_USER

import webapp2

SCOPES = [
    'https://www.googleapis.com/auth/admin.directory.orgunit',
    'https://www.googleapis.com/auth/admin.directory.user'
]

def getServiceAccountCredentials(scopes):
    if os.environ.get('SERVER_SOFTWARE', '').startswith('Development'):
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

class IndexPage(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get('limit')
        if limit:
            limit = int(limit)
        service = self.app.config.get('directory_service')
        usernames = findActiveUsersInOrgUnits(service, limit)
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write('\n'.join(usernames))

# Google OAuth2 setup for service accounts, if we ever need to use it
credentials = getServiceAccountCredentials(SCOPES)

http = httplib2.Http(cache=memcache)
auth_http = credentials.authorize(http)
service = discovery.build('admin', 'directory_v1', http=auth_http)
config = { 'directory_service': service }

app = webapp2.WSGIApplication(routes=[
    ('/', IndexPage), ], 
    debug=True,
    config=config)