pub mod python {
    use crate::{
        Error,
        types::{
            global::TokenAddress,
            primitives::{OrderSide, TokenSymbol},
        },
    };
    use pyo3::{exceptions::PyException, prelude::*, types::PyType};
    use pyo3_stub_gen::{create_exception, derive::*};
    use std::str::FromStr;

    create_exception!(ddx._rust, CoreCommonError, PyException, "DDX Core error");

    impl From<Error> for pyo3::PyErr {
        fn from(e: Error) -> Self {
            CoreCommonError::new_err(e.to_string())
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl TokenSymbol {
        /// Construct a `TokenSymbol` from the on-chain token `address`.
        #[classmethod]
        fn from_address(_cls: &Bound<'_, PyType>, address: TokenAddress) -> Self {
            address.into()
        }

        /// Return the canonical on-chain address for this token.
        fn address(&self) -> TokenAddress {
            TokenAddress::from(*self)
        }
    }

    #[gen_stub_pymethods]
    #[pymethods]
    impl OrderSide {
        /// Parse an `OrderSide` (`"Bid"` or `"Ask"`) from its string `name`.
        #[new]
        fn new(name: &str) -> PyResult<Self> {
            Self::from_str(name).map_err(|e| CoreCommonError::new_err(e.to_string()))
        }
    }
}
