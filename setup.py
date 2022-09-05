from sys import version_info

from setuptools import find_packages, setup

minimum_python_version = (3, 6, 0)

if version_info[:3] < minimum_python_version:
    raise RuntimeError(
        'Unsupported python version {}. Please use {} or newer'.format(
            '.'.join(map(str, version_info[:3])),
            '.'.join(map(str, minimum_python_version)),
        )
    )


setup(
    name='rt-operator',
    version='0.1.0',
    packages=find_packages(),
    author='Chris Love',
    author_email='christopherlove68@gmail.com',
    include_package_data=True,
    install_requires=[
        'kubernetes>=24.0.0,<24.3.0',
    ],
    entry_points={
        'console_scripts': [
            "rt-operator = rt_operator.rtoperator:main",
        ]
    },
    data_files=[
        ('etc', ['config/rt-operator.yaml']),
        ('service', ['rt-operator.service'])
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX :: Linux",
    ]
)