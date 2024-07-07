import json
import anthropic
import openai
import os
from groq import Groq
from .config import Config
from .system_prompt_loader import SystemPromptLoader

class ScriptGenerator:
    def __init__(self, config: Config):
        self.config = config
        self.system_prompt_loader = SystemPromptLoader(config)

    async def generate_script(self, prompt: str, length: float, model: str) -> str:
        system_prompt = self._prepare_system_prompt(prompt, length)
        response_data = None

        if model == "claude":
            response_data = self._generate_with_claude(system_prompt)
        elif model == "gpt4":
            response_data = self._generate_with_gpt4(system_prompt)
        elif model == "llama":
            response_data = self._generate_with_llama(system_prompt)

        if response_data == None:
            return ""

        title = response_data.get("title", "")
        subject = self._create_subject_identifier(title)

        # Salvează datele complete în fișierul JSON
        os.makedirs(f"output/{subject}", exist_ok=True)
        with open(f"output/{subject}/script.json", "w", encoding="utf-8") as f:
            json.dump(response_data, f, ensure_ascii=False, indent=2)

        return subject

    def _create_subject_identifier(self, title: str) -> str:
        # Creează un identificator unic bazat pe titlu
        subject = title.replace(":", "").replace(" ", "_")
        return subject

    def _prepare_system_prompt(self, prompt: str, length: float) -> str:
        with open(self.config.SYSTEM_PROMPT_FILE, "r") as file:
            system_prompt = file.read()

        with open(self.config.USED_SUBJECTS_FILE, "r") as file:
            used_subjects = file.read().replace("\n", ", ")

        system_prompt = system_prompt.replace("<<IGNORED TOPICS>>", used_subjects)
        system_prompt = system_prompt.replace("<<VIDEO LENGTH>>", f"{length} minutes")
        system_prompt = system_prompt.replace("<<TOPIC>>", prompt)

        return system_prompt

    def _generate_with_claude(self, system_prompt: str) -> dict:
        client = anthropic.Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=0,
            system="",
            messages=[
                {"role": "user", "content": [{"type": "text", "text": system_prompt}]}
            ],
        )
        response = message.model_dump()
        response_text = response["content"][0]["text"]
        return json.loads(self._extract_json(response_text))

    def _generate_with_gpt4(self, system_prompt: str) -> dict:
        client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-4-turbo-2024-04-09",
            messages=[{"role": "user", "content": system_prompt}],
            temperature=1,
            max_tokens=4095,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        response_text = response.choices[0].message.content
        if response_text is None:
            raise ValueError("GPT-4 returned an empty response")
        return json.loads(self._extract_json(response_text))

    def _generate_with_llama(self, system_prompt: str) -> dict:
        client = Groq(api_key=self.config.GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": system_prompt}],
            model="llama3-70b-8192",
        )
        response_text = chat_completion.choices[0].message.content
        if response_text is None:
            raise ValueError("Llama model returned an empty response")
        return json.loads(self._extract_json(response_text))

    def _extract_json(self, text: str) -> str:
        if text is None:
            raise ValueError("Cannot extract JSON from None")
        start_index = text.find("{")
        end_index = text.rfind("}")
        if start_index != -1 and end_index != -1:
            return text[start_index : end_index + 1]
        else:
            raise ValueError("No valid JSON found in the response")
