from setuptools import setup, find_packages

setup(
    name="png2jpg-converter", 
    version="0.1.0", 
    description="A simple PNG to JPG converter using Python",
    author="Azeem Teli",  
    packages=find_packages(),
    install_requires=["Pillow"],
    entry_points={
        "console_scripts": [
            "png2jpg=png2jpg.converter:main"
        ]
    },
)