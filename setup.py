from setuptools import setup

setup(
    name='aloft-services',
    packages=['aloft_services'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask-markdown',
        'PyPDF2',
        'gunicorn',
        'mistune',
        'gitpython'
    ]
)
