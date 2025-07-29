import setuptools


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="Python-FastUI-Widgets",
    version="1.0.2",
    keywords="pyside6 fastui widgets",
    author="NumBNN",
    author_email="NumBNN@outlook.com",
    description="FastUI on PySide6",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=None,
    packages=setuptools.find_packages(),
    install_requires=[
        "PySide6>=6.4.2",
        "Python-FastUI-Window>=1.0.2",
        "darkdetect",
    ],
    extras_require = {
        'full': ['scipy', 'pillow', 'colorthief']
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ],
    project_urls={
    }
)
