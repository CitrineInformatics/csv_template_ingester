from setuptools import setup, find_packages

setup(name='csv_template_ingester',
    version='1.1.0',
    url='http://github.com/CitrineInformatics/csv_template_ingester',
    description='Converts a specialized CSV/XLSX or XLS file to a physical information file.',
    author='Jo Hill',
    author_email='jo@citrine.io',
    packages=find_packages(),
    install_requires=[
        'pypif>=2.1.0,<3',
        'xlrd',
        'pytest'
    ],
    entry_points={
        'citrine.dice.converter': [
            'template_csv = csv_template_ingester.converter',
        ],
    },
)
