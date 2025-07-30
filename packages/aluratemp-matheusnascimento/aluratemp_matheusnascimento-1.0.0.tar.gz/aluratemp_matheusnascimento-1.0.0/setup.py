from setuptools import setup, find_packages
setup(
    name = 'aluratemp-matheusnascimento',
    version = '1.0.0',
    author = 'Matheus Nascimento',
    author_email = 'matheus.maciel34@gmail.com',
    packages = find_packages(),
    description = 'Um simples conversor de temperatura (Celsius - Fahrenheit)',
    long_description = 'Um simples conversor de temperatura, com funções para '
                        + 'conversão de Celsius para Fahrenheit e vice-versa, '
                        + 'usado para um post no Blog da Alura',
    url = 'https://github.com/yanorestes/aluratemp',
    project_urls = {
        'Código fonte': 'https://github.com/yanorestes/aluratemp',
        'Download': 'https://github.com/yanorestes/aluratemp/archive/1.0.0.zip'
    },
    license = 'MIT',
    keywords = 'conversor temperatura alura'
    """classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Portuguese (Brazilian)',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Internationalization',
        'Topic :: Scientific/Engineering :: Physics'
    ]"""
)


