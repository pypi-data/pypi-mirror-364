from setuptools import setup, find_packages

setup(
    name="procx",
    version="0.1.0",
    author="Duxiao Hao",
    description="Object-Centric and Explainable Process Mining for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["pandas", "networkx", "scikit-learn", "shap", "matplotlib"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.8",
)
