# from groq import Groq
# from langchain_core.prompts import PromptTemplate
# from kynex.llm.base import LLMBase
#
# class GroqLLMWrapper(LLMBase):
#     def __init__(self, api_key: str, model_name: str):
#         self.client = Groq(api_key=api_key)
#         self.model_name = model_name
#
#     def get_data(self, prompt: str) -> str:
#         try:
#             # Optional: format prompt using LangChain template
#             template = PromptTemplate.from_template("{prompt}")
#             formatted_prompt = template.format(prompt=prompt)
#
#             response = self.client.chat.completions.create(
#                 model=self.model_name,
#                 messages=[{"role": "user", "content": formatted_prompt}],
#                 temperature=0.7
#             )
#             print(response)
#
#             return response.choices[0].message.content.strip()
#         except Exception as e:
#             return f"[Groq ERROR]: {str(e)}"

from groq import Groq
from langchain_core.prompts import PromptTemplate
from kynex.llm.base import LLMBase

class GroqLLMWrapper(LLMBase):
    def __init__(self, api_key: str, model_name: str):
        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def get_data(self, prompt: str) -> dict:
        try:
            # Format prompt using LangChain template
            template = PromptTemplate.from_template("{prompt}")
            formatted_prompt = template.format(prompt=prompt)

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": formatted_prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()
            usage = response.usage  # Token usage info

            return {
                "response": "[Groq] " + content,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }

        except Exception as e:
            return {
                "response": f"[Groq ERROR]: {str(e)}",
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None
            }
