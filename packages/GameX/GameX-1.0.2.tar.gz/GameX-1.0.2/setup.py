from setuptools import setup, find_packages
#python setup.py sdist
setup(
    name="GameX",
    version="1.0.2",
    packages=find_packages(),
    description=("Welcome to GameX, a product developed using Pygame! \
                 It is more suitable for people have just switched from \
                 Scratch to Python. This lib is simple and easy to use."),
    package_data={
        "GameX": [r"GameX/gameX.py", r"GameX/*"]
    },
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown"
)