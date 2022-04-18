from setuptools import setup

with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="vpype-occult",
    version="0.1.0",
    description="Occlusion plug-in for vpype",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loic Goulefert",
    url="https://github.com/LoicGoulefert/occult",
    license=license,
    packages=["occult"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Topic :: Multimedia :: Graphics",
        "Environment :: Plugins",
    ],
    setup_requires=["wheel"],
    install_requires=[
        "click",
        "numpy",
        "shapely>=1.8.0",
        "vpype>=1.9,<2.0",
    ],
    entry_points="""
            [vpype.plugins]
            occult=occult.occult:occult
        """,
)
