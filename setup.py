from setuptools import setup


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="occult",
    version="0.1.0",
    description="",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Loic Goulefert",
    url="",
    license=license,
    packages=["occult"],
    install_requires=[
        'click',
        'vpype @ git+https://github.com/abey79/vpype.git',
    ],
    entry_points='''
            [vpype.plugins]
            occult=occult.occult:occult
        ''',
)
