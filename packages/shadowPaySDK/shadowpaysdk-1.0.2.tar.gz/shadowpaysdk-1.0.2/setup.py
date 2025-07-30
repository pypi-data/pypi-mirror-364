from setuptools import setup, find_packages

setup(
    name='shadowPaySDK',
    version='1.0.2',
    description='ShadowPay SDK for ERC20/ERC721 and P2P smart contract interaction',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='dazay',
    author_email='shadowpay.protocol@gmail.com',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'web3',
        'requests',
        'solana',
        'anchorpy',
        
        'solders',
        'httpx==0.28.1'                 

    ],
    python_requires='>=3.9',
)
