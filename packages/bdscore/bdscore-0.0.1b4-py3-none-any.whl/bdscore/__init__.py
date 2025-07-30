from .services.datapack import DataPack
from .services.datamanagement import DataManagement


import requests
import urllib3

class BDSCore:

    """
    Classe base para comunicação com as APIs da BDS DataSolution.
    Ao instanciar, é necessário fornecer a chave de autenticação.
    """
    def __init__(
        self,
        api_key: str,
        datapack_url: str = "https://temp-api.bdsdatapack.com.br",
        guard_url: str = "https://auth.bdsdatapack.com.br/api/v1",
        datamanagement_url: str = "https://api.bdsdatapack.com.br/smart-temp/data-management/v1",
        verify: str | bool = False
    ):
        
        if not api_key or not isinstance(api_key, str):
            raise ValueError("É necessário fornecer uma chave de autenticação válida.")
        self.api_key = api_key
        self.base_url = datapack_url
        self.datapack_url = datapack_url
        self.guard_url = guard_url
        self.datamanagement_url = datamanagement_url
        self.verify = verify

        self._session = requests.Session()
        self._session.headers.update({"BDSKey": self.api_key})

        # Remove warnings de SSL se verify=False
        if self.verify is False:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.datapack = DataPack(self)
        self.datamanagement = DataManagement(self)

        self.__request(
            method="get",
            url=f"{self.guard_url}/user/sync"
        )

  
    def __request(self, method, url, **kwargs):
        """
        Handler global para requisições HTTP, com tratamento de erro e correlation id.
        """
        try:
            response = self._session.request(method, url, verify=self.verify, **kwargs)
            if response.status_code == 401:
                correlation_id = response.headers.get("bdsh-correlation-id", "N/A")
                raise ValueError(f"Chave de autenticação incorreta ou não autorizada (HTTP 401). Verifique sua BDSKey. CorrelationId: {correlation_id}")
            response.raise_for_status()
            # Tenta retornar JSON, senão retorna o texto
            try:
                return response.json()
            except Exception:
                return response.text
        except requests.RequestException as e:
            correlation_id = None
            body = None
            if hasattr(e, 'response') and e.response is not None:
                correlation_id = e.response.headers.get("bdsh-correlation-id", "N/A")
                try:
                    body = e.response.text
                except Exception:
                    body = None
                msg = f"Erro na requisição: {e}. CorrelationId: {correlation_id}. Body: {body}"
            else:
                msg = f"Erro na requisição: {e}"
            raise RuntimeError(msg) from e
