from setuptools import setup, find_packages

setup(
    name="pyzup",
    version="0.1.0",
    description="Reusable upload handler for PDF, PPTX, DOCX, and ZIPs",
    author="Punit Tripathi, Mohd. Amir",
    author_email="tripathi.punit@proton.me, amir.zilli@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Werkzeug==3.1.3",
        "loguru==0.7.3",
    ],
    python_requires=">=3.7",
)