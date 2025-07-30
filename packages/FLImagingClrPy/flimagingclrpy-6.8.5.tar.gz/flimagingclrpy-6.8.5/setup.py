from setuptools import setup, find_packages

setup(
    name="FLImagingClrPy",
    version="6.8.5",
    packages=find_packages(),
    install_requires=[
        "pythonnet>=3.0.5", 
    ],
    author="Fourth Logic Incorporated",
    author_email="support@fourthlogic.co.kr",
    description="FLImaging(R) CLR for Python",
    license="MIT",
    python_requires='>=3.8.0',
)