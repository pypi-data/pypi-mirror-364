from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="pyzup",
    version="0.1.2",
    description="Reusable upload handler for PDFs, DOCX, PPTX, ZIPs",
    long_description=long_description,
    long_description_content_type="text/markdown", 
    author="Punit Tripathi, Mohd. Amir",
    author_email="tripathi.punit@proton.me, amir.zilli@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Werkzeug==3.1.3",
        "loguru==0.7.3",
    ],
    python_requires=">=3.7",
)
