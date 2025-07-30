from unittest.mock import MagicMock, patch

import pytest

from uipath._config import Config
from uipath._execution_context import ExecutionContext
from uipath._services.llm_gateway_service import (
    EmbeddingModels,
    UiPathOpenAIService,
)
from uipath.models.llm_gateway import TextEmbedding


class TestOpenAIService:
    @pytest.fixture
    def config(self):
        return Config(base_url="https://example.com", secret="test_secret")

    @pytest.fixture
    def execution_context(self):
        return ExecutionContext()

    @pytest.fixture
    def openai_service(self, config, execution_context):
        return UiPathOpenAIService(config=config, execution_context=execution_context)

    def test_init(self, config, execution_context):
        service = UiPathOpenAIService(
            config=config, execution_context=execution_context
        )
        assert service._config == config
        assert service._execution_context == execution_context

    @patch.object(UiPathOpenAIService, "request_async")
    @pytest.mark.asyncio
    async def test_embeddings(self, mock_request, openai_service):
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0, "object": "embedding"}],
            "model": "text-embedding-ada-002",
            "object": "list",
            "usage": {"prompt_tokens": 4, "total_tokens": 4},
        }
        mock_request.return_value = mock_response

        # Call the method
        result = await openai_service.embeddings(input="Test input")

        # Assertions
        mock_request.assert_called_once()
        assert isinstance(result, TextEmbedding)
        assert result.data[0].embedding == [0.1, 0.2, 0.3]
        assert result.model == "text-embedding-ada-002"
        assert result.usage.prompt_tokens == 4

    @patch.object(UiPathOpenAIService, "request_async")
    @pytest.mark.asyncio
    async def test_embeddings_with_custom_model(self, mock_request, openai_service):
        # Mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "data": [{"embedding": [0.1, 0.2, 0.3], "index": 0, "object": "embedding"}],
            "model": "text-embedding-3-large",
            "object": "list",
            "usage": {"prompt_tokens": 4, "total_tokens": 4},
        }
        mock_request.return_value = mock_response

        # Call the method with custom model
        result = await openai_service.embeddings(
            input="Test input", embedding_model=EmbeddingModels.text_embedding_3_large
        )

        # Assertions for the result
        mock_request.assert_called_once()
        assert result.model == "text-embedding-3-large"
        assert len(result.data) == 1
        assert result.data[0].embedding == [0.1, 0.2, 0.3]
        assert result.data[0].index == 0
        assert result.object == "list"
        assert result.usage.prompt_tokens == 4
        assert result.usage.total_tokens == 4
