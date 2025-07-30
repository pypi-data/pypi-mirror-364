extern crate scrapr_bindings;

use pyo3::prelude::*;

#[pymodule]
pub fn scraprr(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(scrapr_bindings::fetch_http, m)?)?;
    m.add_function(wrap_pyfunction!(scrapr_bindings::extract_tag, m)?)?;
    m.add_function(wrap_pyfunction!(scrapr_bindings::extract_attribute, m)?)?;
    m.add_function(wrap_pyfunction!(scrapr_bindings::extract_links, m)?)?;
    m.add_function(wrap_pyfunction!(scrapr_bindings::fetch_https, m)?)?;
    m.add_function(wrap_pyfunction!(scrapr_bindings::fetch_url, m)?)?;
    m.add_function(wrap_pyfunction!(
        scrapr_bindings::fetch_http_with_options,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        scrapr_bindings::fetch_https_with_options,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        scrapr_bindings::fetch_url_with_options,
        m
    )?)?;

    m.add_class::<scrapr_bindings::RequestOptions>()?;

    Ok(())
}

pub use scrapr_core::{
    ParsedUrl, RequestOptions, build_url, extract_attribute, extract_links, extract_tag,
    fetch_http, fetch_http_with_options, fetch_https, fetch_https_with_options, fetch_url,
    fetch_url_with_options, format_headers,
};
