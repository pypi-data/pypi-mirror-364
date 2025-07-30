"""Order-related type definitions."""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class Order(BaseModel):
    """Basic order structure."""
    
    symbol: str = Field(..., description="Trading symbol")
    side: Literal["buy", "sell"] = Field(..., description="Order side")
    quantity: float = Field(..., description="Order quantity")
    type_: Literal["market", "limit", "stop", "stop_limit"] = Field(..., alias="type", description="Order type")
    price: Optional[float] = Field(None, description="Order price")
    stop_price: Optional[float] = Field(None, description="Stop price")
    time_in_force: Literal["day", "gtc", "opg", "cls", "ioc", "fok"] = Field(..., description="Time in force")
    
    model_config = {"populate_by_name": True}


class OptionsOrder(Order):
    """Options-specific order."""
    
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    strike_price: float = Field(..., description="Strike price")
    expiration_date: str = Field(..., description="Expiration date")


class CryptoOrderOptions(BaseModel):
    """Crypto order options."""
    
    quantity: Optional[float] = Field(None, description="Quantity")
    notional: Optional[float] = Field(None, description="Notional value")


class OptionsOrderOptions(BaseModel):
    """Options order options."""
    
    strike_price: float = Field(..., description="Strike price")
    expiration_date: str = Field(..., description="Expiration date")
    option_type: Literal["call", "put"] = Field(..., description="Option type")
    contract_size: Optional[int] = Field(None, description="Contract size")


class OrderResponse(BaseModel):
    """Order response from API."""
    
    success: bool = Field(..., description="Order success status")
    response_data: dict = Field(..., description="Order response data")
    message: str = Field(..., description="Response message")
    status_code: int = Field(..., description="HTTP status code")


class BrokerOrderParams(BaseModel):
    """Broker order parameters."""
    
    broker: Literal["robinhood", "tasty_trade", "ninja_trader"] = Field(..., description="Broker name")
    account_number: str = Field(..., description="Account number")
    symbol: str = Field(..., description="Trading symbol")
    order_qty: float = Field(..., description="Order quantity")
    action: Literal["Buy", "Sell"] = Field(..., description="Order action")
    order_type: Literal["Market", "Limit", "Stop", "TrailingStop"] = Field(..., description="Order type")
    asset_type: Literal["Equity", "Equity Option", "Crypto", "Futures", "Futures Option"] = Field(..., description="Asset type")
    time_in_force: Literal["day", "gtc", "gtd", "ioc", "fok"] = Field(..., description="Time in force")
    price: Optional[float] = Field(None, description="Order price")
    stop_price: Optional[float] = Field(None, description="Stop price")


class BrokerExtras(BaseModel):
    """Broker-specific extras for orders."""
    
    robinhood: Optional[dict] = Field(None, description="Robinhood-specific options")
    ninja_trader: Optional[dict] = Field(None, description="NinjaTrader-specific options")
    tasty_trade: Optional[dict] = Field(None, description="TastyTrade-specific options") 