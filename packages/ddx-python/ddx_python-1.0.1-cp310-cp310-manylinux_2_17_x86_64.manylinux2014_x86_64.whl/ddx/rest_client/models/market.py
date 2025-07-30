from datetime import datetime
from enum import IntEnum
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from dateutil.parser import parse
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from ddx._rust.decimal import Decimal


def parse_datetime_string(value):
    """Utility function to parse datetime strings."""
    if isinstance(value, str):
        return parse(value)
    return value


# Enums
class OrderSide(IntEnum):
    """Order side enum."""

    BID = 0
    ASK = 1


class OrderType(IntEnum):
    """Order type enum."""

    LIMIT = 0
    MARKET = 1
    STOP = 2
    LIMIT_POST_ONLY = 3


class OrderUpdateReason(IntEnum):
    """Order update reason enum."""

    TRADE = 0
    LIQUIDATION = 1
    CANCEL = 2
    ORDER_REJECTION = 3
    CANCEL_REJECTION = 4


class StrategyUpdateReason(IntEnum):
    """Strategy update reason enum."""

    DEPOSIT = 0
    WITHDRAW = 1
    WITHDRAW_INTENT = 2
    FUNDING_PAYMENT = 3
    REALIZED_PNL = 4
    LIQUIDATION = 5
    ADL = 6
    WITHDRAW_REJECTION = 7


class TraderUpdateReason(IntEnum):
    """Trader update reason enum."""

    DEPOSIT = 0
    WITHDRAW_DDX = 1
    WITHDRAW_DDX_INTENT = 2
    TRADE_MINING_REWARD = 3
    PROFILE_UPDATE = 4
    FEE_DISTRIBUTION = 5
    WITHDRAW_DDX_REJECTION = 6


# Mark Price History Models
class MarkPrice(BaseModel):
    """Mark price data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    global_ordinal: int
    epoch_id: int
    symbol: str
    price: str
    funding_rate: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class MarkPriceHistoryResponse(BaseModel):
    """Response model for mark price history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_global_ordinal: Optional[int] = None
    value: List[MarkPrice]
    success: bool
    timestamp: int


# Order Book L3 Models
class OrderBookL3(BaseModel):
    """L3 order book entry model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    book_ordinal: int
    order_hash: str
    symbol: str
    side: int = Field(..., description="0: Bid, 1: Ask")
    original_amount: str
    amount: str
    price: str
    trader_address: str
    strategy_id_hash: str


class OrderBookL3Response(BaseModel):
    """Response model for L3 order book endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[OrderBookL3]
    success: bool
    timestamp: int


# Order Update History Models
class OrderIntent(BaseModel):
    """Order intent data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    order_hash: str
    symbol: str
    side: int = Field(..., description="0: Bid, 1: Ask")
    amount: str
    price: str
    trader_address: str
    strategy_id_hash: str
    order_type: int = Field(
        ..., description="0: Limit, 1: Market, 2: Stop, 3: LimitPostOnly"
    )
    stop_price: str
    nonce: str
    signature: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class OrderUpdate(BaseModel):
    """Order update data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    global_ordinal: int
    epoch_id: int
    tx_ordinal: Optional[int] = None
    ordinal: Optional[int] = None
    order_rejection: Optional[int] = Field(
        None, description="0-5: only applicable when rejection"
    )
    cancel_rejection: Optional[int] = None
    reason: int = Field(
        ...,
        description="0: Trade, 1: Liquidation, 2: Cancel, 3: Order Rejection, 4: Cancel Rejection",
    )
    amount: str
    quote_asset_amount: Optional[str] = None
    symbol: str
    price: Optional[str] = None
    maker_fee_collateral: Optional[str] = None
    maker_fee_ddx: Optional[str] = None
    maker_realized_pnl: Optional[str] = None
    taker_order_intent: Optional[OrderIntent] = None
    taker_fee_collateral: Optional[str] = None
    taker_fee_ddx: Optional[str] = None
    taker_realized_pnl: Optional[str] = None
    liquidated_trader_address: Optional[str] = None
    liquidated_strategy_id_hash: Optional[str] = None
    maker_order_intent: OrderIntent
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class OrderUpdateHistoryResponse(BaseModel):
    """Response model for order update history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_global_ordinal: Optional[int] = None
    value: List[OrderUpdate]
    success: bool
    timestamp: int


# Strategy Update History Models
class StrategyPosition(BaseModel):
    """Strategy position data within a strategy update."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    side: Optional[int] = Field(
        None, description="0: Bid, 1: Ask. Only present on ADL strategy update"
    )
    avg_entry_price: Optional[str] = Field(
        None, description="New average entry price after RealizedPnl strategy update"
    )
    realized_pnl: str = Field(
        ..., description="Realized PnL after RealizedPnl or ADL strategy update"
    )


class StrategyUpdate(BaseModel):
    """Strategy update data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    global_ordinal: int
    epoch_id: int
    tx_ordinal: Optional[int] = None
    ordinal: Optional[int] = None
    withdraw_rejection: Optional[int] = Field(
        None, description="0-4: Withdraw rejection type. Only present on rejections"
    )
    reason: int = Field(
        ...,
        description="0: Deposit, 1: Withdraw, 2: WithdrawIntent, 3: FundingPayment, 4: RealizedPnl, 5: Liquidation, 6: ADL, 7: Withdraw Rejection",
    )
    trader_address: str
    strategy_id_hash: str
    collateral_address: Optional[str] = None
    collateral_symbol: Optional[str] = None
    amount: Optional[str] = None
    new_avail_collateral: Optional[str] = Field(
        None, description="Not present on ADL reason"
    )
    new_locked_collateral: Optional[str] = Field(
        None, description="Not present on ADL reason"
    )
    block_number: Optional[int] = Field(None, description="Not present on ADL reason")
    tx_hash: Optional[str] = None
    positions: Optional[List[StrategyPosition]] = None
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class StrategyUpdateHistoryResponse(BaseModel):
    """Response model for strategy update history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_global_ordinal: Optional[int] = None
    value: List[StrategyUpdate]
    success: bool
    timestamp: int


# Ticker Models
class Ticker(BaseModel):
    """Market ticker data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    high_price_24h: str
    low_price_24h: str
    prev_price_24h: str
    last_price: str
    mark_price: str
    index_price: str
    next_funding_time: datetime
    volume_24h: str
    amount_24h: Optional[str] = None
    funding_rate: str
    open_interest: str
    open_interest_value: str

    @field_validator("next_funding_time", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class TickersResponse(BaseModel):
    """Response model for tickers endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[Ticker]
    success: bool
    timestamp: int


# Trader Update History Models
class TraderUpdate(BaseModel):
    """Trader update data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    global_ordinal: int
    epoch_id: int
    tx_ordinal: Optional[int] = None
    ordinal: Optional[int] = None
    withdraw_ddx_rejection: Optional[int] = Field(
        None, description="0-1: only present on rejections"
    )
    reason: int = Field(
        ...,
        description="0: Deposit, 1: WithdrawDDX, 2: WithdrawDDXIntent, 3: TradeMiningReward, 4: ProfileUpdate, 5: FeeDistribution, 6: WithdrawDDXRejection",
    )
    trader_address: str
    amount: Optional[str] = None
    new_avail_ddx_balance: Optional[str] = None
    new_locked_ddx_balance: Optional[str] = None
    pay_fees_in_ddx: Optional[bool] = None
    block_number: Optional[int] = None
    tx_hash: Optional[str] = None
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class TraderUpdateHistoryResponse(BaseModel):
    """Response model for trader update history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_global_ordinal: Optional[int] = None
    value: List[TraderUpdate]
    success: bool
    timestamp: int


# Balance Aggregation Models
class BalanceAggregation(BaseModel):
    """Balance aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    trader: str
    strategy_id_hash: str
    amount: str
    timestamp: int


class BalanceAggregationResponse(BaseModel):
    """Response model for balance aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[BalanceAggregation]
    success: bool
    timestamp: int


# Fees Aggregation Models
class FeesAggregation(BaseModel):
    """Fees aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    timestamp: int

    def get_fees_value(self, fee_symbol: str) -> Optional[str]:
        """Get fees value for a specific fee symbol (e.g., 'USDC', 'DDX')."""
        return getattr(self, f"fees_{fee_symbol}", None)


class FeesAggregationResponse(BaseModel):
    """Response model for fees aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_lookback_timestamp: Optional[int] = None
    value: List[FeesAggregation]
    success: bool
    timestamp: int


# Funding Rate Comparison Models
class FundingRateComparison(BaseModel):
    """Funding rate comparison data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    derivadex_funding_rate: float
    binance_funding_rate: float
    derivadex_binance_arbitrage: float
    bybit_funding_rate: float
    derivadex_bybit_arbitrage: float
    hyperliquid_funding_rate: float
    derivadex_hyperliquid_arbitrage: float


class FundingRateComparisonResponse(BaseModel):
    """Response model for funding rate comparison aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[FundingRateComparison]
    success: bool
    timestamp: int


# Top Traders Models
class TopTrader(BaseModel):
    """Top trader data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    trader: str
    volume: Optional[str] = None
    realized_pnl: Optional[str] = None
    account_value: Optional[str] = None


class TopTradersAggregationResponse(BaseModel):
    """Response model for top traders aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    value: List[TopTrader]
    next_cursor: Optional[int] = None
    success: bool
    timestamp: int


# Volume Aggregation Models
class VolumeAggregation(BaseModel):
    """Volume aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    timestamp: int

    def get_volume_value(self, field_name: str) -> Optional[str]:
        """Get value for a specific volume field."""
        return getattr(self, f"volume_{field_name}", None)


class VolumeAggregationResponse(BaseModel):
    """Response model for volume aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_lookback_timestamp: Optional[int] = None
    value: List[VolumeAggregation]
    success: bool
    timestamp: int


# Funding Rate History Models
class FundingRateHistory(BaseModel):
    """Funding rate history data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    tx_ordinal: int
    symbol: str
    funding_rate: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class FundingRateHistoryResponse(BaseModel):
    """Response model for funding rate history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_epoch: Optional[int] = None
    next_tx_ordinal: Optional[int] = None
    next_ordinal: Optional[int] = None
    value: List[FundingRateHistory]
    success: bool
    timestamp: int


# Open Interest History Models
class OpenInterestHistory(BaseModel):
    """Open interest history data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    amount: str
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class OpenInterestHistoryResponse(BaseModel):
    """Response model for open interest history endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[OpenInterestHistory]
    success: bool
    timestamp: int


# Order Book L2 Models
class OrderBookL2Item(BaseModel):
    """L2 order book item model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    side: int = Field(..., description="0: Bid, 1: Ask")
    amount: str
    price: str


class OrderBookL2Response(BaseModel):
    """Response model for L2 order book endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[OrderBookL2Item]
    success: bool
    timestamp: int


@dataclass
class OrderBook:
    """
    Complete order book for a single market.

    Attributes
    ----------
    symbol : str
        The symbol of the market
    bids : List[OrderBookL2Item]
        List of bid orders, sorted by price (descending)
    asks : List[OrderBookL2Item]
        List of ask orders, sorted by price (ascending)
    timestamp : int
        Timestamp of the order book snapshot
    """

    symbol: str
    bids: List[OrderBookL2Item]
    asks: List[OrderBookL2Item]
    timestamp: int

    @classmethod
    def from_order_book_l2_items(
        cls, symbol: str, order_book_l2_items: List[OrderBookL2Item], timestamp: int
    ) -> "OrderBook":
        """
        Create instance from a list of entries for a single symbol.

        Parameters
        ----------
        symbol : str
            The market symbol
        order_book_l2_items : List[OrderBookL2Item]
            List of order book entries for this symbol
        timestamp : int
            Timestamp of the order book snapshot

        Returns
        -------
        OrderBook
            Initialized instance
        """
        # Filter and sort bids (descending by price)
        bids = [e for e in order_book_l2_items if e.side == OrderSide.BID]
        bids.sort(key=lambda x: Decimal(x.price), reverse=True)

        # Filter and sort asks (ascending by price)
        asks = [e for e in order_book_l2_items if e.side == OrderSide.ASK]
        asks.sort(key=lambda x: Decimal(x.price))

        return cls(symbol=symbol, bids=bids, asks=asks, timestamp=timestamp)

    @classmethod
    def from_response(
        cls, response: OrderBookL2Response, symbol: Optional[str] = None
    ) -> Dict[str, "OrderBook"]:
        """
        Create OrderBook instance(s) from response data.

        Parameters
        ----------
        response : OrderBookL2Response
            Parsed response from the API
        symbol : Optional[str]
            If provided, only return order book for this symbol

        Returns
        -------
        Dict[str, OrderBook]
            Dictionary mapping symbols to their respective order books
        """
        if not response.value:
            return {}

        # If specific symbol requested, filter first
        items = response.value
        if symbol:
            items = [item for item in items if item.symbol == symbol]
            if not items:
                return {}

        # Group entries by symbol
        items_sorted = sorted(items, key=attrgetter("symbol"))
        grouped = groupby(items_sorted, key=attrgetter("symbol"))

        # Create order books for each symbol
        order_books = {}
        for sym, entries in grouped:
            entry_list = list(entries)
            if entry_list:  # Only create order book if there are entries
                order_books[sym] = cls.from_order_book_l2_items(
                    sym, entry_list, response.timestamp
                )

        return order_books


# Price Checkpoint History Models
class PriceCheckpoint(BaseModel):
    """Price checkpoint data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    tx_ordinal: int
    index_price_hash: str
    symbol: str
    index_price: str
    mark_price: str
    time: str
    ema: Optional[str] = None
    price_ordinal: int
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class PriceCheckpointHistoryResponse(BaseModel):
    """Response model for price checkpoint history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_epoch: Optional[int] = None
    next_tx_ordinal: Optional[int] = None
    next_ordinal: Optional[int] = None
    value: List[PriceCheckpoint]
    success: bool
    timestamp: int
