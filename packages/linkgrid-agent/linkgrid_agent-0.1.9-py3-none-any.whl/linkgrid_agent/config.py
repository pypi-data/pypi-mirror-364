class AgentConfig:
    def __init__(
        self,
        system_prompt: str = "You are a helpful assistant that provides concise and accurate answers.",
        max_tokens: int = 150,
        temperature: float = 0.7,
        api_url: str = "https://bitnet-demo.azurewebsites.net/completion",
    ):
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.api_url = api_url

        self.headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://bitnet-demo.azurewebsites.net",
            "referer": "https://bitnet-demo.azurewebsites.net/",
            "user-agent": "LinkGridAgent/1.0",
        }
