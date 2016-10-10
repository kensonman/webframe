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
1. Install the django_tables2 package:

		sudo pip install django_tables2

2. Add the `webframe` into `INSTALLED_APPS`:

		#file: settings.py
		INSTALLED_APPS += ('webframe',)

3. Install the context-processors:

		#file: settings.py #in Django 1.9
		TEMPLATES = [
		   #...
		   'context_processors':[
		      #...
		      'webframe.providers.absolute_path', 'webframe.providers.fmt_injection', 'webframe.providers.template_injection'
		      #...
		   ]
		]

4. Install the Middleware

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
		from webframe.CurrentUserMiddleware import get_current_user

		...
		class MyModel(models.Model):
			last_modify_by = models.ForeignKey(settings.AUTH_USER_MODEL,default=get_current_user)
		...

Javascript Translation (optionsal)
----
The WEBFRAME also support the javascript translation. Just add the belows statement into your code.
1. Setup the preference views

		#urls.py
		urlpatterns = [
			#...
			url(r'^jsi18n/webframe/$', javascript_catalog, {'packages':('webframe',),'domain':'django'}, name='webframe-js'),
			#...
		]

2. In HTML code add

		<script type="text/javascript" src="{%url 'webframe-js'%}"></script>


Preference (optional)
----
The WEBFRAME also support the preference model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS`:

		#file: settings.py
		INSTALLED_APPS += ('django_tables2',)

2. Install the context-processors:

		#file: settings.py #in Django 1.9
		TEMPLATES = [
		   #...
		   'context_processors':[
		   	#...
			'django.template.context_processors.request',
			#...
		   ]
		]

3. Setup the preference views

		#urls.py
		from webframe import views as webframe_view

		urlpatterns = [
			#...
			url(r'^users/(?P<user>[^/]+)/prefs/?$', webframe_view.prefs, name='preferences'),
			url(r'^users/(?P<user>[^/]+)/prefs/(?P<prefId>[^/]+)/?$', webframe_view.pref, name='preference'),
			#...
		]


Users (optional)
----
The WEBFRAME also support the User model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS`:

		#file: settings.py
		INSTALLED_APPS += ('django_tables2',)

2. Install the context-processors:

		#file: settings.py #in Django 1.9
		TEMPLATES = [
		   #...
		   'context_processors':[
		   	#...
			'django.template.context_processors.request',
			#...
		   ]
		]

3. Setup the preference views

		#urls.py
		from webframe import views as webframe_view

		urlpatterns = [
			#...
			url(r'^users/?$', webframe_view.users, name='users'),
			url(r'^users/(?P<user>[^/]+)/?$', webframe_view.user, name='user'),
			#...
		]
