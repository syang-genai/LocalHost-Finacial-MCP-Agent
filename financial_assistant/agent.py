import yfinance as yf
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.langchain_tool import LangchainTool
from . import prompt


# endpoint URL provided by your vLLM deployment
api_base_url = "http://0.0.0.0:8000/v1"

# model name as recognized by *your* vLLM endpoint configuration
model_name_at_endpoint = "hosted_vllm//root/Qwen/Qwen3-0.6B"

# fetching finance news
news_tool = LangchainTool(YahooFinanceNewsTool())


def get_stock_price(symbol: str) -> float:
    """    
        Retrieve the current stock price for the given ticker symbol.    
        Returns the latest closing price as a float.    
    """    
    try:    
        ticker = yf.Ticker(symbol)        
        # Get today's historical data; may return empty if market is closed or symbol is invalid.        
        data = ticker.history(period="1d")        
        if not data.empty:      
            # Use the last closing price from today's data            
            price = data['Close'].iloc[-1]            
            return float(price)        
        else:       
            # As a fallback, try using the regular market price from the ticker info            
            info = ticker.info            
            price = info.get("regularMarketPrice", None)            
            if price is not None:            
                return float(price)            
            else:            
                return -1.0  # Indicate failure    
    except Exception:   
        # Return -1.0 to indicate an error occurred when fetching the stock price        
        return -1.0


def get_stock_history(symbol: str, period: str ) -> str:
    """    
    Retrieve historical data for a stock given a ticker symbol and a period.    
    Returns the historical data as a CSV formatted string.        
    
    Parameters:    
        symbol: The stock ticker symbol.        
        period: The period over which to retrieve historical data (e.g., '1mo', '3mo', '1y').    
    """    
    try:     
        ticker = yf.Ticker(symbol)        
        data = ticker.history(period=period)        
        if data.empty:       
            return f"No historical data found for symbol '{symbol}' with period '{period}'."        
        # Convert the DataFrame to a CSV formatted string        
        csv_data = data.to_csv()        
        return csv_data    
    except Exception as e:    
        return f"Error fetching historical data: {str(e)}"

def compare_stocks(symbol1: str, symbol2: str) -> str:
    """    
    Compare the current stock prices of two ticker symbols.    
    Returns a formatted message comparing the two stock prices.        
    
    Parameters:    
        symbol1: The first stock ticker symbol.        
        symbol2: The second stock ticker symbol.    
    """    
    price1 = get_stock_price(symbol1)    
    price2 = get_stock_price(symbol2)    
    if price1 < 0 or price2 < 0:    
        return f"Error: Could not retrieve data for comparison of '{symbol1}' and '{symbol2}'."    
    if price1 > price2:    
        result = f"{symbol1} (${price1:.2f}) is higher than {symbol2} (${price2:.2f})."    
    elif price1 < price2:    
        result = f"{symbol1} (${price1:.2f}) is lower than {symbol2} (${price2:.2f})."    
    else:    
        result = f"Both {symbol1} and {symbol2} have the same price (${price1:.2f})."    
    return result


MODEL=LiteLlm(
        model=model_name_at_endpoint,
        api_base=api_base_url,
    )

root_agent = LlmAgent(
    name="financial_assistant",
    model=MODEL,
    description=(
        "Navigate the world of finance with confidence. This agent is designed to be your all-in-one partner for managing and understanding your money. From real-time market updates to complex financial analysis, it provides the tools and insights you need to make informed decisions."
    ),
    instruction=prompt.FINANCIAL_ASSISTANT_PROMPT,
    output_key="assistant_output",
    tools=[get_stock_price, get_stock_history, compare_stocks]
)