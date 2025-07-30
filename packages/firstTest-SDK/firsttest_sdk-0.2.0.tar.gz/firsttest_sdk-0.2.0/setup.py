# setup.py
from setuptools import setup, find_packages

setup(
    name='firstTest_SDK',
    version='0.2.0',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.1',
    ],
    description='AI图像分类模型的Python SDK',
    author='desaiot',
    author_email='2607074788@qq.com',
    url='https://github.com/desaiot/firstTest_SDK',
)