# import google.generativeai as genai
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class GeminiLLM(LLMBase):
#     def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel(model_name)
#     def get_data(self, prompt: str) -> str:
#         try:
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#             response = self.model.generate_content(formatted_prompt)
#             print(response)
#             return response.text
#         except Exception as e:
#             return f"[Gemini ERROR]: {str(e)}"

#
# import google.generativeai as genai
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class GeminiLLMWrapper(LLMBase):
#     def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel(model_name)
#         print(f"🔹 [GeminiLLM] Initialized with model: {model_name}")
#
#     def get_data(self, prompt: str) -> str:
#         try:
#             print(f"🔹 [GeminiLLM] Generating response for prompt:\n{prompt}")
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             response = self.model.generate_content(formatted_prompt)
#             return "[Gemini] " + response.text
#
#         except Exception as e:
#             return f"[Gemini ERROR]: {str(e)}"

import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class GeminiLLMWrapper(LLMBase):
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        print(f"🔹 [GeminiLLM] Initialized with model: {model_name}")

    def get_data(self, prompt: str) -> dict:
        try:
            print(f"🔹 [GeminiLLM] Generating response for prompt:\n{prompt}")
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)

            response = self.model.generate_content(formatted_prompt)

            # Token usage details from Gemini
            usage = response.usage_metadata if hasattr(response, "usage_metadata") else {}

            return {
                "response": "[Gemini] " + response.text,
                "prompt_tokens": usage.get("prompt_token_count", "N/A"),
                "completion_tokens": usage.get("candidates_token_count", "N/A"),
                "total_tokens": usage.get("total_token_count", "N/A")
            }

        except Exception as e:
            return {
                "response": f"[Gemini ERROR]: {str(e)}",
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None
            }
