import json
from functools import partial
from typing import Any, List, Optional

import httpx
import respx

from openai.types.embedding import Embedding
from openai.types.embedding_create_params import EmbeddingCreateParams
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage

from ._base import StatelessMock, CallContainer
from ..decorators import side_effect
from ..utils import model_dict


class EmbeddingsMock(StatelessMock):
    def __init__(self) -> None:
        super().__init__()
        self.url = self.BASE_URL + "/embeddings"
        self.create = CallContainer()

    def _register_routes(self, **common: Any) -> None:
        self.create.route = respx.post(url__regex=self.url).mock(
            side_effect=partial(self._create, **common)
        )

    def __call__(
        self,
        *,
        embedding: Optional[List[float]] = None,
        latency: Optional[float] = None,
        failures: Optional[int] = None,
    ):
        def getter(*args: Any, **kwargs: Any):
            return dict(
                embedding=embedding or [],
                latency=latency or 0,
                failures=failures or 0,
            )

        return self._make_decorator("embeddings_mock", getter)

    @side_effect
    def _create(
        self,
        request: httpx.Request,
        route: respx.Route,
        embedding: List[float],
        **kwargs: Any,
    ) -> httpx.Response:
        self.create.route = route

        content: EmbeddingCreateParams = json.loads(request.content)

        embeddings = CreateEmbeddingResponse(
            data=[Embedding(embedding=embedding, index=0, object="embedding")],
            model=content["model"],
            object="list",
            usage=Usage(prompt_tokens=0, total_tokens=0),
        )

        return httpx.Response(status_code=201, json=model_dict(embeddings))
