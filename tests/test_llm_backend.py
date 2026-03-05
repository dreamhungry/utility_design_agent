"""LLM 后端测试（mock 调用）"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from utility_design_agent.llm_backend import create_llm_backend
from utility_design_agent.llm_backend.openai_backend import OpenAIBackend
from utility_design_agent.llm_backend.litellm_backend import LiteLLMBackend


class TestCreateBackend:
    def test_create_openai(self):
        backend = create_llm_backend("openai", api_key="test-key")
        assert isinstance(backend, OpenAIBackend)

    def test_create_litellm(self):
        backend = create_llm_backend("litellm", api_key="test-key")
        assert isinstance(backend, LiteLLMBackend)

    def test_invalid_backend(self):
        with pytest.raises(ValueError, match="不支持的 LLM 后端"):
            create_llm_backend("invalid")


class TestOpenAIBackend:
    @pytest.mark.asyncio
    async def test_generate(self):
        backend = OpenAIBackend(api_key="test-key", model="gpt-4o")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '[{"behavior": "test", "formula": "x"}]'

        with patch.object(backend.client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_response):
            result = await backend.generate([{"role": "user", "content": "test"}])
            assert "test" in result


class TestLiteLLMBackend:
    @pytest.mark.asyncio
    async def test_generate(self):
        backend = LiteLLMBackend(api_key="test-key", model="gpt-4o")
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '[{"behavior": "test", "formula": "x"}]'

        with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_response):
            result = await backend.generate([{"role": "user", "content": "test"}])
            assert "test" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
