// TODO: proceduralize these macros for cleaner code
use super::*;

pub mod python {
    use super::{
        Balance, BookOrder, EpochMetadata, ITEM_BOOK_ORDER, ITEM_EMPTY, ITEM_EPOCH_METADATA,
        ITEM_INSURANCE_FUND, ITEM_INSURANCE_FUND_CONTRIBUTION, ITEM_POSITION, ITEM_PRICE,
        ITEM_SIGNER, ITEM_SPECS, ITEM_STATS, ITEM_STRATEGY, ITEM_TRADABLE_PRODUCT, ITEM_TRADER,
        InsuranceFundContribution, Item as RustItem, Position, Price, ReleaseHash, SpecsExpr,
        Stats, Strategy, TradableProduct, TradableProductParameters, Trader, VoidableItem,
    };
    #[cfg(feature = "fixed_expiry_future")]
    use crate::specs::quarterly_expiry_future::Quarter;
    #[cfg(feature = "insurance_fund_client_req")]
    use crate::types::request::InsuranceFundWithdrawIntent;
    use crate::{
        specs::{
            ProductSpecs,
            types::{SpecsKey, SpecsKind},
        },
        tree::{
            shared_smt::{SharedSparseMerkleTree, exported::python::H256, from_genesis},
            shared_store::ConcurrentStore,
        },
        types::{
            accounting::{MarkPriceMetadata, PriceMetadata, TradeSide},
            identifiers::{
                BookOrderKey, EpochMetadataKey, InsuranceFundContributorAddress, InsuranceFundKey,
                PositionKey, PriceKey, SignerAddress, StatsKey, StrategyIdHash, StrategyKey,
                VerifiedStateKey,
            },
            primitives::{
                IndexPriceHash, OrderHash, Product, ProductSymbol as RustProductSymbol,
                UnderlyingSymbol,
            },
            request::{
                AdvanceEpoch, AdvanceSettlementEpoch, Block, CancelAllIntent, CancelOrderIntent,
                ClientRequest, Cmd, CmdTimeValue, IndexPrice, MatchableIntent, MintPriceCheckpoint,
                ModifyOrderIntent, OrderIntent, OrderType as RustOrderType, ProfileUpdateIntent,
                Request, SettlementAction as RustSettlementAction, UpdateProductListings,
                WithdrawDDXIntent, WithdrawIntent,
            },
            state::TradableProductKey,
            transaction::{InsuranceFundUpdateKind, StrategyUpdateKind, TraderUpdateKind},
        },
    };
    use alloy_dyn_abi::{DynSolType, DynSolValue};
    #[cfg(feature = "fixed_expiry_future")]
    use chrono::prelude::*;
    use core_common::{
        Address,
        global::ApplicationContext,
        types::{
            accounting::StrategyId,
            exported::python::CoreCommonError,
            primitives::{
                Hash, TokenSymbol, TraderAddress, UnscaledI128, exported::python::Decimal,
            },
        },
        util::tokenize::Tokenizable,
    };
    use core_crypto::eip712::{HashEIP712, SignedEIP712};
    use lazy_static::lazy_static;
    use pyo3::{
        IntoPyObjectExt,
        exceptions::PyValueError,
        prelude::*,
        types::{PyDict, PyType},
    };
    use pyo3_stub_gen::derive::*;
    use pythonize;
    use sparse_merkle_tree::{
        CompiledMerkleProof, H256 as RustH256, traits::Value, tree::LeafNode,
    };
    #[cfg(feature = "index_fund")]
    use std::collections::BTreeMap;
    use std::{borrow::Cow, collections::HashMap, fmt, str::FromStr};

    /// Get the operator application context for this DerivaDEX instance.
    #[gen_stub_pyfunction]
    #[pyfunction]
    pub fn get_operator_context() -> ApplicationContext {
        core_common::global::app_context().clone()
    }

    /// Reinitialize the operator application context for this DerivaDEX instance.
    #[gen_stub_pyfunction]
    #[pyfunction]
    pub fn reinit_operator_context() {
        core_common::global::reinit_app_context_from_env()
    }

    // GENERAL TYPES------------------------------------------------------------

    #[gen_stub_pyclass]
    #[pyclass(frozen, eq, ord, hash, str)]
    #[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, std::hash::Hash, Debug)]
    pub struct ProductSymbol {
        inner: RustProductSymbol,
    }

    #[cfg_eval]
    #[gen_stub_pymethods]
    #[pymethods]
    impl ProductSymbol {
        /// Construct a product symbol from a string representation such as `"ETHP"`.
        /// Returns an error if the supplied string cannot be parsed.
        #[new]
        fn new(symbol: &str) -> PyResult<Self> {
            Ok(Self {
                inner: RustProductSymbol::from_str(symbol)?,
            })
        }

        fn __deepcopy__(&self, _memo: &Bound<'_, PyDict>) -> Self {
            *self
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        fn __len__(&self) -> usize {
            self.inner.0.len()
        }

        /// Return `true` when this symbol represents a perpetual contract.
        fn is_perpetual(&self) -> bool {
            matches!(self.inner.product(), Product::Perpetual)
        }

        #[cfg(feature = "fixed_expiry_future")]
        /// Return `true` when this symbol corresponds to a fixed-expiry future.
        fn is_future(&self) -> bool {
            matches!(self.inner.product(), Product::QuarterlyExpiryFuture { .. })
        }

        #[cfg(feature = "fixed_expiry_future")]
        /// For futures symbols, return the associated `Quarter`; otherwise `None`.
        fn futures_quarter(&self) -> Option<Quarter> {
            match self.inner.product() {
                Product::QuarterlyExpiryFuture { month_code } => Some(month_code.into()),
                _ => None,
            }
        }

        /// Construct a `PriceMetadata` value appropriate for this product type.
        fn price_metadata(&self) -> PriceMetadata {
            match self.inner.product() {
                // TODO: distinguish between single and index perps
                Product::Perpetual => PriceMetadata::SingleNamePerpetual(),
                #[cfg(feature = "fixed_expiry_future")]
                Product::QuarterlyExpiryFuture { .. } => PriceMetadata::QuarterlyExpiryFuture(),
            }
        }
    }

    impl fmt::Display for ProductSymbol {
        fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
            write!(f, "{}", self.inner)
        }
    }

    impl From<RustProductSymbol> for ProductSymbol {
        fn from(symbol: RustProductSymbol) -> Self {
            Self { inner: symbol }
        }
    }

    impl From<ProductSymbol> for RustProductSymbol {
        fn from(symbol: ProductSymbol) -> Self {
            symbol.inner
        }
    }

    #[gen_stub_pyclass]
    #[pyclass(frozen, eq)]
    #[derive(Clone, Copy, PartialEq, Eq, Debug)]
    pub struct OrderType {
        inner: RustOrderType,
    }

    #[allow(non_upper_case_globals)]
    #[gen_stub_pymethods]
    #[pymethods]
    impl OrderType {
        #[classattr]
        const Limit: Self = Self {
            inner: RustOrderType::Limit { post_only: false },
        };

        #[classattr]
        const Market: Self = Self {
            inner: RustOrderType::Market,
        };

        #[classattr]
        const StopLimit: Self = Self {
            inner: RustOrderType::StopLimit,
        };

        #[classattr]
        const PostOnlyLimit: Self = Self {
            inner: RustOrderType::Limit { post_only: true },
        };

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }
    }

    impl From<RustOrderType> for OrderType {
        fn from(order_type: RustOrderType) -> Self {
            Self { inner: order_type }
        }
    }

    impl From<OrderType> for RustOrderType {
        fn from(order_type: OrderType) -> Self {
            order_type.inner
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl TradeSide {
        /// Compute the trading fee for the given `amount` at `price` on this side.
        #[pyo3(name = "trading_fee")]
        fn trading_fee_py(&self, amount: Decimal, price: Decimal) -> Decimal {
            self.trading_fee(amount.into(), price.into()).into()
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl SpecsKind {
        /// Parse a `SpecsKind` from its string representation.
        #[new]
        fn new(kind: &str) -> PyResult<Self> {
            Self::from_str(kind).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl InsuranceFundUpdateKind {
        /// Parse an `InsuranceFundUpdateKind` from its string discriminant.
        #[new]
        fn new(name: &str) -> PyResult<Self> {
            Self::from_str(name).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl TraderUpdateKind {
        /// Parse a `TraderUpdateKind` from its string discriminant.
        #[new]
        fn new(name: &str) -> PyResult<Self> {
            Self::from_str(name).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl StrategyUpdateKind {
        /// Parse a `StrategyUpdateKind` from its string discriminant.
        #[new]
        fn new(name: &str) -> PyResult<Self> {
            Self::from_str(name).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl ProductSpecs {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        /// Return the list of underlying symbols referenced by this specification.
        #[pyo3(name = "underlying_symbols")]
        fn underlying_symbols_py(&self) -> Vec<UnderlyingSymbol> {
            self.underlying_symbols()
        }

        #[getter(tick_size)]
        fn tick_size_py(&self) -> UnscaledI128 {
            self.tick_size()
        }

        #[getter(max_order_notional)]
        fn max_order_notional_py(&self) -> UnscaledI128 {
            self.max_order_notional()
        }

        #[getter(max_taker_price_deviation)]
        fn max_taker_price_deviation_py(&self) -> UnscaledI128 {
            self.max_taker_price_deviation()
        }

        #[getter(min_order_size)]
        fn min_order_size_py(&self) -> UnscaledI128 {
            self.min_order_size()
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl MarkPriceMetadata {
        #[getter]
        fn ema(&self) -> Option<UnscaledI128> {
            #[allow(unreachable_patterns)]
            match self {
                MarkPriceMetadata::Ema(ema) => Some(*ema),
                _ => None,
            }
        }

        /// Deserialize `MarkPriceMetadata` from the operator serialization.
        #[classmethod]
        fn from_dict(_cls: &Bound<'_, PyType>, ob: &Bound<'_, PyAny>) -> PyResult<Self> {
            pythonize::depythonize(ob).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        fn __deepcopy__(&self, _memo: &Bound<'_, PyDict>) -> Self {
            *self
        }
    }

    #[cfg_eval]
    #[gen_stub_pymethods]
    #[pymethods]
    impl PriceMetadata {
        #[cfg(feature = "index_fund")]
        #[getter]
        fn weights(&self) -> Option<BTreeMap<UnderlyingSymbol, UnscaledI128>> {
            #[allow(unreachable_patterns)]
            match self {
                PriceMetadata::IndexFundPerpetual(weights) => Some(weights.clone()),
                _ => None,
            }
        }

        /// Deserialize `PriceMetadata` from the operator serialization.
        #[classmethod]
        fn from_dict(_cls: &Bound<'_, PyType>, ob: &Bound<'_, PyAny>) -> PyResult<Self> {
            pythonize::depythonize(ob).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }
    }

    #[cfg_eval]
    #[gen_stub_pymethods]
    #[pymethods]
    impl TradableProductParameters {
        #[cfg(feature = "fixed_expiry_future")]
        #[getter]
        fn quarter(&self) -> Option<Quarter> {
            #[allow(unreachable_patterns)]
            match self {
                TradableProductParameters::QuarterlyExpiryFuture(quarter) => Some(*quarter),
                _ => None,
            }
        }

        /// Deserialize `TradableProductParameters` from the operator serialization.
        #[classmethod]
        fn from_dict(_cls: &Bound<'_, PyType>, ob: &Bound<'_, PyAny>) -> PyResult<Self> {
            pythonize::depythonize(ob).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }
    }

    #[gen_stub_pyclass]
    #[pyclass(frozen, eq, hash)]
    #[derive(Clone, PartialEq, Eq, std::hash::Hash, Debug)]
    pub struct SettlementAction {
        inner: RustSettlementAction,
    }

    #[cfg_eval]
    #[allow(non_upper_case_globals)]
    #[gen_stub_pymethods]
    #[pymethods]
    impl SettlementAction {
        /// Settlement action representing the distribution of trade mining payments.
        #[classattr]
        const TradeMining: RustSettlementAction = RustSettlementAction::TradeMining;

        /// Settlement action representing the realization of all unrealized P&L.
        #[classattr]
        const PnlRealization: RustSettlementAction = RustSettlementAction::PnlRealization;

        /// Settlement action representing the distribution of funding payments.
        #[classattr]
        const FundingDistribution: RustSettlementAction = RustSettlementAction::FundingDistribution;

        /// Settlement action representing the expiry of a quarterly future.
        #[allow(non_snake_case)]
        #[cfg(feature = "fixed_expiry_future")]
        #[classmethod]
        fn FuturesExpiry(_cls: &Bound<'_, PyType>, quarter: Quarter) -> Self {
            Self {
                inner: RustSettlementAction::FuturesExpiry { quarter },
            }
        }

        /// For futures-expiry actions, return the quarter of the quarterly expiry future.
        #[cfg(feature = "fixed_expiry_future")]
        fn futures_quarter(&self) -> Option<Quarter> {
            match self.inner {
                RustSettlementAction::FuturesExpiry { quarter } => Some(quarter),
                _ => None,
            }
        }

        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }
    }

    impl From<RustSettlementAction> for SettlementAction {
        fn from(action: RustSettlementAction) -> Self {
            Self { inner: action }
        }
    }

    impl From<SettlementAction> for RustSettlementAction {
        fn from(action: SettlementAction) -> Self {
            action.inner
        }
    }

    #[cfg(feature = "fixed_expiry_future")]
    #[gen_stub_pymethods]
    #[pymethods]
    impl Quarter {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        /// Parse a calendar quarter ("March", "June", …) from `name`.
        #[new]
        fn new(name: &str) -> PyResult<Self> {
            Self::from_str(name).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }

        /// Determine the quarter in which `datetime` lies.
        #[classmethod]
        #[pyo3(name = "find_quarter")]
        fn find_quarter_py(_cls: &Bound<'_, PyType>, datetime: DateTime<Utc>) -> Self {
            Self::find_quarter(datetime)
        }

        /// First expiry date for this quarter strictly after `datetime`.
        #[pyo3(name = "expiry_date_after")]
        fn expiry_date_after_py(&self, datetime: DateTime<Utc>) -> DateTime<Utc> {
            self.expiry_date_after(datetime)
        }

        /// Next quarterly-futures expiry date from `current_time`.
        #[classmethod]
        #[pyo3(name = "upcoming_expiry_date")]
        fn upcoming_expiry_date_py(
            _cls: &Bound<'_, PyType>,
            current_time: DateTime<Utc>,
        ) -> DateTime<Utc> {
            Self::upcoming_expiry_date(current_time)
        }

        /// Return the quarter immediately following this one.
        #[pyo3(name = "next")]
        fn next_py(&self) -> Self {
            self.next()
        }
    }

    // REQUESTS---------------------------------------------------------------------

    macro_rules! delegate_request_methods {
        ($( ($name:ty, $variant:ident), )*) => {
            $(
                #[gen_stub_pymethods]
                #[pymethods]
                impl $name {
                    fn __repr__(&self) -> String {
                        format!("{:?}", self)
                    }

                    #[getter(json)]
                    fn request_repr(&self, py: Python) -> PyObject {
                        pythonize::pythonize(py, &Request::from(Cmd::$variant(self.clone().into()))).unwrap().into()
                    }
                }
            )*
        };
    }

    delegate_request_methods!(
        (CmdTimeValue, AdvanceTime),
        (AdvanceEpoch, AdvanceEpoch),
        (AdvanceSettlementEpoch, AdvanceSettlementEpoch),
        (Block, Block),
        (IndexPrice, IndexPrice),
        (MintPriceCheckpoint, PriceCheckpoint),
        (UpdateProductListings, UpdateProductListings),
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl IndexPrice {
        /// Compute the hash of this index price request.
        #[pyo3(name = "hash")]
        fn hash_py(&self) -> IndexPriceHash {
            self.price_hash()
        }
    }

    // INTENTS----------------------------------------------------------------------

    macro_rules! delegate_intent_methods {
        ($( ($name:ty, $variant:ident), )*) => {
            $(
                #[gen_stub_pymethods]
                #[pymethods]
                impl $name {
                    fn __repr__(&self) -> String {
                        format!("{:?}", self)
                    }

                    #[getter(json)]
                    fn request_repr(&self, py: Python) -> PyObject {
                        pythonize::pythonize(py, &Request::from(ClientRequest::$variant(self.clone()))).unwrap().into()
                    }

                    /// Compute the EIP-712 digest for this intent.
                    /// Passing `message_metadata=(chain_id, verifying_contract)`
                    /// overrides the default values used in the hash.
                    #[pyo3(name = "hash_eip712")]
                    #[pyo3(signature = (message_metadata=None))]
                    fn hash_eip712_py(&self, message_metadata: Option<(u64, String)>) -> PyResult<Hash> {
                        if let Some((chain_id, contract_address)) = message_metadata {
                            return Ok(self.hash_eip712_raw(
                                core_common::types::state::Chain::Ethereum(chain_id),
                                Address::from_str(&contract_address).map_err(|e| CoreCommonError::new_err(e.to_string()))?,
                            ));
                        }
                        Ok(self.hash_eip712())
                    }

                    /// Recover the `(eip712_hash, trader_address)` that signed
                    /// this intent.
                    #[pyo3(name = "recover_signer")]
                    fn recover_signer_py(&self) -> PyResult<(Hash, TraderAddress)> {
                        Ok(self.recover_signer()?)
                    }
                }
            )*
        };
    }

    #[cfg(feature = "insurance_fund_client_req")]
    delegate_intent_methods!((InsuranceFundWithdrawIntent, InsuranceFundWithdraw),);
    delegate_intent_methods!(
        (OrderIntent, Order),
        (ModifyOrderIntent, ModifyOrder),
        (WithdrawIntent, Withdraw),
        (CancelAllIntent, CancelAll),
        (CancelOrderIntent, CancelOrder),
        (ProfileUpdateIntent, ProfileUpdate),
        (WithdrawDDXIntent, WithdrawDDX),
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl OrderIntent {
        /// Compute the hash of this order intent.
        #[pyo3(name = "hash")]
        fn hash_py(&self) -> PyResult<OrderHash> {
            Ok(self.order_hash()?)
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl ModifyOrderIntent {
        /// Compute the hash of this modify order intent.
        #[pyo3(name = "hash")]
        fn hash_py(&self) -> PyResult<OrderHash> {
            Ok(self.order_hash()?)
        }
    }

    // ITEM/ BASE TYPES------------------------------------------------------------

    #[gen_stub_pyclass_enum]
    #[pyclass(frozen, eq, eq_int)]
    #[repr(u8)]
    #[derive(Clone, Copy, PartialEq, Eq, std::hash::Hash)]
    pub enum ItemKind {
        Empty = ITEM_EMPTY,
        Trader = ITEM_TRADER,
        Strategy = ITEM_STRATEGY,
        Position = ITEM_POSITION,
        BookOrder = ITEM_BOOK_ORDER,
        Price = ITEM_PRICE,
        InsuranceFund = ITEM_INSURANCE_FUND,
        Stats = ITEM_STATS,
        Signer = ITEM_SIGNER,
        Specs = ITEM_SPECS,
        TradableProduct = ITEM_TRADABLE_PRODUCT,
        InsuranceFundContribution = ITEM_INSURANCE_FUND_CONTRIBUTION,
        EpochMetadata = ITEM_EPOCH_METADATA,
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl ItemKind {
        /// Create an `ItemKind` from its numeric discriminant (`u8`).  
        /// Returns `PyValueError` if the value does not correspond to a variant.
        #[new]
        fn new(value: u8) -> PyResult<Self> {
            Ok(match value {
                ITEM_EMPTY => ItemKind::Empty,
                ITEM_TRADER => ItemKind::Trader,
                ITEM_STRATEGY => ItemKind::Strategy,
                ITEM_POSITION => ItemKind::Position,
                ITEM_BOOK_ORDER => ItemKind::BookOrder,
                ITEM_PRICE => ItemKind::Price,
                ITEM_INSURANCE_FUND => ItemKind::InsuranceFund,
                ITEM_STATS => ItemKind::Stats,
                ITEM_SIGNER => ItemKind::Signer,
                ITEM_SPECS => ItemKind::Specs,
                ITEM_TRADABLE_PRODUCT => ItemKind::TradableProduct,
                ITEM_INSURANCE_FUND_CONTRIBUTION => ItemKind::InsuranceFundContribution,
                ITEM_EPOCH_METADATA => ItemKind::EpochMetadata,
                _ => {
                    return Err(PyValueError::new_err(format!(
                        "{} is not a valid ItemKind",
                        value
                    )));
                }
            })
        }

        /// Return a Python `dict` that maps variant names to their discriminant values.
        #[classattr]
        fn discriminants(py: Python) -> Bound<'_, PyDict> {
            let members = PyDict::new(py);
            members.set_item("Empty", ItemKind::Empty as u8).unwrap();
            members.set_item("Trader", ItemKind::Trader as u8).unwrap();
            members
                .set_item("Strategy", ItemKind::Strategy as u8)
                .unwrap();
            members
                .set_item("Position", ItemKind::Position as u8)
                .unwrap();
            members
                .set_item("BookOrder", ItemKind::BookOrder as u8)
                .unwrap();
            members.set_item("Price", ItemKind::Price as u8).unwrap();
            members
                .set_item("InsuranceFund", ItemKind::InsuranceFund as u8)
                .unwrap();
            members.set_item("Stats", ItemKind::Stats as u8).unwrap();
            members.set_item("Signer", ItemKind::Signer as u8).unwrap();
            members.set_item("Specs", ItemKind::Specs as u8).unwrap();
            members
                .set_item("TradableProduct", ItemKind::TradableProduct as u8)
                .unwrap();
            members
                .set_item(
                    "InsuranceFundContribution",
                    ItemKind::InsuranceFundContribution as u8,
                )
                .unwrap();
            members
                .set_item("EpochMetadata", ItemKind::EpochMetadata as u8)
                .unwrap();
            members
        }
    }

    #[gen_stub_pyclass]
    #[pyclass(frozen, eq)]
    #[derive(Clone, PartialEq, Debug, Eq)]
    pub struct Item {
        inner: RustItem,
    }

    macro_rules! generate_item_abi_decode {
        ($( $variants:ident, $key_variants:ident; )*) => {
            #[gen_stub_pymethods]
            #[pymethods]
            impl Item {
                fn __repr__(&self) -> String {
                    format!("{:?}", self)
                }

                /// Return this item's [`ItemKind`] discriminant.
                fn item_kind(&self) -> ItemKind {
                    ItemKind::new(self.inner.discriminant()).unwrap()
                }

                /// ABI-encode the wrapped value for hashing / storage.
                fn abi_encoded_value(&self) -> Cow<[u8]> {
                    match &self.inner {
                        RustItem::Empty => Vec::new().into(),
                        $(
                            RustItem::$variants(inner) => <$variants>::from(inner.clone()).abi_encoded_value().into_owned().into(),
                        )*
                    }
                }

                /// Decode the bytes produced by `abi_encoded_value()` back into
                /// an [`Item`] of the supplied kind.
                #[classmethod]
                fn abi_decode_value_into_item(
                    cls: &Bound<'_, PyType>,
                    kind: ItemKind,
                    abi_encoded_value: Cow<[u8]>,
                ) -> PyResult<Option<Self>> {
                    match kind {
                        ItemKind::Empty if abi_encoded_value.is_empty() => Ok(Some(Self {
                            inner: RustItem::Empty,
                        })),
                        ItemKind::Empty => {
                            return Err(CoreCommonError::new_err(
                                "invalid abi representation: empty schema but non-empty value",
                            ))
                        }
                        $(
                            ItemKind::$variants => <$variants>::abi_decode_value_into_item(
                                &PyType::new::<$variants>(cls.py()),
                                abi_encoded_value,
                            ),
                        )*
                    }
                }

                /// Decode a 32-byte SMT key into its strongly-typed form for
                /// the provided item kind.
                #[classmethod]
                fn decode_key<'py>(
                    cls: &Bound<'py, PyType>,
                    kind: ItemKind,
                    encoded_key: H256,
                ) -> PyResult<Bound<'py, PyAny>> {
                    match kind {
                        ItemKind::Empty => {
                            return Err(CoreCommonError::new_err(
                                "cannot decode key for empty item kind",
                            ))
                        }
                        $(
                            ItemKind::$variants => <$key_variants>::decode_key_py(
                                &PyType::new::<$key_variants>(cls.py()),
                                encoded_key,
                            ).and_then(|v| v.into_bound_py_any(cls.py())),
                        )*
                    }
                }
            }
        }
    }

    generate_item_abi_decode!(
        Trader, TraderKey;
        Strategy, StrategyKey;
        Position, PositionKey;
        BookOrder, BookOrderKey;
        Price, PriceKey;
        InsuranceFund, InsuranceFundKey;
        Stats, StatsKey;
        Signer, SignerKey;
        Specs, SpecsKey;
        TradableProduct, TradableProductKey;
        InsuranceFundContribution, InsuranceFundContributionKey;
        EpochMetadata, EpochMetadataKey;
    );

    impl From<Item> for RustItem {
        fn from(item: Item) -> Self {
            item.inner
        }
    }

    // INNER TYPES------------------------------------------------------------

    // Renaming is used to avoid name conflicts with the corresponding Rust methods
    #[gen_stub_pymethods]
    #[pymethods]
    impl Balance {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        fn __len__(&self) -> PyResult<usize> {
            Ok(self.len())
        }

        fn __getitem__(&self, key: TokenSymbol) -> Decimal {
            Decimal::from(*self.get_or_default(key))
        }

        fn __setitem__(&mut self, key: TokenSymbol, value: Decimal) {
            self.insert(key, value.clone().into());
        }

        /// Return an empty `Balance` with zero for every token.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Balance::default()
        }

        /// Construct a `Balance` from a mapping (`dict`) of
        /// `TokenSymbol` → `Decimal` amounts.
        #[classmethod]
        #[pyo3(name = "new_from_many")]
        fn new_from_many_py(
            _cls: &Bound<'_, PyType>,
            amounts: HashMap<TokenSymbol, Decimal>,
        ) -> PyResult<Self> {
            Ok(Balance::new_from_many(
                &amounts
                    .into_iter()
                    .map(|(symbol, amount)| (symbol, amount.into()))
                    .collect(),
            )?)
        }

        /// Total value of this balance, obtained by summing
        /// every token amount. This will be either in USD or DDX, depending on
        /// its contents.
        #[pyo3(name = "total_value")]
        fn total_value_py(&self) -> Decimal {
            self.total_value().into()
        }

        /// Raw amounts ordered by the canonical token list.
        #[pyo3(name = "amounts")]
        fn amounts_py(&self) -> Vec<Decimal> {
            self.amounts().into_iter().map(|v| (*v).into()).collect()
        }
    }

    // TODO: this really sucks but it has to be done. we definitely should proceduralize all of this later

    macro_rules! delegate_balance_methods {
        ($item_name:ty) => {
            #[gen_stub_pymethods]
            #[pymethods]
            impl $item_name {
                fn __len__(&self) -> PyResult<usize> {
                    self.inner.__len__()
                }

                fn __getitem__(&self, key: TokenSymbol) -> Decimal {
                    self.inner.__getitem__(key)
                }

                fn __setitem__(&mut self, key: TokenSymbol, value: Decimal) {
                    self.inner.__setitem__(key, value)
                }

                /// Construct a balance initialized with `amount` of `symbol`.
                #[new]
                fn new(amount: Decimal, symbol: TokenSymbol) -> Self {
                    Self {
                        inner: Balance::new_py(amount, symbol),
                    }
                }

                /// Return an empty balance with zero for every token.
                #[classmethod]
                fn default(cls: &Bound<'_, PyType>) -> Self {
                    Self {
                        inner: Balance::default_py(&PyType::new::<Balance>(cls.py())),
                    }
                }

                /// Construct a balance from a mapping of token amounts.
                #[classmethod]
                fn new_from_many(
                    cls: &Bound<'_, PyType>,
                    amounts: HashMap<TokenSymbol, Decimal>,
                ) -> PyResult<Self> {
                    Ok(Self {
                        inner: Balance::new_from_many_py(
                            &PyType::new::<Balance>(cls.py()),
                            amounts,
                        )?,
                    })
                }

                /// Total value of this balance, obtained by summing
                /// every token amount. This will be either in USD or DDX, depending on
                /// its contents.
                fn total_value(&self) -> Decimal {
                    self.inner.total_value_py()
                }

                /// Raw amounts ordered by the canonical token list.
                fn amounts(&self) -> Vec<Decimal> {
                    self.inner.amounts_py()
                }
            }
        };
    }

    // ITEM/ TYPES------------------------------------------------------------

    // Note: unfortunately macros cannot be called inside of pymethods, or else a lot of extraneous
    // code could be removed and replaced with paste! or internal macros.
    macro_rules! impl_item {
        ($item_name:ident, $key_name:ident) => {
            impl_item!(@common $item_name, $key_name; $item_name);
        };
        ($item_name:ident, $key_name:ident;; $key_type:ty) => {
            impl_item!(@key $key_name, $key_type);
            impl_item!(@common $item_name, $key_name; $item_name);
        };
        ($item_name:ident, $key_name:ident; $inner:ty;) => {
            impl_item!(@item $item_name, $inner);
            impl_item!(@common $item_name, $key_name; $inner);
        };
        ($item_name:ident, $key_name:ident; $inner:ty; $key_type:ty) => {
            impl_item!(@item $item_name, $inner);
            impl_item!(@key $key_name, $key_type);
            impl_item!(@common $item_name, $key_name; $inner);
        };
        (@item $name:ident, $inner:ty) => {
            #[gen_stub_pyclass]
            #[pyclass(eq)]
            #[derive(Clone, PartialEq, Eq, Debug, Default)]
            pub struct $name {
                inner: $inner,
            }

            impl VoidableItem for $name {
                fn is_void(&self) -> bool {
                    self.inner.is_void()
                }
            }

            impl Tokenizable for $name {
                fn from_token(token: DynSolValue) -> core_common::Result<Self>
                where
                    Self: Sized,
                {
                    <$inner>::from_token(token).map(|inner| Self { inner })
                }
                fn into_token(self) -> DynSolValue {
                    self.inner.into_token()
                }
            }

            impl From<$name> for $inner {
                fn from(item: $name) -> Self {
                    item.inner
                }
            }

            impl From<&$name> for $inner {
                fn from(item: &$name) -> Self {
                    item.inner.clone()
                }
            }

            impl From<$inner> for $name {
                fn from(inner: $inner) -> Self {
                    Self { inner }
                }
            }
        };
        (@key $name:ident, $key_type:ty) => {
            #[gen_stub_pyclass]
            #[pyclass(frozen, eq, ord, hash)]
            #[derive(Clone, PartialEq, Eq, std::hash::Hash, Debug, PartialOrd, Ord)]
            pub struct $name {
                inner: $key_type,
            }

            #[gen_stub_pymethods]
            #[pymethods]
            impl $name {
                #[new]
                fn new(inner: $key_type) -> Self {
                    Self { inner }
                }
            }

            impl VerifiedStateKey for $name {
                fn encode_key(&self) -> Hash {
                    self.inner.encode_key()
                }

                fn decode_key(value: &Hash) -> core_common::Result<Self> {
                    Ok(Self {
                        inner: <$key_type>::decode_key(value)?,
                    })
                }
            }

            impl From<$name> for $key_type {
                fn from(item: $name) -> Self {
                    item.inner
                }
            }

            impl<'a> From<&'a $name> for &'a $key_type {
                fn from(item: &'a $name) -> &'a $key_type {
                    &item.inner
                }
            }

            impl From<$key_type> for $name {
                fn from(inner: $key_type) -> Self {
                    Self { inner }
                }
            }
        };
        (@common $item_name:ident, $key_name:ident; $inner:ty) => {
            #[gen_stub_pymethods]
            #[pymethods]
            impl $key_name {
                fn __repr__(&self) -> String {
                    format!("{:?}", self)
                }

                fn __deepcopy__(&self, _memo: &Bound<'_, PyDict>) -> Self {
                    self.clone()
                }

                /// Encode this state-key into the 32-byte format used on-chain.
                #[pyo3(name = "encode_key")]
                fn encode_key_py(&self) -> H256 {
                    RustH256::from(<$key_name>::from(self.clone()).encode_key()).into()
                }

                /// Decode a previously-encoded key back into its strongly-typed form.
                #[classmethod]
                #[pyo3(name = "decode_key")]
                fn decode_key_py(_cls: &Bound<'_, PyType>, value: H256) -> PyResult<Self> {
                    Ok(<$key_name>::decode_key(&RustH256::from(value).into())?.into())
                }
            }

            #[gen_stub_pymethods]
            #[pymethods]
            impl $item_name {
                fn __repr__(&self) -> String {
                    format!("{:?}", self)
                }

                fn __deepcopy__(&self, _memo: &Bound<'_, PyDict>) -> Self {
                    self.clone()
                }

                /// Wrap this concrete structure into the generic [`Item`] enum.
                fn as_item(&self) -> Item {
                    Item {
                        inner: RustItem::$item_name(<$inner>::from(self.clone())),
                    }
                }

                /// Down-cast a generic [`Item`] into this concrete type.
                #[classmethod]
                fn from_item(_cls: &Bound<'_, PyType>, item: Item) -> PyResult<Self> {
                    match item.inner {
                        RustItem::$item_name(inner) => Ok(inner.into()),
                        _ => Err(CoreCommonError::new_err("invalid item kind")),
                    }
                }

                /// ABI-encode this value.
                fn abi_encoded_value(&self) -> Cow<[u8]> {
                    alloy_dyn_abi::DynSolValue::Tuple(vec![self.as_item().inner.into_token()]).abi_encode().into()
                }

                /// Decode bytes back into an [`Item`] of this concrete type.
                #[classmethod]
                fn abi_decode_value_into_item(
                    _cls: &Bound<'_, PyType>,
                    abi_encoded_value: Cow<[u8]>,
                ) -> PyResult<Option<Item>> {
                    for abi_schema in &ITEM_PARAM_TYPES[&ItemKind::$item_name] {
                        match abi_schema.abi_decode(abi_encoded_value.as_ref()).map_err(|e|CoreCommonError::new_err(format!("invalid abi representation: {}", e.to_string())))
                            .and_then(|v|
                                match v.as_tuple() {
                                    Some(t) => RustItem::from_token(t[0].clone()).map_err(|_| {
                                    CoreCommonError::new_err(format!("Failed to deserialize token into Item"))
                                }),
                                    None => Err(CoreCommonError::new_err("failed to deserialize token as tuple".to_string())),
                                })
                        {
                            Ok(item) => {
                                return Ok(Some(Item { inner: item }));
                            }
                            Err(_) => continue,
                        }
                    }
                    Err(CoreCommonError::new_err(
                        "invalid abi representation: all schemas failed".to_string(),
                    ))
                }

                /// `true` when this value represents the special *void* marker
                /// used to delete a leaf from the SMT.
                #[pyo3(name = "is_void")]
                fn is_void_py(&self) -> bool {
                    self.is_void()
                }
            }
        };
    }

    lazy_static! {
        static ref ITEM_PARAM_TYPES: HashMap<ItemKind, Vec<DynSolType>> = {
            [
                (
                    ItemKind::Trader,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Uint(256),
                        DynSolType::Uint(256),
                        DynSolType::Address,
                        DynSolType::Bool,
                        DynSolType::Bool,
                    ])],
                ),
                (
                    ItemKind::Strategy,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Tuple(vec![
                            DynSolType::Array(Box::new(DynSolType::Address)),
                            DynSolType::Array(Box::new(DynSolType::Uint(128))),
                        ]),
                        DynSolType::Tuple(vec![
                            DynSolType::Array(Box::new(DynSolType::Address)),
                            DynSolType::Array(Box::new(DynSolType::Uint(128))),
                        ]),
                        DynSolType::Uint(64),
                        DynSolType::Bool,
                    ])],
                ),
                (
                    ItemKind::Position,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Tuple(vec![DynSolType::Uint(256)]),
                        DynSolType::Uint(256),
                        DynSolType::Uint(256),
                    ])],
                ),
                (
                    ItemKind::BookOrder,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Tuple(vec![DynSolType::Uint(256)]),
                        DynSolType::Uint(256),
                        DynSolType::Uint(256),
                        DynSolType::FixedBytes(32),
                        DynSolType::FixedBytes(4),
                        DynSolType::Uint(64),
                        DynSolType::Uint(64),
                    ])],
                ),
                (
                    ItemKind::Price,
                    vec![
                        DynSolType::Tuple(vec![
                            DynSolType::Uint(256),
                            DynSolType::Tuple(vec![DynSolType::Uint(256), DynSolType::Uint(256)]),
                            DynSolType::Uint(64),
                            DynSolType::Uint(64),
                        ]),
                        DynSolType::Tuple(vec![
                            DynSolType::Uint(256),
                            DynSolType::Tuple(vec![
                                DynSolType::Uint(256),
                                DynSolType::Uint(256),
                                DynSolType::Uint(64),
                            ]),
                            DynSolType::Uint(64),
                            DynSolType::Uint(64),
                        ]),
                    ],
                ),
                (
                    ItemKind::InsuranceFund,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Array(Box::new(DynSolType::Address)),
                        DynSolType::Array(Box::new(DynSolType::Uint(128))),
                    ])],
                ),
                (
                    ItemKind::Stats,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Uint(256),
                        DynSolType::Uint(256),
                    ])],
                ),
                (ItemKind::Signer, vec![DynSolType::FixedBytes(32)]),
                (ItemKind::Specs, vec![DynSolType::String]),
                (ItemKind::TradableProduct, vec![DynSolType::Tuple(vec![])]),
                (
                    ItemKind::InsuranceFundContribution,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Tuple(vec![
                            DynSolType::Array(Box::new(DynSolType::Address)),
                            DynSolType::Array(Box::new(DynSolType::Uint(128))),
                        ]),
                        DynSolType::Tuple(vec![
                            DynSolType::Array(Box::new(DynSolType::Address)),
                            DynSolType::Array(Box::new(DynSolType::Uint(128))),
                        ]),
                    ])],
                ),
                (
                    ItemKind::EpochMetadata,
                    vec![DynSolType::Tuple(vec![
                        DynSolType::Uint(256),
                        DynSolType::Tuple(vec![
                            DynSolType::Array(Box::new(DynSolType::FixedBytes(32))),
                            DynSolType::Array(Box::new(DynSolType::Uint(64))),
                        ]),
                    ])],
                ),
            ]
            .into_iter()
            .map(|(k, inner)| {
                (
                    k,
                    inner
                        .into_iter()
                        .map(|pt| {
                            DynSolType::Tuple(vec![DynSolType::Tuple(vec![
                                DynSolType::Uint(256),
                                pt,
                            ])])
                        })
                        .collect(),
                )
            })
            .collect()
        };
    }

    impl_item!(
        Trader,
        TraderKey
        ;;
        TraderAddress
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl Trader {
        /// Return a zero-initialized `Trader` value.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }
    }

    impl_item!(Strategy, StrategyKey);

    #[gen_stub_pymethods]
    #[pymethods]
    impl Strategy {
        /// Return an empty `Strategy` with default parameters.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }

        /// Return a new `Balance` obtained by updating this strategy's
        /// available collateral for `symbol` to `amount`.
        fn update_avail_collateral(&self, symbol: TokenSymbol, amount: Decimal) -> Balance {
            let mut new = self.avail_collateral.clone();
            new.insert(symbol, amount.into());
            new
        }

        /// Return a new `Balance` obtained by updating this strategy's
        /// locked collateral for `symbol` to `amount`.
        fn update_locked_collateral(&self, symbol: TokenSymbol, amount: Decimal) -> Balance {
            let mut new = self.locked_collateral.clone();
            new.insert(symbol, amount.into());
            new
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl StrategyKey {
        /// Deterministically hash `strategy_id` into a `StrategyIdHash`.
        #[staticmethod]
        fn generate_strategy_id_hash(strategy_id: StrategyId) -> StrategyIdHash {
            strategy_id.into()
        }

        /// Derive the `PositionKey` for `symbol` that belongs to this strategy.
        #[pyo3(name = "as_position_key")]
        fn as_position_key_py(&self, symbol: ProductSymbol) -> PositionKey {
            self.as_position_key::<RustProductSymbol>(symbol.into())
        }
    }

    impl_item!(Position, PositionKey);

    // Renaming is used to avoid name conflicts with the corresponding Rust methods
    #[gen_stub_pymethods]
    #[pymethods]
    impl Position {
        /// Return an empty `Position` with zero balance and no entry price.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }

        /// Bankruptcy price at which margin would be exhausted.
        #[pyo3(name = "bankruptcy_price")]
        fn bankruptcy_price_py(
            &self,
            mark_price: Decimal,
            account_total_value: Decimal,
        ) -> Decimal {
            self.bankruptcy_price(mark_price.into(), account_total_value.into())
                .into()
        }

        /// Unrealized profit and loss at the specified `price`.
        #[pyo3(name = "unrealized_pnl")]
        fn unrealized_pnl_py(&self, price: Decimal) -> Decimal {
            self.unrealized_pnl(price.into()).into()
        }

        /// Average P&L per contract at the specified `price`.
        #[pyo3(name = "avg_pnl")]
        fn avg_pnl_py(&self, price: Decimal) -> Decimal {
            self.avg_pnl(price.into()).into()
        }

        // HACK: have to clone here because of this annoying #[pyo3(get)] cloning behavior
        // https://pyo3.rs/v0.21.2/faq#pyo3get-clones-my-field
        /// Increase position size by `amount` at `price`; returns the new
        /// position together with any realized P&L.
        #[pyo3(name = "increase")]
        fn increase_py(&self, price: Decimal, amount: Decimal) -> (Position, Decimal) {
            let mut new = self.clone();
            let res = new.increase(price.into(), amount.into()).into();
            (new, res)
        }

        // HACK: have to clone here because of this annoying #[pyo3(get)] cloning behavior
        // https://pyo3.rs/v0.21.2/faq#pyo3get-clones-my-field
        /// Decrease position size by `amount` at `price`; returns the new
        /// position and realized P&L.
        #[pyo3(name = "decrease")]
        fn decrease_py(&self, price: Decimal, amount: Decimal) -> (Position, Decimal) {
            let mut new = self.clone();
            let res = new.decrease(price.into(), amount.into()).into();
            (new, res)
        }

        // HACK: have to clone here because of this annoying #[pyo3(get)] cloning behavior
        // https://pyo3.rs/v0.21.2/faq#pyo3get-clones-my-field
        /// Reverse side by `amount` at `price`; returns updated position and P&L.
        #[pyo3(name = "cross_over")]
        fn cross_over_py(&self, price: Decimal, amount: Decimal) -> (Position, Decimal) {
            let mut new = self.clone();
            let res = new.cross_over(price.into(), amount.into()).unwrap().into();
            (new, res)
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl PositionKey {
        /// Convert this position key into its owner `StrategyKey`.
        fn as_strategy_key(&self) -> StrategyKey {
            StrategyKey::from(*self)
        }
    }

    impl_item!(BookOrder, BookOrderKey);
    impl_item!(Price, PriceKey);

    // Renaming is used to avoid name conflicts with the corresponding Rust methods
    #[gen_stub_pymethods]
    #[pymethods]
    impl Price {
        #[getter(mark_price)]
        fn mark_price_py(&self) -> Decimal {
            self.mark_price().into()
        }
    }

    impl_item!(
        InsuranceFund,
        InsuranceFundKey
        ;
        Balance;
    );
    delegate_balance_methods!(InsuranceFund);
    impl_item!(Stats, StatsKey);

    #[gen_stub_pymethods]
    #[pymethods]
    impl Stats {
        /// Return a `Stats` structure with all counters set to zero.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl StatsKey {
        /// Convert this stats key into the corresponding `TraderKey`.
        fn as_trader_key(&self) -> TraderKey {
            TraderKey { inner: self.trader }
        }
    }

    impl_item!(
        Signer,
        SignerKey
        ;
        ReleaseHash;
        SignerAddress
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl Signer {
        /// Construct a new `Signer` identified by `inner` release hash.
        #[new]
        fn new(inner: ReleaseHash) -> Self {
            Self { inner }
        }
    }

    impl_item!(
        Specs,
        SpecsKey
        ;
        SpecsExpr;
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl Specs {
        /// Wrapped `SpecsExpr`.
        #[new]
        fn new(inner: SpecsExpr) -> Self {
            Self { inner }
        }

        /// Convert this expression into concrete `ProductSpecs` of the requested kind.
        fn as_product_specs(&self, specs_kind: SpecsKind) -> PyResult<ProductSpecs> {
            Ok(self.inner.as_product_specs(specs_kind)?)
        }
    }

    #[cfg_eval]
    #[gen_stub_pymethods]
    #[pymethods]
    impl SpecsKey {
        #[cfg(feature = "fixed_expiry_future")]
        /// List the currently tradable products that are live at `current_time`.
        #[pyo3(name = "current_tradable_products")]
        fn current_tradable_products_py(
            &self,
            current_time: DateTime<Utc>,
        ) -> Vec<TradableProductKey> {
            self.current_tradable_products(current_time)
        }

        #[cfg(not(feature = "fixed_expiry_future"))]
        /// List the currently tradable products.
        #[pyo3(name = "current_tradable_products")]
        fn current_tradable_products_py(&self) -> Vec<TradableProductKey> {
            self.current_tradable_products()
        }

        /// Return whether this specs has a lifecycle constraint.
        #[pyo3(name = "has_lifecycle")]
        fn has_lifecycle_py(&self) -> Option<bool> {
            self.has_lifecycle()
        }
    }

    impl_item!(TradableProduct, TradableProductKey);

    #[gen_stub_pymethods]
    #[pymethods]
    impl TradableProductKey {
        /// Convert this key into its `ProductSymbol`.
        fn as_product_symbol(&self) -> ProductSymbol {
            RustProductSymbol::from(self).into()
        }
    }

    impl_item!(
        InsuranceFundContribution,
        InsuranceFundContributionKey
        ;;
        InsuranceFundContributorAddress
    );

    #[gen_stub_pymethods]
    #[pymethods]
    impl InsuranceFundContribution {
        /// Return an empty `InsuranceFundContribution` with zero balances.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }

        /// Return a copy of `avail_balance` with `symbol` set to `amount`.
        fn update_avail_balance(&self, symbol: TokenSymbol, amount: Decimal) -> Balance {
            let mut new = self.avail_balance.clone();
            new.insert(symbol, amount.into());
            new
        }

        /// Return a copy of `locked_balance` with `symbol` set to `amount`.
        fn update_locked_balance(&self, symbol: TokenSymbol, amount: Decimal) -> Balance {
            let mut new = self.locked_balance.clone();
            new.insert(symbol, amount.into());
            new
        }
    }

    impl_item!(EpochMetadata, EpochMetadataKey);

    #[gen_stub_pymethods]
    #[pymethods]
    impl EpochMetadata {
        /// Return empty `EpochMetadata` with zero fee pool and no order ordinals.
        #[classmethod]
        #[pyo3(name = "default")]
        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
            Self::default()
        }
    }

    // SMT TYPES------------------------------------------------------------

    #[gen_stub_pyclass]
    #[pyclass(frozen)]
    #[derive(Clone, Debug)]
    pub struct MerkleProof {
        inner: CompiledMerkleProof,
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl MerkleProof {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        /// Return the compiled proof as a raw byte slice suitable for
        /// on-chain verification.
        fn as_bytes(&self) -> Cow<[u8]> {
            self.inner.0.clone().into()
        }
    }

    impl From<CompiledMerkleProof> for MerkleProof {
        fn from(proof: CompiledMerkleProof) -> Self {
            MerkleProof { inner: proof }
        }
    }

    /// Wrapped DerivaDEX Sparse Merkle Tree.
    #[gen_stub_pyclass]
    #[pyclass]
    #[derive(Debug)]
    pub struct DerivadexSMT {
        inner: SharedSparseMerkleTree,
    }

    #[cfg_eval]
    #[gen_stub_pymethods]
    #[pymethods]
    impl DerivadexSMT {
        fn __repr__(&self) -> String {
            format!("{:?}", self)
        }

        /// Construct an empty in-memory SMT with a fresh root.
        #[new]
        fn new() -> Self {
            Self {
                inner: SharedSparseMerkleTree::new(Default::default(), ConcurrentStore::empty()),
            }
        }

        /// Build the genesis SMT (without quarterly-future support).
        #[cfg(not(feature = "fixed_expiry_future"))]
        #[classmethod]
        fn from_genesis(
            _cls: &Bound<'_, PyType>,
            _py: Python,
            insurance_fund_cap: Balance,
            ddx_fee_pool: UnscaledI128,
            specs: &Bound<'_, PyAny>,
        ) -> PyResult<Self> {
            let specs = &specs.extract::<HashMap<SpecsKey, SpecsExpr>>()?;
            Ok(Self {
                inner: from_genesis(insurance_fund_cap, ddx_fee_pool, specs)?,
            })
        }

        /// Build the genesis SMT, taking `current_time` into account for futures.
        #[cfg(feature = "fixed_expiry_future")]
        #[classmethod]
        fn from_genesis(
            _cls: &Bound<'_, PyType>,
            insurance_fund_cap: Balance,
            ddx_fee_pool: UnscaledI128,
            specs: &Bound<'_, PyAny>,
            current_time: DateTime<Utc>,
        ) -> PyResult<Self> {
            let specs = &specs.extract::<HashMap<SpecsKey, SpecsExpr>>()?;
            Ok(Self {
                inner: from_genesis(insurance_fund_cap, ddx_fee_pool, specs, current_time)?,
            })
        }

        /// Current SMT root hash.
        fn root(&self) -> H256 {
            (*self.inner.root()).into()
        }

        /// Generate a compiled Merkle proof covering all provided leaf `keys`.
        fn merkle_proof(&self, keys: Vec<H256>) -> PyResult<MerkleProof> {
            // No keys require no proof. It's easier than adding error conditions.
            if keys.is_empty() {
                return Ok(CompiledMerkleProof(vec![]).into());
            }
            let leaves = keys
                .iter()
                .map(|k| {
                    let k: RustH256 = (*k).into();
                    let v = self.inner.get(&k).map_err(|e| {
                        CoreCommonError::new_err(format!("merkle proof error: {}", e))
                    })?;
                    Ok((k, v.to_h256()))
                })
                .collect::<PyResult<Vec<_>>>()?;
            let compiled_proof = self
                .inner
                .merkle_proof(keys.iter().map(|&k| k.into()).collect())
                .and_then(|proof| proof.compile(leaves))
                .map_err(|e| CoreCommonError::new_err(format!("merkle proof error: {}", e)))?;
            Ok(compiled_proof.into())
        }

        #[pyo3(signature = (key, maybe_inner))]
        /// Insert (`Some`) or delete (`None`) a leaf at `key` and return the
        /// updated tree root hash.
        fn store_item_by_key(&mut self, key: H256, maybe_inner: Option<Item>) -> PyResult<H256> {
            let key: RustH256 = key.into();
            let item = match maybe_inner {
                Some(inner) => {
                    let item = RustItem::from(inner);
                    if key.as_slice()[0] != item.discriminant() {
                        return Err(CoreCommonError::new_err(
                            "key and item discriminant mismatch",
                        ));
                    }
                    item
                }
                None => RustItem::zero(),
            };
            self.inner
                .update(key, item)
                .map(|&key| key.into())
                .map_err(|e| CoreCommonError::new_err(format!("smt update error: {}", e)))
        }

        fn __deepcopy__(&self, _memo: &Bound<'_, PyDict>) -> Self {
            DerivadexSMT {
                inner: SharedSparseMerkleTree::new(
                    *self.inner.root(),
                    self.inner.store().deep_copy(),
                ),
            }
        }
    }

    // Note: unfortunately macros cannot be called inside of pymethods, or else a lot of extraneous
    // code could be removed and replaced with paste! or internal macros.
    macro_rules! impl_get_and_store_for_smt {
        ($get_name:ident, $get_all_name:ident, $store_name:ident; $variant:ident, $key_type:ty) => {
            #[gen_stub_pymethods]
            #[pymethods]
            impl DerivadexSMT {
                /// Fetch the item stored at `key`, or `None` if the leaf is empty.
                fn $get_name(&self, key: &$key_type) -> PyResult<Option<$variant>> {
                    let item = self
                        .inner
                        .get(&(key.encode_key().into()))
                        .map_err(|e| CoreCommonError::new_err(format!("smt get error: {}", e)))?;
                    if let RustItem::$variant(val) = item {
                        Ok(Some(val.into()))
                    } else if item == RustItem::zero() {
                        Ok(None)
                    } else {
                        Err(CoreCommonError::new_err(concat!(
                            "invalid ",
                            stringify!($variant),
                            " item"
                        )))
                    }
                }

                /// Insert (`Some`) or delete (`None`) a leaf and return the new
                /// SMT root hash.
                #[pyo3(signature = (key, maybe_inner))]
                fn $store_name(
                    &mut self,
                    key: $key_type,
                    maybe_inner: Option<$variant>,
                ) -> PyResult<H256> {
                    let item = match maybe_inner {
                        Some(inner) if !inner.is_void() => RustItem::$variant(inner.into()),
                        _ => RustItem::zero(),
                    };
                    self.inner
                        .update(key.encode_key().into(), item)
                        .map(|&root| root.into())
                        .map_err(|e| CoreCommonError::new_err(format!("smt update error: {}", e)))
                }

                /// Return every item of this type currently stored in the tree.
                fn $get_all_name(&self) -> Vec<($key_type, $variant)> {
                    self.inner
                        .store()
                        .leaves_map()
                        .read()
                        .unwrap()
                        .iter()
                        .filter_map(|(_, item)| {
                            if let RustItem::$variant(val) = &item.value {
                                Some((
                                    <$key_type>::decode_key(&item.key.into())
                                        .expect("key item mismatch"),
                                    <$variant>::from(val.clone()),
                                ))
                            } else {
                                None
                            }
                        })
                        .collect()
                }
            }
        };
    }

    impl_get_and_store_for_smt!(
        trader,
        all_traders,
        store_trader;
        Trader,
        TraderKey
    );
    impl_get_and_store_for_smt!(
        strategy,
        all_strategies,
        store_strategy;
        Strategy,
        StrategyKey
    );
    impl_get_and_store_for_smt!(
        position,
        all_positions,
        store_position;
        Position,
        PositionKey
    );
    impl_get_and_store_for_smt!(
        book_order,
        all_book_orders,
        store_book_order;
        BookOrder,
        BookOrderKey
    );
    impl_get_and_store_for_smt!(
        price,
        all_prices,
        store_price;
        Price,
        PriceKey
    );
    impl_get_and_store_for_smt!(
        insurance_fund,
        all_insurance_funds,
        store_insurance_fund;
        InsuranceFund,
        InsuranceFundKey
    );
    impl_get_and_store_for_smt!(
        stats,
        all_stats,
        store_stats;
        Stats,
        StatsKey
    );
    impl_get_and_store_for_smt!(
        signer,
        all_signers,
        store_signer;
        Signer,
        SignerKey
    );
    impl_get_and_store_for_smt!(
        specs,
        all_specs,
        store_specs;
        Specs,
        SpecsKey
    );
    impl_get_and_store_for_smt!(
        tradable_product,
        all_tradable_products,
        store_tradable_product;
        TradableProduct,
        TradableProductKey
    );
    impl_get_and_store_for_smt!(
        insurance_fund_contribution,
        all_insurance_fund_contributions,
        store_insurance_fund_contribution;
        InsuranceFundContribution,
        InsuranceFundContributionKey
    );
    impl_get_and_store_for_smt!(
        epoch_metadata,
        all_epoch_metadatas,
        store_epoch_metadata;
        EpochMetadata,
        EpochMetadataKey
    );

    // Note: unfortunately macros cannot be called inside of pymethods, or else a lot of extraneous
    // code could be removed and replaced with paste! or internal macros.
    macro_rules! impl_extra_get_all_for_smt {
        ($name:ident($( $args:tt )*), $variant_type:ident, $key_type:ident, $filter_map:expr) => {
            #[gen_stub_pymethods]
            #[pymethods]
            impl DerivadexSMT {
                /// Helper that returns the filtered list described by the method.
                fn $name(&self, $($args)*) -> Vec<($key_type, $variant_type)> {
                    self.inner
                        .store()
                        .leaves_map()
                        .read()
                        .unwrap()
                        .iter()
                        .filter_map(|(key, item)| {
                            #[allow(unused_variables, clippy::redundant_closure_call)]
                            $filter_map(key, item)
                        })
                        .collect()
                }
            }
        }
    }

    impl_extra_get_all_for_smt!(
        all_leaves(),
        Item,
        H256,
        (|_hash: &RustH256, item: &LeafNode<RustItem>| {
            Some((
                H256::from(item.key),
                Item {
                    inner: item.value.clone(),
                },
            ))
        })
    );
    impl_extra_get_all_for_smt!(
        all_prices_for_symbol(symbol: RustProductSymbol),
        Price,
        PriceKey,
        (|_hash: &RustH256, item: &LeafNode<RustItem>| {
            if let RustItem::Price(val) = &item.value {
                let key = PriceKey::decode_key(&item.key.into()).expect("invalid price key");
                if key.symbol == symbol {
                    return Some((key, *val));
                }
            }
            None
        })
    );
    impl_extra_get_all_for_smt!(
        all_positions_for_symbol(symbol: RustProductSymbol),
        Position,
        PositionKey,
        (|_hash: &RustH256, item: &LeafNode<RustItem>| {
            if let RustItem::Position(val) = &item.value {
                let key = PositionKey::decode_key(&item.key.into()).expect("invalid position key");
                if key.symbol == symbol {
                    return Some((key, val.clone()));
                }
            }
            None
        })
    );
    impl_extra_get_all_for_smt!(
        all_book_orders_for_symbol(symbol: RustProductSymbol),
        BookOrder,
        BookOrderKey,
        (|_hash: &RustH256, item: &LeafNode<RustItem>| {
            if let RustItem::BookOrder(val) = &item.value {
                let key =
                    BookOrderKey::decode_key(&item.key.into()).expect("invalid book order key");
                if key.symbol == symbol {
                    return Some((key, val.clone()));
                }
            }
            None
        })
    );

    #[cfg(test)]
    mod tests {
        use super::*;
        use crate::tree::shared_smt::Keccak256Hasher;
        #[cfg(feature = "fixed_expiry_future")]
        use crate::types::state::exported::UnscaledI128;

        macro_rules! generate_roundtrip_tests {
            ($($test_name:ident, $name:ident;)*) => {
                $(
                    #[test]
                    fn $test_name() {
                        pyo3::prepare_freethreaded_python();
                        Python::with_gil(|py| {
                            let item = $name::default_py(&PyType::new::<$name>(py));
                            let expected_token = RustItem::$name(item.clone().into()).into_token();
                            let expected_token = alloy_dyn_abi::DynSolValue::Tuple(vec![expected_token]);
                            let bytes = expected_token.abi_encode();
                            let schema: alloy_dyn_abi::DynSolType = core_common::util::tokenize::generate_schema(&expected_token).into();
                            println!("abi schema: {:?}", schema);
                            let actual_token = item.abi_encoded_value().into_owned();
                            assert_eq!(
                                actual_token,
                                Item {
                                    inner: RustItem::$name(item.clone().into())
                                }
                                .abi_encoded_value()
                                .into_owned()
                            );
                            assert_eq!(bytes, actual_token);
                            let expected_item = RustItem::from_token(
                                schema.abi_decode(&bytes)
                                    .unwrap()
                                    .as_tuple()
                                    .unwrap()
                                    .get(0).unwrap().clone(),
                            )
                            .unwrap();
                            let actual_item =
                                $name::abi_decode_value_into_item(&PyType::new::<$name>(py), Cow::Borrowed(&actual_token))
                                    .unwrap()
                                    .unwrap()
                                    .into();
                            assert_eq!(expected_item, actual_item);
                            assert_eq!(
                                actual_item,
                                Item::abi_decode_value_into_item(
                                    &PyType::new::<Item>(py),
                                    ItemKind::$name,
                                    Cow::Borrowed(&actual_token)
                                )
                                .unwrap()
                                .unwrap()
                                .into()
                            );
                        })
                    }
                )*
            };
        }

        macro_rules! generate_roundtrip_tests_with_default {
            ($($test_name:ident, $name:ident;)*) => {
                $(
                    #[pymethods]
                    impl $name {
                        #[classmethod]
                        #[pyo3(name = "default")]
                        fn default_py(_cls: &Bound<'_, PyType>) -> Self {
                            $name::default()
                        }
                    }
                )*

                generate_roundtrip_tests!($($test_name, $name;)*);
            };
        }

        generate_roundtrip_tests!(
            test_abi_roundtrip_strategy, Strategy;
            test_abi_roundtrip_trader, Trader;
            test_abi_roundtrip_position, Position;
            test_abi_roundtrip_stats, Stats;
            test_abi_roundtrip_insurance_fund_contribution, InsuranceFundContribution;
            test_abi_roundtrip_epoch_metadata, EpochMetadata;
        );

        generate_roundtrip_tests_with_default!(
            test_abi_roundtrip_book_order, BookOrder;
            test_abi_roundtrip_price, Price;
            test_abi_roundtrip_signer, Signer;
            test_abi_roundtrip_specs, Specs;
            test_abi_roundtrip_tradable_product, TradableProduct;
        );

        #[cfg(feature = "fixed_expiry_future")]
        #[test]
        fn test_abi_roundtrip_price_different_variant() {
            pyo3::prepare_freethreaded_python();
            Python::with_gil(|py| {
                let item = Price {
                    index_price: UnscaledI128::from_str("200").unwrap(),
                    mark_price_metadata: crate::types::accounting::MarkPriceMetadata::Average {
                        accum: UnscaledI128::ZERO,
                        count: 0,
                    },
                    ordinal: 4,
                    time_value: 241,
                };
                let expected_token =
                    alloy_dyn_abi::DynSolValue::Tuple(vec![RustItem::Price(item).into_token()])
                        .abi_encode();
                let actual_token = item.abi_encoded_value().into_owned();
                assert_eq!(
                    actual_token,
                    Item {
                        inner: RustItem::Price(item)
                    }
                    .abi_encoded_value()
                    .into_owned()
                );
                assert_eq!(expected_token, actual_token);
                let expected_item = RustItem::from_token(
                    ITEM_PARAM_TYPES[&ItemKind::Price][1]
                        .abi_decode(&actual_token)
                        .unwrap()
                        .as_tuple()
                        .unwrap()
                        .first()
                        .unwrap()
                        .clone(),
                )
                .unwrap();
                let actual_item = Price::abi_decode_value_into_item(
                    &PyType::new::<Price>(py),
                    Cow::Borrowed(&actual_token),
                )
                .unwrap()
                .unwrap()
                .into();
                assert_eq!(expected_item, actual_item);
                assert_eq!(
                    actual_item,
                    Item::abi_decode_value_into_item(
                        &PyType::new::<Item>(py),
                        ItemKind::Price,
                        Cow::Borrowed(&actual_token),
                    )
                    .unwrap()
                    .unwrap()
                    .into()
                );
            })
        }

        #[test]
        fn test_abi_roundtrip_merkle_proof_single_key() {
            pyo3::prepare_freethreaded_python();
            Python::with_gil(|py| {
                let mut smt = DerivadexSMT::from_genesis(
                    &PyType::new::<DerivadexSMT>(py),
                    Balance::default(),
                    UnscaledI128::default(),
                    &HashMap::from([(SpecsKey::new_py(SpecsKind::SingleNamePerpetual, "ETHP".to_string()).unwrap(), SpecsExpr::new("\n(SingleNamePerpetual :name \"ETHP\"\n :underlying \"ETH\"\n :tick-size 0.1\n :max-order-notional 1000000\n :max-taker-price-deviation 0.02\n :min-order-size 0.0001\n)".to_string()))]).into_pyobject(py).unwrap(),
                    #[cfg(feature = "fixed_expiry_future")]
                    Utc::now()
                ).unwrap();
                let strategy_key = StrategyKey::new_py(
                    TraderAddress::parse_eth_address("0x0000000000000000000000000000000000000001")
                        .unwrap(),
                    StrategyIdHash::default(),
                );
                smt.store_strategy(
                    strategy_key,
                    Some(Strategy::default_py(&PyType::new::<Strategy>(py))),
                )
                .unwrap();
                let expected_root = smt.root();

                let keys = vec![strategy_key.encode_key_py()];
                let proof = smt.merkle_proof(keys.clone()).unwrap();
                assert!(
                    proof
                        .inner
                        .verify::<Keccak256Hasher>(
                            &expected_root.into(),
                            keys.into_iter()
                                .map(|k| {
                                    let k = k.into();
                                    (k, smt.inner.get(&k).unwrap().to_h256())
                                })
                                .collect(),
                        )
                        .unwrap()
                );
            })
        }
    }
}
