class SystemPromptLoader:
    def __init__(self, config):
        self.config = config

    def load_system_prompt(self):
        with open(self.config.SYSTEM_PROMPT_FILE, "r") as f:
            return f.read().strip()
