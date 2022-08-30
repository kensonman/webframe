from setuptools import setup, find_packages
from setuptools.command.install import install                                      
import warnings
import sys

class CustomInstall(install):                                                       
   def run(self):                                                                  
      msg='WARNING: Install pycryptodome for Crypto related features'
      warnings.warn(msg)
      sys.stdout.write(msg)
      sys.stdout.flush()
      install.run(self)  

setup(
    name='webframe',
    version='2.12.3',    
    description='My django framework',
    url='https://repos.kenson.idv.hk/kenson/webframe',
    author='Kenson Man',
    author_email='kenson.idv.hk@gmail.com',
    license='Apache 2.0',
    packages=find_packages('.', exclude=['tests']),
    cmdclass={'install': CustomInstall},
    install_requires=[
		'amqp>=5.1.1',
		'asgiref>=3.5.2',
		'billiard>=3.6.4.0',
		'bleach>=5.0.1',
		'celery>=5.2.7',
		'click>=8.1.3',
		'click-didyoumean>=0.3.0',
		'click-plugins>=1.1.1',
		'click-repl>=0.2.0',
		'deprecation>=2.1.0',
		'Django>=3.2.15,<4.0.0',
		'django-ajax-selects>=2.2.0',
		'django-guardian>=2.4.0',
		'django-impersonate>=1.8.2',
		'django-json-widget>=1.1.1',
		'django-maintenance-mode>=0.16.3',
		'django-method-override>=1.0.4',
		'django-restframework>=0.0.1',
		'django-summernote>=0.8.20.0',
		'django-tables2>=2.4.1',
		'djangorestframework>=3.13.1',
		'future>=0.18.2',
		'kombu>=5.2.4',
		'Markdown>=3.4.1',
		'netaddr>=0.8.0',
		'packaging>=21.3',
		'Pillow>=9.2.0',
		'prompt-toolkit>=3.0.30',
		'pyparsing>=3.0.9',
		'python-dateutil>=2.8.2',
		'python-fsutil>=0.6.1',
		'pytimeparse>=1.1.8',
		'pytz>=2022.2.1',
		'six>=1.16.0',
		'sqlparse>=0.4.2',
		'vine>=5.0.0',
		'wcwidth>=0.2.5',
		'webencodings>=0.5.1',
                     ],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Programming/Web',
        'License :: OSI Approved :: Apache License',  
        'Operating System :: POSIX :: Linux',        
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
