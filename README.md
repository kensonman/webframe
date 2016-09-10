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
		INSTALLED_APPS += ('webframe',)





2. Add the ABSOLUTE_PATH provider:

		#file: settings.py #in Django 1.9
		TEMPLATES = [
		   #...
		   'context_processors':[
		      #...
		      'webframe.providers.absolute_path', 'webframe.providers.fmt_injection', 'webframe.providers.template_injection'
		      #...
		   ]
		]

3. Install the Middleware

		#file: settings.py
		MIDDLEWARE_CLASSES += [
			'webframe.LangMiddleware.LangMiddleware',
			'webframe.CurrentUserMiddleware.CurrentUserMiddle',
			'django.middleware.locale.LocaleMiddleware',
		]

Application
----
1. You can use the below script to get the current user. It very useful to implement the last_modified_by in model.

		#file: modles.py
		def get_current_user():
			from threading import local
			thread=local()
			if hasattr(thread, 'user'):
				return thread.user
			else:
				from django.contrib.auth.models import AnonymousUser
				return AnonymousUser()

		...
		class MyModel(models.Model):
			last_modify_by = models.ForeignKey(settings.AUTH_USER_MODEL,default=get_current_user)
		...
