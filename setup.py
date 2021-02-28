from setuptools import setup, find_packages

setup(
        name='web-player-server',
        version='0.0.1',
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'flask', 'flask-cors', 'tinydb', 'pyyaml'
            ]
        )