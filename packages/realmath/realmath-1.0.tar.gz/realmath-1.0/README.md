# realmath

RealMath is a simple and smart Python math utility library by Benyamin Ghaem.

## Features
- Smart rounding functions
- Safe math operations (log, exp, divide, sqrt)
- Clamp and rounding helpers

## Installation

```bash
pip install realmath


from realmath import rond, rlog

print(rond(150))   # 200
print(rlog(10))    # 2.302585092994046


---

### فایل: `setup.py`

```python
from setuptools import setup, find_packages

setup(
    name='realmath',
    version='0.1.0',
    description='Smart rounding and safe math utilities in Python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Benyamin Ghaem',
    url='https://github.com/benionclouds/realmath',
    packages=find_packages(),
    py_modules=['realmath'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
