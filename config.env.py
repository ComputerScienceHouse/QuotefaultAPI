import os

# Flask config
DEBUG = True
IP = os.environ.get('API_QUOTEFAULT_IP', '127.0.0.1')
PORT = os.environ.get('API_QUOTEFAULT_PORT', 8080)
SERVER_NAME = os.environ.get('API_QUOTEFAULT_SERVER_NAME', 'quotefault-api.csh.rit.edu')

# DB Info
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///{}'.format(os.path.join(os.getcwd(), "data.db")))
#DB_HOST = os.environ.get('API_QUOTEFAULT_DB_HOST', 'mysql.csh.rit.edu')
#DB_USERNAME = os.environ.get('API_QUOTEFAULT_DB_USERNAME', 'quotefault')
#DB_NAME = os.environ.get('API_QUOTEFAULT_DB_NAME', 'quotefault')
#DB_PASSWORD = os.environ.get('API_QUOTEFAULT_DB_PASSWORD', '')

# OpenID Connect SSO config
OIDC_ISSUER = os.environ.get('API_QUOTEFAULT_OIDC_ISSUER', 'https://sso.csh.rit.edu/realms/csh')
OIDC_CLIENT_CONFIG = {
    'client_id': os.environ.get('API_QUOTEFAULT_OIDC_CLIENT_ID', 'quotefaultAPI'),
    'client_secret': os.environ.get('API_QUOTEFAULT_OIDC_CLIENT_SECRET', ''),
    'post_logout_redirect_uris': [os.environ.get('API_QUOTEFAULT_OIDC_LOGOUT_REDIRECT_URI', 'https://quotefault-api.csh.rit.edu/logout')]
}