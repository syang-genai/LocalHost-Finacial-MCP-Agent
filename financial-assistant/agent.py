from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.langchain_tool import LangchainTool
from . import prompt


# Endpoint URL provided by your vLLM deployment
api_base_url = "http://0.0.0.0:8000/v1"

# Model name as recognized by *your* vLLM endpoint configuration
model_name_at_endpoint = "hosted_vllm//root/Qwen/Qwen/Qwen3-0.6B"

# fetching finance news
news_tool = LangchainTool(YahooFinanceNewsTool())

MODEL=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
    )

root_agent = LlmAgent(
    name="financial-assistant",
    model=MODEL,
    description=(
        "Navigate the world of finance with confidence. This agent is designed to be your all-in-one partner for managing and understanding your money. From real-time market updates to complex financial analysis, it provides the tools and insights you need to make informed decisions."
    )
    instruction=prompt.FINANCIAL_ASSISTANT_PROMPT,
    output_key="assistant_output",
    tools=[news_tool]
)
