from setuptools import setup, Extension
from pathlib import Path


def read_readme() -> str:
    readme_path = Path(__file__).parent / "README.md"
    if readme_path.exists():
        return readme_path.read_text()
    return "Non-invasive performance metrics collection for Python"


module = Extension(
    "clinic_monitor",
    sources=[str(Path("clinic_py") / "monitor.c")],
)

setup(
    name="clinic-py",
    version="0.1.0",
    description="Non-invasive performance metrics collection for Python",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="fullzer4",
    author_email="gabrielpelizzaro@gmail.com",
    license="MIT",
    packages=["clinic_py"],
    ext_modules=[module],
)