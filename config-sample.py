# List of paths to organizations in your domain to search
# The search will find all users in these orgs and their sub-orgs
INCLUDE_ORG_UNITS = [
    '/'
]

# List of org paths to not include in results
EXCLUDE_ORG_UNITS = [ 
    '/Staff',
]

# Your GAFE domain
DOMAIN = 'myschool.org'

# A user in your GAFE domain with admin rights
ADMIN_USER = 'pzingg@kentfieldschools.org'

# CIDR representations of your school's subnet(s)
ALLOW_FROM = [
    '10.0.0.0/8'
]

# Shared secret keys
API_KEYS = [
    'key1',
    'key2'
]
