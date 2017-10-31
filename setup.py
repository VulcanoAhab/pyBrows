from distutils.core import setup

setup(
    name="pyBrows",
    version='0.1.0',
    author="VulcanoAhab",
    packages=["pyBrows", "pyBrows.headers"],
    url="https://github.com/VulcanoAhab/pyBrows.git",
    description="Browsers Utils",
    install_requires=[
        "requests==2.18.4",
        "selenium==3.6.0",
        "lxml==4.1.0",
        ]
)
