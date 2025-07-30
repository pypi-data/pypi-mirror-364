from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel
from dateutil.parser import parse


def parse_datetime_string(value):
    """Utility function to parse datetime strings."""
    if isinstance(value, str):
        return parse(value)
    return value


# Exchange Info Models
class SettlementInfo(BaseModel):
    """Settlement information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    type: str
    duration_value: str
    duration_unit: str


class SymbolInfo(BaseModel):
    """Symbol information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    symbol: str
    tick_size: str
    max_order_notional: str
    max_taker_price_deviation: str
    min_order_size: str
    kind: str = Field(
        ..., description="SingleNamePerpetual, IndexFundPerpetual, FixedExpiryFuture"
    )


class ExchangeInfo(BaseModel):
    """Exchange information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    settlements_info: List[SettlementInfo]
    assets: List[str]
    symbols: List[SymbolInfo]


class ExchangeInfoResponse(BaseModel):
    """Response model for exchange info endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: ExchangeInfo
    success: bool
    timestamp: int


# Ping Response
class PingResponse(BaseModel):
    """Response model for ping endpoint."""

    model_config = ConfigDict(extra="allow")

    # The ping endpoint returns an empty object on success
    # We'll allow extra fields in case the response changes in the future


# Symbols Models
class Symbol(BaseModel):
    """Tradable product symbol model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    kind: int = Field(
        ..., description="0: Perpetual Market, 2: Index Market, 4: Futures Market"
    )
    symbol: str
    name: str
    is_active: bool
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class SymbolsResponse(BaseModel):
    """Response model for symbols endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[Symbol]
    success: bool
    timestamp: int


# Server Time Model
class ServerTimeResponse(BaseModel):
    """Response model for server time endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    server_time: int


# Epoch History Models
class Epoch(BaseModel):
    """Epoch data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value) if value is not None else None


class EpochHistoryResponse(BaseModel):
    """Response model for epoch history endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[Epoch]
    success: bool
    timestamp: int


# Insurance Fund History Models
class InsuranceFund(BaseModel):
    """Insurance fund update data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    epoch_id: int
    tx_ordinal: int
    symbol: str
    total_capitalization: Optional[str] = None
    kind: int = Field(
        ..., description="0: fill, 1: liquidation, 2: deposit, 3: withdrawal"
    )
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class InsuranceFundHistoryResponse(BaseModel):
    """Response model for insurance fund history endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_epoch: Optional[int] = None
    next_tx_ordinal: Optional[int] = None
    next_ordinal: Optional[int] = None
    value: List[InsuranceFund]
    success: bool
    timestamp: int


# Specs Models
class Spec(BaseModel):
    """Spec data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    kind: int = Field(..., description="0: Market, 1: MarketGateway")
    name: str
    expr: str
    value: Any


class SpecsResponse(BaseModel):
    """Response model for specs endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[Spec]
    success: bool
    timestamp: int


# Exchange Status Models
class OnChainCheckpoint(BaseModel):
    """On-chain checkpoint information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    latest_on_chain_checkpoint: int
    latest_checkpoint_transaction_link: Optional[str] = None


class ExchangeStatus(BaseModel):
    """Exchange status information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    current_epoch: str
    latest_on_chain_checkpoint: Optional[OnChainCheckpoint] = None
    active_addresses: int


class ExchangeStatusResponse(BaseModel):
    """Response model for exchange status endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: ExchangeStatus
    success: bool
    timestamp: int


# DDX Supply Models
class DDXSupply(BaseModel):
    """DDX supply information model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    circulating_supply: str


class DDXSupplyResponse(BaseModel):
    """Response model for DDX supply endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: DDXSupply
    success: bool
    timestamp: int


# Tradable Products Models
class TradableProduct(BaseModel):
    """Tradable product data model."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    kind: int = Field(
        ..., description="0: Perpetual Market, 2: Index Market, 4: Futures Market"
    )
    symbol: str
    name: str
    is_active: bool
    created_at: datetime

    @field_validator("created_at", mode="before")
    @classmethod
    def parse_datetime_field(cls, value):
        return parse_datetime_string(value)


class TradableProductsResponse(BaseModel):
    """Response model for tradable products endpoint."""

    model_config = ConfigDict(populate_by_name=True)

    value: List[TradableProduct]
    success: bool
    timestamp: int


# Aggregation Models
class CollateralAggregation(BaseModel):
    """Collateral aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    timestamp: int

    def get_collateral_value(self, field_name: str) -> Optional[str]:
        """Get value for a specific collateral field."""
        return getattr(self, f"collateral_{field_name}", None)


class CollateralAggregationResponse(BaseModel):
    """Response model for collateral aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_starting_value: Optional[str] = None
    value: List[CollateralAggregation]
    success: bool
    timestamp: int


class DDXAggregation(BaseModel):
    """DDX aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    timestamp: int

    def get_ddx_value(self, value_type: str) -> Optional[str]:
        """Get DDX value for a specific type."""
        return getattr(self, f"ddx_{value_type}", None)


class DDXAggregationResponse(BaseModel):
    """Response model for DDX aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_starting_value: Optional[str] = None
    value: List[DDXAggregation]
    success: bool
    timestamp: int


class InsuranceFundAggregation(BaseModel):
    """Insurance fund aggregation data model."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    timestamp: int

    def get_insurance_fund_value(self, field_name: str) -> Optional[str]:
        """Get value for a specific insurance fund field."""
        return getattr(self, f"insurance_fund_{field_name}", None)


class InsuranceFundAggregationResponse(BaseModel):
    """Response model for insurance fund aggregation endpoint."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    next_starting_value: Optional[str] = None
    value: List[InsuranceFundAggregation]
    success: bool
    timestamp: int


# Deployment Models
class DeploymentAddresses(BaseModel):
    """Model for contract deployment addresses."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    ddx_address: str
    ddx_wallet_cloneable_address: str
    derivadex_address: str = Field(alias="derivaDEXAddress")
    di_fund_token_factory_address: str
    governance_address: str
    insurance_fund_address: str
    pause_address: str
    trader_address: str
    usdt_address: str
    ausdt_address: str
    cusdt_address: str
    usdc_address: str
    cusdc_address: str
    ausdc_address: str
    husd_address: str
    gusd_address: str
    gnosis_safe_address: str
    gnosis_safe_proxy_factory_address: str
    gnosis_safe_proxy_address: str
    create_call_address: str
    banner_address: str
    funded_insurance_fund_address: str
    funded_insurance_fund_dip12_address: str
    checkpoint_address: str
    registration_address: str
    initialize_app_address: str
    specs_address: str
    collateral_address: str
    collateral_dip12_address: str
    custodian_address: str
    reject_address: str
    stake_address: str
    stake_dip12_address: str
    pilot_reset_address: str


class DeploymentInfo(BaseModel):
    """Model for deployment information."""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    addresses: DeploymentAddresses
    chain_id: int
    eth_rpc_url: str
