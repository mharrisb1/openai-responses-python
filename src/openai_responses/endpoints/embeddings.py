import json
from typing import Any, List, Optional

import httpx
import respx

from openai.types.embedding import Embedding
from openai.types.embedding_create_params import EmbeddingCreateParams
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage

from ._base import StatelessMock, CallContainer
from ..decorators import side_effect
from ..tokens import count_tokens
from ..utils import model_dict


class EmbeddingsMock(StatelessMock):
    def __init__(self) -> None:
        super().__init__(
            name="embeddings_mock",
            endpoint="/v1/embeddings",
            route_registrations=[
                {
                    "name": "create",
                    "method": respx.post,
                    "pattern": None,
                    "side_effect": self._create,
                }
            ],
        )
        self.create = CallContainer()

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

        return self._make_decorator(getter)

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

        token_count = 0
        if isinstance(content["input"], str):
            token_count = count_tokens(content["model"], content["input"])

        embeddings = CreateEmbeddingResponse(
            data=[Embedding(embedding=embedding, index=0, object="embedding")],
            model=content["model"],
            object="list",
            usage=Usage(prompt_tokens=token_count, total_tokens=token_count),
        )

        return httpx.Response(status_code=201, json=model_dict(embeddings))
