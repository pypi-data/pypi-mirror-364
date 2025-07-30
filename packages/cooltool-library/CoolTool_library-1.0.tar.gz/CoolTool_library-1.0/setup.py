from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='CoolTool_library',
    version='1.0',
    packages=['cooltool_library'],
    author='Quadzeco',
    author_email='example@example.com',
    description='Simple library with many function to help you with consol project',
    long_description=long_description,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
