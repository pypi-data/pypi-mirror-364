from http_misc.services import Transformer

from iiko_sdk.gateways.authorization.v1.client import AuthorizationGateway


class SetAuthorization(Transformer):
    """
    Указывает у запроса заголовок Authorization вида 'Bearer {access_token}' предварительно запросив токен пользователя
    """

    def __init__(self, api_login: str, base_url: str):
        self.api_login = api_login
        self.base_url = base_url

    async def modify(self, request_id, *args, **kwargs):
        gateway = AuthorizationGateway(self.base_url)
        access_token = await gateway.get_api_token(self.api_login)
        # TODO: кеширование
        headers = kwargs.setdefault('cfg', {}).setdefault('headers', {})
        headers['Content-Type'] = 'application/json; charset=utf-8'
        headers['Authorization'] = f'Bearer {access_token}'

        return args, kwargs
