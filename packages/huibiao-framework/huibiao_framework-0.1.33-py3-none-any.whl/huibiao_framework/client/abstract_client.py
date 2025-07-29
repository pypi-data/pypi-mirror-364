from abc import ABC
from typing import Optional

import aiohttp


class HuibiaoAbstractClient(ABC):
    def __init__(
        self,
        client_name: str,
        *,
        url: str = None,
        host: str = None,
        session: Optional[aiohttp.ClientSession] = None
    ):
        self.__session = session
        self.__name = client_name
        self.__url = url
        self.__host = host
        assert self.__session is not None, "会话不能为空"
        assert self.__url is not None or self.__host is not None, (
            "url和host不能同时为空"
        )

    @property
    def session(self):
        return self.__session

    @property
    def client_name(self) -> Optional[str]:
        return self.__name

    @property
    def url(self) -> Optional[str]:
        return self.__url

    @property
    def host(self) -> Optional[str]:
        return self.__host


    def session_tag(self, session_id: str) -> str:
        session_id_suffix = f"[{session_id}]" if session_id else ""
        return f"[{self.client_name}]{session_id_suffix}"
