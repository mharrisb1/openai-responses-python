from openai.types.embedding import Embedding
from openai.types.embedding_create_params import EmbeddingCreateParams
from openai.types.create_embedding_response import CreateEmbeddingResponse, Usage

import httpx
import respx

from ._base import StatelessRoute

from .._types.partials.embeddings import PartialCreateEmbeddingResponse

from .._utils.serde import json_loads, model_parse

__all__ = ["EmbeddingsCreateRoute"]


class EmbeddingsCreateRoute(
    StatelessRoute[
        CreateEmbeddingResponse,
        PartialCreateEmbeddingResponse,
    ]
):
    def __init__(self, router: respx.MockRouter) -> None:
        super().__init__(
            route=router.post(url__regex="/embeddings"),
            status_code=201,
        )

    @staticmethod
    def _build(
        partial: PartialCreateEmbeddingResponse,
        request: httpx.Request,
    ) -> CreateEmbeddingResponse:
        content: EmbeddingCreateParams = json_loads(request.content)
        embeddings = partial.get("data", [])
        response = CreateEmbeddingResponse(
            data=[model_parse(Embedding, e) for e in embeddings],
            model=partial.get("model", content["model"]),
            object="list",
            usage=model_parse(
                Usage,
                partial.get("usage", dict({"prompt_tokens": 0, "total_tokens": 0})),
            ),
        )
        return response
