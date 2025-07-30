import os
import requests
from urllib.parse import urlparse
from typing import Text
from datetime import datetime
import jwt
import logging

_logger = logging.getLogger(__name__)

TOKEN_EXCHANGE_PATH = '/oauth/token'
GRANT_TYPE = 'urn:ietf:params:oauth:grant-type:token-exchange'
SUBJECT_TOKEN_TYPE = 'programmatic_access_token'

class SnowflakeTokenGenerator:
    def __init__(self, endpoint: Text, pat: Text, role: Text = None):
        """
        __init__ creates an object that uses the supplied PAT to get a token to access SPCS ingress endpoints.
        :param account: Your Snowflake account URL (<ORGNAME>-<ACCTNAME>.snowflakecomputing.com)
        :param endpoint: The endpoint you are trying to access (just the hostname here: <HASH>-<ORGNAME>-<ACCTNAME>.snowflakecomputing.app)
        :param pat: The PAT to use.
        :param role: The role to use when requesting the short-lived token (optional).
        """        
        self.endpoint = endpoint
        self.account = self.create_snowflake_account_url(endpoint)
        self.pat = open(pat, 'r').read() if os.path.isfile(pat) else pat
        self.role = role
        self.token = None
        self.renew_time = datetime.now()

    def create_snowflake_account_url(self, native_app_url: Text) -> Text:
        parsed = urlparse(native_app_url)
        host = parsed.hostname  # e.g., brbehlf-gk45826-privacerapartner1.snowflakecomputing.app
        
        if host:
            # Remove the first prefix before the first dash
            parts = host.split('-')
            if len(parts) > 1:
                clean_host = '-'.join(parts[1:])
                # Replace the ending `.app` with `.com`
                if clean_host.endswith('.snowflakecomputing.app'):
                    clean_host = clean_host.replace('.snowflakecomputing.app', '.snowflakecomputing.com')
                return clean_host
        return None  # fallback if something goes wrong

    def _get_new_token(self) -> Text:
        return self._exchange_response().text
    
    def _exchange_response(self) -> requests.models.Response:
        endpoint_host = urlparse(self.endpoint).hostname
        scope = f'session:scope:{self.role.upper()} {endpoint_host}' if self.role else f'{endpoint_host}'
        data = {
            'grant_type': GRANT_TYPE,
            'scope': scope,
            'subject_token': self.pat,
            'subject_token_type': SUBJECT_TOKEN_TYPE
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        url = f'https://{self.account}{TOKEN_EXCHANGE_PATH}'
        _logger.info(f"POST to {url} with data: {data}")
        resp = requests.post(url=url, data=data, headers=headers)
        _logger.info(f"Response status code: {resp.status_code}")
        _logger.info(f"Response text: {resp.text}")
        resp.raise_for_status()
        return resp


    def _get_token(self) -> Text:
        now = datetime.now()
        if self.token is None or self.renew_time <= now:
            self.token = self._get_new_token()

            jwt_details = jwt.decode(self.token, options={"verify_signature": False})
            self.renew_time = datetime.fromtimestamp(jwt_details['exp'])
        return self.token

    def authorization_header(self) -> dict:
        return {'Authorization': f'Snowflake Token="{self._get_token()}"'}