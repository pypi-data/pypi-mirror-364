from setuptools import setup, find_packages

setup(
    name="hr-edge-recruit-mcp-server",
    version="0.1.0",
    description="A custom MCP server using FastAPI, AWS, Firebase, and LangChain for real-time audio analysis.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="LLM Lords",
    author_email="prathameshb@incubxperts.com",
    url="https://github.com/yourusername/mcp-server",  # Optional
    packages=find_packages(exclude=["tests*", "debug*", "temp*", "*.db"]),
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    entry_points={
        "console_scripts": [
            "mcp-server=mcp_server.main:main"
        ]
    },
)
