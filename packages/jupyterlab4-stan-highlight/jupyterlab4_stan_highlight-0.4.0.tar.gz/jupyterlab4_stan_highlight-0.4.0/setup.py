from setuptools import setup, find_packages

setup(
    name="jupyterlab4-stan-highlight",
    version="0.4.0",
    description="JupyterLab extension to highlight Stan syntax",
    author="Oonishi Takato",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "jupyterlab>=4.0.0"
    ],
    zip_safe=False,
    entry_points={
        "jupyterlab.extension": [
            "jupyterlab4-stan-highlight = jupyterlab4_stan_highlight"
        ]
    },
)
