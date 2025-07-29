import setuptools

PACKAGE_NAME = "internet-domain-local"
package_dir = PACKAGE_NAME.replace("-", "_")

setuptools.setup(
    name=PACKAGE_NAME,
    version='0.0.33',  # https://pypi.org/project/internet-domain-local/
    author="Circles",
    author_email="info@circlez.ai",
    description="PyPI Package for Circles internet-domain-local Python",
    long_description="PyPI Package for Circles internet-domain-local Python",
    long_description_content_type='text/markdown',
    url="https://github.com/circles-zone/internet-domain-local-python-package",
    packages=[package_dir],
    package_dir={package_dir: f'{package_dir}/src'},
    package_data={package_dir: ['*.py']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'logger-local>=0.0.135',
        'database-mysql-local>=0.0.290',
        'storage-local>=0.1.41'
    ],
)
