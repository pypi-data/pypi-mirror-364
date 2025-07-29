import requests
import json
import os
import logging

from openrouter_manager.adapter.prompt import Prompt
from openrouter_manager.adapter.variable import Variable
from openrouter_manager.adapter.llm_exception import LLMException


class AiAgent():
    logger = logging.getLogger(__name__)
    api_url = ""
    llm_model = ""
    _instance = None

    prompt = None
    prompt_folder = None
    available_prompts = []
    current_prompt_file = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AiAgent, cls).__new__(cls)
            try:
                prompt_file = kwargs.get('prompt_file') or os.getenv(
                    'AIAGENT_PROMPT_FILE')
                prompt_folder = kwargs.get('prompt_folder') or os.getenv(
                    'AIAGENT_PROMPT_FOLDER')
                cls._instance._initialize(prompt_file, prompt_folder)
            except Exception as e:
                cls._instance = None
                raise e
        return cls._instance

    def _initialize(self, prompt_file: str = None, prompt_folder: str = None):
        """ Initializes API settings and loads the prompt. """
        api_key = os.getenv('AIAGENT_API_KEY')
        if not api_key:
            raise ValueError("AIAGENT_API_KEY is missing in environment variables")

        api_url = os.getenv('AIAGENT_API_URL')
        if not api_url:
            raise ValueError("AIAGENT_API_URL is missing in environment variables")
        llm_model = os.getenv('AIAGENT_LLM_MODEL')
        if not llm_model:
            raise ValueError("AIAGENT_LLM_MODEL is missing in environment variables")

        self.api_url = api_url
        self.llm_model = llm_model

        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "koralat.co",
            "X-Title": "Koral Advanced Technology"
        }

        if prompt_folder and os.path.isdir(prompt_folder):
            self.prompt_folder = prompt_folder
            self.available_prompts = [f for f in os.listdir(
                prompt_folder) if f.endswith('.prompt')]
            if len(self.available_prompts) == 0:
                raise ValueError(f"No .prompt files found in {prompt_folder}")

            # Default to first prompt if prompt_file not specified
            if prompt_file is None:
                prompt_file = self.available_prompts[0]
            elif prompt_file not in self.available_prompts:
                raise ValueError(
                    f"Prompt {prompt_file} is not in folder {prompt_folder}")

            full_path = os.path.join(prompt_folder, prompt_file)
            self._load_prompt(full_path)

        elif prompt_file:
            if not os.path.exists(prompt_file):
                raise ValueError(f"Prompt file not found: {prompt_file}")
            self._load_prompt(prompt_file)
        else:
            raise ValueError("Either prompt_file or prompt_folder must be provided")

    def _load_prompt(self, path: str):
        with open(path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        self.prompt = Prompt(prompt_content)
        self.current_prompt_file = os.path.basename(path)

    def resolve(self, variables: dict) -> str:
        """ Replaces variables in the prompt and sends the request to the LLM. """
        self.prompt.clean()
        for key, value in variables.items():
            variable = Variable(key, value)
            self.prompt.set_variable(variable)

        data = json.dumps({
            "model": self.llm_model,
            "messages": [{"role": "user", "content": str(self.prompt)}]
        })

        try:
            response = requests.post(self.api_url, data=data, headers=self.headers)
            response.raise_for_status()  # Throws an error for HTTP status codes 4xx/5xx
            return response.json().get(
                'choices', [{}])[0].get('message', {}).get('content', '')
        except requests.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            raise LLMException('Error requesting to LLM')

    def set_prompt(self, prompt_file: str):
        ''' Sets a prompt from a file without prompt folder as a active prompt. '''
        if not os.path.exists(prompt_file):
            raise ValueError(f"Prompt file not found: {prompt_file}")
        self._load_prompt(prompt_file)

    def get_actual_prompt(self) -> str:
        ''' Returns the current prompt file name. '''
        return self.current_prompt_file

    def get_available_prompts(self) -> list:
        ''' Returns a list of available prompt files in the prompt folder. '''
        return self.available_prompts

    def change_prompt(self, prompt_file: str):
        ''' Changes the current prompt to a new one from the prompt folder. '''
        if not self.prompt_folder:
            raise ValueError("Prompt folder not set, cannot change prompt dynamically")

        if prompt_file not in self.available_prompts:
            raise ValueError(
                f"Prompt {prompt_file} is not in folder {self.prompt_folder}")

        full_path = os.path.join(self.prompt_folder, prompt_file)
        self._load_prompt(full_path)
