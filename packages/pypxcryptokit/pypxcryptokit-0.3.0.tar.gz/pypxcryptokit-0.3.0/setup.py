from setuptools import setup, find_packages

setup(
    name="pypxcryptokit",
    version="0.3.0",
    description="Python cryptographic library implementing Double Ratchet and X3DH protocols",
    long_description="A Python cryptographic library providing modern secure messaging primitives, including Double Ratchet and X3DH, designed for end-to-end encryption and forward secrecy.",
    author="UNSHD-X7",
    author_email="",
    url="https://github.com/UNSHD-X7/PROJECT-PX1",
    packages=find_packages(),
    install_requires=[
        "cryptography>=41.0.0",
        "xeddsa>=0.1.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ],
    python_requires='>=3.8',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Topic :: Security :: Cryptography",
    ],
    include_package_data=True,
    package_data={
        "pypxcryptokit": ["*.py"],
    },
    keywords="cryptography double-ratchet x3dh signal python end-to-end encryption",
)
