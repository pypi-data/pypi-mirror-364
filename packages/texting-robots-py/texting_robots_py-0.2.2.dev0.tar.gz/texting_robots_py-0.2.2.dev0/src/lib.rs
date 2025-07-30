use pyo3::prelude::*;

#[pyclass]
struct Robot(texting_robots::Robot);

#[pymethods]
impl Robot {
    #[new]
    #[pyo3(signature = (agent, txt))]
    fn new(agent: &str, txt: &[u8]) -> PyResult<Self> {
        Ok(Self(texting_robots::Robot::new(agent, txt)?))
    }

    #[getter]
    fn delay(&self) -> Option<f32> {
        self.0.delay
    }

    #[getter]
    fn sitemaps(&self) -> Vec<String> {
        self.0.sitemaps.clone()
    }

    #[pyo3(signature = (url))]
    fn allowed(&self, url: &str) -> bool {
        self.0.allowed(url)
    }
}

#[pymodule(name = "texting_robots")]
fn texting_robots_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Robot>()?;
    Ok(())
}
