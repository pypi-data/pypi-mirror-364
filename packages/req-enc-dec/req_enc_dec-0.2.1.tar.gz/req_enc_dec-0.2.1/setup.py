from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='req_enc_dec',
    version='0.2.1',
    packages=find_packages(),
    install_requires=[
        'pycryptodome>=3.10.1',
    ],
    author='Jahan',
    author_email='ambition_xu@163.com',
    description='Request/Response Encryption/Decryption Middleware',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    keywords='middleware encryption decryption',
    url='https://github.com/Michaelxwb/ReqEncDec',
)
