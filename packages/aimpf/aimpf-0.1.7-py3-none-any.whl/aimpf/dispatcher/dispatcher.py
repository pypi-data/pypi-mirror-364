import logging
from abc import ABC, abstractmethod
# from pycarta.auth import CartaAgent
from pycarta.auth import CartaAgent

logger = logging.getLogger(__name__)

__all__ = ["Dispatcher"]

"""
TODO: When the changeover to the pycarta singleton agent is complete, that agent should handle token refresh and other administrative tasks associated with maintaining an active connection to Carta. Therefore, this should change to something like the following,

class Dispatcher(ABC):
    def __init__(
        self,
        *,
        namespace: None | str=None,
        service: None | str=None,
        host: None | str=None
    ):
    
        if host is None and (namespace is None and namespace is None):
            raise ValueError("Either a Host or a Namespace and Service must be specified to create a Dispatcher.")
        auth = pycarta.get_agent()
        self._namespace = namespace
        self._service = service
        self._host = host or (auth.host + f"/service/{namespace}/{service}")
        
    @property
    def auth(self):
        agent = CartaAgent(
            token=pycarta.get_agent().token,
            host=self._host,)
        agent._session.header.update({"X_CARTA_TOKEN": f"Bearer {agent.token}"})
        return agent
"""
class Dispatcher(ABC):
    """
    Base class for dispatchers.
    """
    def __init__(
        self,
        auth: CartaAgent,
        *,
        namespace: None | str=None,
        service: None | str=None,
        host: None | str=None
    ):
        """
        :param auth:
            The authorization agent to use.
        :param namespace:
            The Carta namespace to use. Required if `host` is not specified.
        :param service:
            The Carta service to use. Required if `host` is not specified.
        :param host:
            The URL of the dispatcher. This is used for Dispatchers that have
            not been registered as a Carta service.
        """
        if namespace is not None and service is not None:
            self._auth: CartaAgent = CartaAgent(
                token=auth.token,
                host=auth.host + f"/service/{namespace}/{service}")
        elif host is not None:
            self._auth: CartaAgent = CartaAgent(
                token=auth.token,
                host=str(host))
            self._auth._session.headers.update({"X_CARTA_TOKEN": f"Bearer {self._auth.token}"})
        else:
            raise ValueError(
                "If registered as a Carta service, specify 'namespace' and "
                "'service'. If not, specify 'host'.")
        
    @property
    def auth(self):
        """
        The authorization agent.
        """
        return self._auth
        
    @property
    def url(self):
        """
        The URL of the dispatcher.
        """
        return self.auth.url
    
    @url.setter
    def url(self, value: str):
        """
        Set the URL of the dispatcher.
        """
        self.auth.url = value
