
#
# from kynex.llm.gemini.gemini import GeminiLLM
# from kynex.llm.groq.groq import GroqLLM
# from kynex.llm.ollama.ollama import OllamaLLMWrapper as OllamaLLM
#
# class LLMConnector:
#     def __init__(self, model_name: str, llm_type: str, host: str = None):
#         self.model_name = model_name
#         self.llm_type = llm_type.lower()
#         self.host = host  # Host required for Ollama
#
#     def get_llm_instance(self):
#         print(f"🔍 Selected LLM: {self.llm_type} | Model: {self.model_name}")
#
#         if self.llm_type == "gemini":
#             return GeminiLLM(model_name=self.model_name)
#         elif self.llm_type == "groq":
#             return GroqLLM(model_name=self.model_name)
#         elif self.llm_type == "ollama":
#             if not self.host:
#                 raise ValueError("Host is required for Ollama LLM.")
#             return OllamaLLM(model_name=self.model_name, host=self.host)
#         else:
#             raise ValueError(f"Unsupported LLM type: {self.llm_type}")
#
#     def getLLMData(self, prompt: str) -> str:
#         llm = self.get_llm_instance()
#         return llm.get_data(prompt)

#
# from kynex.llm.gemini.GeminiLLMWrapper import GeminiLLMWrapper
# from kynex.llm.groq.GroqLLMWrapper import GroqLLMWrapper
# from kynex.llm.ollama.OllamaLLMWrapper import OllamaLLMWrapper
#
# class LLMConnectorHelper:
#     def __init__(self, model_name: str, llm_type: str, api_key: str = None, host: str = None):
#         self.model_name = model_name
#         self.llm_type = llm_type.lower()
#         self.api_key = api_key
#         self.host = host
#
#     def get_llm_instance(self):
#         print(f" Selected LLM: {self.llm_type} | Model: {self.model_name}")
#
#         if self.llm_type == "gemini":
#             return GeminiLLMWrapper(api_key=self.api_key, model_name=self.model_name)
#         elif self.llm_type == "groq":
#             return GroqLLMWrapper(api_key=self.api_key, model_name=self.model_name)
#         elif self.llm_type == "ollama":
#             if not self.host:
#                 raise ValueError("Host is required for Ollama LLM.")
#             return OllamaLLMWrapper(model_name=self.model_name, host=self.host)
#         else:
#             raise ValueError(f"Unsupported LLM type: {self.llm_type}")
#
#     def getLLMData(self, prompt: str) -> str:
#         llm = self.get_llm_instance()
#         return llm.get_data(prompt)


from kynex.llm.gemini.GeminiLLMWrapper import GeminiLLMWrapper
from kynex.llm.groq.GroqLLMWrapper import GroqLLMWrapper
from kynex.llm.ollama.OllamaLLMWrapper import OllamaLLMWrapper

class LLMConnectorHelper:
    def __init__(self, model_name: str, llm_type: str, api_key: str = None, host: str = None):
        self.model_name = model_name
        self.llm_type = llm_type.lower()
        self.api_key = api_key
        self.host = host

    def get_llm_instance(self):
        print(f"🔍 Selected LLM: {self.llm_type} | Model: {self.model_name}")

        if self.llm_type == "gemini":
            return GeminiLLMWrapper(api_key=self.api_key, model_name=self.model_name)
        elif self.llm_type == "groq":
            return GroqLLMWrapper(api_key=self.api_key, model_name=self.model_name)
        elif self.llm_type == "ollama":
            if not self.host:
                raise ValueError("Host is required for Ollama LLM.")
            return OllamaLLMWrapper(model_name=self.model_name, host=self.host)
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

    def getLLMData(self, prompt: str) -> dict:
        llm = self.get_llm_instance()
        result = llm.get_data(prompt)

        if isinstance(result, str):
            result = {
                "response": result,
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None
            }

        # 🔹 Auto-print the result (so user doesn't have to call print())
        # print("\n🔹 LLM Response:\n")
        # print(result["response"])
        #
        # if result["total_tokens"] is not None:
        #     print(
        #         f"\n Token Usage → Prompt: {result['prompt_tokens']} | Completion: {result['completion_tokens']} | Total: {result['total_tokens']}")
        # else:
        #     print("\n Token usage information not available.")
        #
        # return result