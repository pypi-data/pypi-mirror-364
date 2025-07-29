import pytest
import os

from unittest.mock import ANY, patch
from openrouter_manager.adapter.ai_agent import AiAgent

__author__ = "Lenin Lozano"
__copyright__ = "Lenin Lozano"
__license__ = "MIT"


@pytest.fixture(autouse=True)
def setup_environment():
    AiAgent._instance = None  # Reset singleton instance before each test
    os.environ.clear()


def test_when_no_api_key_then_throw_error():
    """Main Function Tests"""
    with pytest.raises(ValueError) as e_info:
        AiAgent()
    assert str(e_info.value) == "AIAGENT_API_KEY is missing in environment variables"


def test_when_prompt_file_doesnot_exists_in_environment_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "test_prompt_file"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    with pytest.raises(ValueError):
        AiAgent()


def test_when_prompt_file_doesnot_exists_as_argument_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    with pytest.raises(ValueError):
        AiAgent(prompt_file="test_prompt_file")


def test_when_no_api_url_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    with pytest.raises(ValueError) as e_info:
        AiAgent()
    assert str(e_info.value) == "AIAGENT_API_URL is missing in environment variables"


def test_when_no_llm_model_then_throw_error():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    with pytest.raises(ValueError) as e_info:
        AiAgent()
    assert str(e_info.value) == "AIAGENT_LLM_MODEL is missing in environment variables"


def test_creation_when_ok():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt_2.prompt"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    AiAgent()


def test_creation_with_prompt_file_as_argument():
    os.environ.clear()
    os.environ["AIAGENT_API_KEY"] = "121231"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    AiAgent(prompt_file="tests/data/test_prompt.prompt")


def test_set_prompt():
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    ai_agent = AiAgent()
    ai_agent.set_prompt("tests/data/test_prompt_2.prompt")
    assert str(ai_agent.prompt) == '''Eres un asistente que resume incidencias.
Título: 
Descripción: 
Genera un resumen breve.'''


@patch('openrouter_manager.adapter.ai_agent.requests')
def test_resolve_ok(mock_requests):
    mock_response = mock_requests.post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {'choices': [{
        'message': {
            'content': "Te doy la respuesta papá"
        }
    }]}
    os.environ["AIAGENT_API_KEY"] = "12123123123"
    os.environ["AIAGENT_PROMPT_FILE"] = "tests/data/test_prompt.prompt"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    ai_agent = AiAgent()
    result = ai_agent.resolve({"titulo": "Este es el titulo",
                               "descripcion": "Descripcion"})
    mock_requests.post.assert_called_once_with(
        'https://openrouter.ai/api/v1/chat/completions', data=ANY, headers=ANY)
    assert result == "Te doy la respuesta papá"


def test_when_prompt_folder_has_no_prompts_then_error():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    with pytest.raises(ValueError):
        AiAgent()


def test_creation_with_prompt_folder_loads_first_prompt():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/data"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    agent = AiAgent()
    assert agent.get_actual_prompt() == "test_prompt.prompt"


def test_get_available_prompts():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/data/"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    agent = AiAgent()
    prompts = agent.get_available_prompts()
    assert "test_prompt.prompt" in prompts
    assert "test_prompt_2.prompt" in prompts


def test_get_actual_prompt():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/data"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    agent = AiAgent()
    agent.set_prompt("tests/data/test_prompt_2.prompt")
    assert agent.get_actual_prompt() == "test_prompt_2.prompt"


def test_change_prompt_success():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/data/"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    agent = AiAgent()
    agent.change_prompt("test_prompt_2.prompt")
    assert agent.get_actual_prompt() == "test_prompt_2.prompt"


def test_change_prompt_not_found_then_error():
    os.environ["AIAGENT_API_KEY"] = "key"
    os.environ["AIAGENT_PROMPT_FOLDER"] = "tests/data"
    os.environ["AIAGENT_API_URL"] = "https://openrouter.ai/api/v1/chat/completions"
    os.environ["AIAGENT_LLM_MODEL"] = "deepseek"
    agent = AiAgent()
    with pytest.raises(ValueError):
        agent.change_prompt("nonexistent.prompt")
