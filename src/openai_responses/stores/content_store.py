from typing import Dict, Union


class ContentStore:
    def __init__(self) -> None:
        self._data: Dict[str, bytes] = {}

    def put(self, id: str, content: bytes) -> None:
        self._data[id] = content

    def get(self, id: str) -> Union[bytes, None]:
        return self._data.get(id)

    def delete(self, id: str) -> None:
        del self._data[id]
