from setuptools import setup, find_packages

setup(
    name="p2pchat",
    version="0.1.28",
    packages=find_packages(include=['p2pchat', 'p2pchat.*']),
    include_package_data=True,
    package_data={
        'p2pchat': [
            'api/*.py',
            'utils/*.py',
            'bot.py',
            'commands.py',
            'events.py',
            'client.py'
        ],
    },
    install_requires=[
        'aiohttp',
        'asyncio'
    ]
)