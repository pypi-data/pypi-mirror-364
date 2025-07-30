from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from datetime import datetime
from dateutil.parser import parse


def parse_datetime_string(value):
    """Utility function to parse datetime strings."""
    if isinstance(value, str):
        return parse(value)
    return value


# Strategy Fees History Models
class Fee(BaseModel):
    """Strategy fee data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    tx_ordinal: int
    ordinal: int
    amount: str
    fee_symbol: str
    symbol: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class FeesHistoryResponse(BaseModel):
    """Response model for strategy fees history endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    next_epoch: Optional[int] = None
    next_tx_ordinal: Optional[int] = None
    next_ordinal: Optional[int] = None
    value: List[Fee]
    success: bool
    timestamp: int


# Strategy Positions Models
class Position(BaseModel):
    """Position data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    trader: str
    symbol: str
    strategy_id_hash: str
    side: int = Field(..., description="0: None, 1: Long, 2: Short")
    balance: str
    avg_entry_price: str
    last_modified_in_epoch: Optional[int] = None


class PositionsResponse(BaseModel):
    """Response model for strategy positions endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[Position]
    success: bool
    timestamp: int


# Strategy Models
class Strategy(BaseModel):
    """Strategy data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    trader: str
    strategy_id_hash: str
    strategy_id: str
    max_leverage: int
    avail_collateral: str
    locked_collateral: str
    frozen: bool


class StrategyResponse(BaseModel):
    """Response model for strategy endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: Optional[Strategy] = None
    success: bool
    timestamp: int


# Strategy Metrics Models
class StrategyMetrics(BaseModel):
    """Strategy metrics data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    margin_fraction: str
    mmr: str
    leverage: str
    strategy_margin: str
    strategy_value: str


class StrategyMetricsResponse(BaseModel):
    """Response model for strategy metrics endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: Optional[StrategyMetrics] = None
    success: bool
    timestamp: int


# Trader Models
class Trader(BaseModel):
    """Trader data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    trader: str
    avail_ddx: str
    locked_ddx: str
    pay_fees_in_ddx: bool


class TraderResponse(BaseModel):
    """Response model for trader endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: Optional[Trader] = None
    success: bool
    timestamp: int
