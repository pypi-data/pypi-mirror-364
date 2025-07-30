use pyo3::prelude::*;

mod ddx;
mod decimal;
mod h256;

pyo3_stub_gen::define_stub_info_gatherer!(stub_info);

use pyo3::prelude::Bound;

trait SubModule {
    const NAME: &'static str;

    fn init_submodule<'py>(py: Python<'py>, module: &Bound<'py, PyModule>) -> PyResult<()>;
    fn finish_submodule<'py>(py: &Python<'py>, module: &Bound<'py, PyModule>) -> PyResult<()>;

    fn add_submodule<'py>(py: Python<'py>, parent_mod: &Bound<'py, PyModule>) -> PyResult<()> {
        let module: Bound<'py, PyModule> = PyModule::new(py, Self::NAME)?;
        Self::init_submodule(py, &module)?;
        parent_mod.add_submodule(&module)?;
        Self::finish_submodule(&py, &module)?;
        Ok(())
    }
}

/// Rust bindings and utils for Python
///
/// Note the pyo3 name aliasing to `_rust`, expected usage is: `from ddx._rust import ...`.
#[pymodule]
#[pyo3(name = "_rust")]
pub fn ddx_python(py: Python, module: &Bound<'_, PyModule>) -> PyResult<()> {
    decimal::add_submodule(py, module)?;
    h256::add_submodule(py, module)?;
    ddx::add_submodule(py, module)?;

    Ok(())
}
