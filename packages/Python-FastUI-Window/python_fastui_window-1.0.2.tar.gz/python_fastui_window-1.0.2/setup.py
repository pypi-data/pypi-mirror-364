import setuptools


with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name="Python-FastUI-Window",
    version="1.0.2",
    keywords="Num frameless",
    author="NumBNN",
    author_email="NumBNN@outlook.com",
    description="FastUI Frameless Window on PySide6",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=None,
    packages=setuptools.find_packages(),
    install_requires=[
        "pywin32;platform_system=='Windows'",
        "pyobjc;platform_system=='Darwin'",
        "PyCocoa;platform_system=='Darwin'",
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent'
    ]
)
