from setuptools import setup, find_packages

setup(
    name="django_app_booster",
    version="0.3.1",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'createapp=app_booster.cli:main',        ],
    },
)
