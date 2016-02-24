Introduction
=====
WEBFRAME is the the web-app template to start the development of the web-application quickly.


Installation
----
- Download the zip file and extract to your project folder. Then do the configuration;
- Checkout as a submodule in GIT. Then do the configuration;

		git submodule add ssh://dev.breakthrough.org.hk/var/git/kenson.webframe.git dev/webframe

Configuration
----
1. Add the `webframe` into `INSTALLED_APPS`:

		#file: settings.py
		INSTALLED_APPS += ('webframe')
2. Add the ABSOLUTE_PATH provider:

		#file: settings.py #in Django 1.9
		TEMPLATES = [
		   #...
		   'context_processors':[
		      #...
		      'webframe.providers.absolute_path',
		      #...
		   ]
		]

