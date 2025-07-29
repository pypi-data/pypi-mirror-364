from setuptools import setup, find_packages

setup(
    name="mcp-benchmark",
    version="0.0.1dev0",
    packages=find_packages(),
    author="Xing Han Lù",
    author_email="mcp-benchmark@googlegroups.com",
    description="A benchmark for MCP.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/xhluca/mcp-benchmark",
    install_requires=['mcp[cli]', 'httpx'],
)
