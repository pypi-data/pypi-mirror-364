from tw_textforge.config.settings import setting

class AIModel():
    """A class for AI model settings and initialization."""
    PROVIDERS = ["openai", "openrouter", "google_genai", "ollama"]
    def __init__(
        self,
        provider:str=setting.provider,
        model_name:str=setting.model_name,
        temperature:float=setting.temperature,
        top_p:float=setting.top_p,
        max_tokens:int=setting.max_tokens,
    ):
        # Choose LLM Provider and Model
        self.provider = provider
        self.model_name = model_name

        # LLM Parameters
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens

        # AI Model Provider URLs
        self.openai_api_url = setting.openai_api_url
        self.openrouter_api_url = setting.openrouter_api_url
        self.ollama_api_url = setting.ollama_api_url
        
        # AI Model Provider Keys
        self.openai_api_key = setting.openai_api_key
        self.openrouter_api_key = setting.openrouter_api_key
        self.genai_api_key = setting.genai_api_key
        
        # Hugging Face Token
        self.hf_token = setting.hf_token
        
        # set up default LLM
        self.llm = self._get_llm(
            provider=provider,
            model_name=model_name,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )

    def _get_llm(
        self,
        provider:str,
        model_name:str,
        temperature:float=None,
        top_p:float=None,
        max_tokens:int=None,
    ):
        """取得llm"""
        if provider not in self.PROVIDERS:
            raise ValueError("Unsupported provider")
        elif provider == "google_genai":
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=model_name,
                temperature= temperature if temperature is not None else self.temperature,
                top_p= top_p if top_p is not None else self.top_p,
                max_tokens= max_tokens if max_tokens is not None else self.max_tokens,
                api_key=self.genai_api_key,
            )
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name,
                temperature= temperature if temperature is not None else self.temperature,
                top_p= top_p if top_p is not None else self.top_p,
                max_tokens= max_tokens if max_tokens is not None else self.max_tokens,
                base_url=self.openai_api_url,
                api_key=self.openai_api_key
            )
        elif provider == "openrouter":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=model_name,
                temperature= temperature if temperature is not None else self.temperature,
                top_p= top_p if top_p is not None else self.top_p,
                max_tokens= max_tokens if max_tokens is not None else self.max_tokens,
                base_url=self.openrouter_api_url,
                api_key=self.openrouter_api_key
            )
        elif provider == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=model_name,
                temperature= temperature if temperature is not None else self.temperature,
                top_p= top_p if top_p is not None else self.top_p,
                max_tokens= max_tokens if max_tokens is not None else self.max_tokens,
                base_url=self.ollama_api_url,
                keep_alive=-1,
            )