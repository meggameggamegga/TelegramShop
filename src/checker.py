import asyncio
import json
import re
import ssl
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

import aiohttp
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _extract_tokens(data: str) -> str:
    """Extract tokens from data"""

    pattern = re.compile('access_token=((?:[a-zA-Z]|\d|\.|-|_)*).*id_token=((?:[a-zA-Z]|\d|\.|-|_)*).*expires_in=(\d*)')
    response = pattern.findall(data['response']['parameters']['uri'])[0]
    return response


def _extract_tokens_from_uri(url: str) -> Optional[Tuple[str, Any]]:
    try:
        access_token = url.split("access_token=")[1].split("&scope")[0]
        token_id = url.split("id_token=")[1].split("&")[0]
        return access_token, token_id
    except IndexError as e:
        print(f"Cookies Invalid: {e}")


FORCED_CIPHERS = [
    'ECDHE-ECDSA-AES256-GCM-SHA384',
    'ECDHE-ECDSA-AES128-GCM-SHA256',
    'ECDHE-ECDSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-GCM-SHA256',
    'ECDHE-RSA-CHACHA20-POLY1305',
    'ECDHE-RSA-AES128-SHA256',
    'ECDHE-RSA-AES128-SHA',
    'ECDHE-RSA-AES256-SHA',
    'ECDHE-ECDSA-AES128-SHA256',
    'ECDHE-ECDSA-AES128-SHA',
    'ECDHE-ECDSA-AES256-SHA',
    'ECDHE+AES128',
    'ECDHE+AES256',
    'ECDHE+3DES',
    'RSA+AES128',
    'RSA+AES256',
    'RSA+3DES',
]


class ClientSession(aiohttp.ClientSession):
    def __init__(self, *args, **kwargs):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3
        ctx.set_ciphers(':'.join(FORCED_CIPHERS))
        super().__init__(*args, **kwargs, cookie_jar=aiohttp.CookieJar(), connector=aiohttp.TCPConnector(ssl=False))


class Auth:
    RIOT_CLIENT_USER_AGENT = "ShooterGame/11 Windows/10.0.22621.1.768.64bit"
     #RIOT_CLIENT_USER_AGENT = 'ShooterGame/11 Windows/10.0.22621.1.768.64bit'

    def __init__(self) -> None:
        self._headers: Dict = {
            'Content-Type': 'application/json',
            'User-Agent': Auth.RIOT_CLIENT_USER_AGENT,
            'Accept': 'application/json, text/plain, */*',
        }
        self.user_agent = Auth.RIOT_CLIENT_USER_AGENT

    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """This function is used to authenticate the user."""

        session = ClientSession()

        data = {"acr_values": "urn:riot:bronze",
                "claims": "",
                "client_id": "riot-client",
                "nonce": "oYnVwCSrlS5IHKh7iI16oQ",
                "redirect_uri": "http://localhost/redirect",
                "response_type": "token id_token",
                "scope": "openid link ban lol_region"
            }

        await session.post('https://auth.riotgames.com/api/v1/authorization', json=data, headers=self._headers)


        data = {"type": "auth", "username": username, "password": password, "remember": True}
        async with session.put('https://auth.riotgames.com/api/v1/authorization', json=data,
                            headers=self._headers) as r:

            data = await r.json()
            print(data,'ВНУТРИ АУНТИФИКАЦИЯ')
        await session.close()
        if data['type'] == 'response':

            response = _extract_tokens(data)
            access_token = response[0]
            token_id = response[1]
            return {'auth': 'response', 'data': {'access_token': access_token, 'token_id': token_id}}

        else:
            return None

    async def get_entitlements_token(self, access_token: str) -> Optional[str]:
        """This function is used to get the entitlements token."""

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://entitlements.auth.riotgames.com/api/token/v1', headers=headers, json={}) as r:
            data = await r.json()

        await session.close()

        entitlements_token = data['entitlements_token']

        return entitlements_token

    async def get_userinfo(self, access_token: str) -> Tuple[str, str, str]:
        """This function is used to get the user info."""

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        async with session.post('https://auth.riotgames.com/userinfo', headers=headers, json={}) as r:
            data = await r.json()
        await session.close()
        try:
            puuid = data['sub']
            name = data['acct']['game_name']
            tag = data['acct']['tag_line']
            country = data['country']
        except KeyError:
           print('Ошибка в getuserinfo')
        else:
            return puuid, name, tag,country

    async def get_region(self, access_token: str, token_id: str) -> str:
        """This function is used to get the region."""

        session = ClientSession()

        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {access_token}'}

        body = {"id_token": token_id}

        async with session.put(
                'https://riot-geo.pas.si.riotgames.com/pas/v1/product/valorant', headers=headers, json=body
        ) as r:
            data = await r.json()

        await session.close()
        try:
            region = data['affinities']['live']
        except KeyError:
            print('Ошибка в регионе')
        else:
            return region



    async def temp_auth(self, username: str, password: str) -> Optional[Dict[str, Any]]:

        authenticate = await self.authenticate(username, password)

        try:
            if authenticate['auth'] == 'response':
                access_token = authenticate['data']['access_token']
                #entitlements_token = await self.get_entitlements_token(access_token)
                return access_token
        except Exception as e:
            return None

    async def check_ban(self,acc_token):

        session = ClientSession()

        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {acc_token}"
        }
        async with session.get('https://auth.riotgames.com/userinfo',headers=headers) as r:

            data = await r.json()
            await session.close()
            #print(data,'БАН БАН ')
            banned = data.get('ban',0).get('restrictions',0)
            if banned:
                return True
            return False



