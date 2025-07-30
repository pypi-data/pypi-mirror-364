"""Setup configuration for mcp-testing-sensei package."""

from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='mcp-testing-sensei',
    version='0.2.0',
    author='Kourtni Marshall',
    description='An MCP server to enforce testing standards',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kourtni/mcp-testing-sensei',
    packages=find_packages(),
    py_modules=['mcp_server', 'linter'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'mcp>=1.6.0',
    ],
    entry_points={
        'console_scripts': [
            'mcp-testing-sensei=mcp_server:main',
        ],
    },
)
