from setuptools import setup, find_packages

setup(
    name='romanRekhta',
    version='0.1.0',
    author='Muhammad Ammar',
    author_email='ammarshafique677@gmail.com',
    description='An NLP library for Roman Urdu text preprocessing, tokenization, and stopword handling.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/is-ammar/romanRekhta',  
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'emoji>=2.0.0'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    python_requires='>=3.7',
    keywords='roman urdu nlp stopwords tokenization emoji preprocessing',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/is-ammar/romanRekhta',
        'Tracker': 'https://github.com/is-ammar/romanRekhta/issues',
    },
)
