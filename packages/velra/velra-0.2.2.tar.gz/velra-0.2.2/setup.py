from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

setup(
    name='velra',  # PyPI package name, lowercase
    version='0.2.2',
    description='A powerful interface that makes web development easier and faster',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Theodore Cromwell',
    author_email='tspcromwell@gmail.com',
    url='https://github.com/apersonithink12/velra',
    packages=find_packages(),
    install_requires=[
        'Flask>=2.0',
        'Jinja2>=3.0',
    ],
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Framework :: Flask',
        'Operating System :: OS Independent',
    ],
    license='MIT',
    include_package_data=True,
    keywords='web development framework',
)
