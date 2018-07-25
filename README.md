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
		INSTALLED_APPS += ('webframe', 'method_override')

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
			'method_override.middleware.MethodOverrideMiddleware', #django 1.9 or belows
			'webframe.methodoverridemiddleware.MethodOverrideMiddleware', #django 1.10 or aboves
			'webframe.LangMiddleware.LangMiddleware',
			'webframe.CurrentUserMiddleware.CurrentUserMiddleware',
			'django.middleware.locale.LocaleMiddleware',
		]

5. Setup the [login url](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-LOGIN_URL)

      #file: settings.py
      LOGIN_URL = 'webframe:login'

Application
----
1. You can use the below script to get the current user. It very useful to implement the last_modified_by in model.

		#file: modles.py
		from webframe.CurrentUserMiddleware import get_current_user

		...
		class MyModel(models.Model):
			last_modify_by = models.ForeignKey(settings.AUTH_USER_MODEL,default=get_current_user)
		...

2. Provide the logout features (Optional)

		#urls.py
      from django.conf import settings
      from django.urls import path, re_path, include
      from webframe.urls import urlpatterns as webframe

		urlpatterns = [
			#...
         path('webframe/', include((webframe, 'webframe'), namespace='webframe')),
		]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Preference
----
The WEBFRAME also support the preference model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS`:

		#file: settings.py
		INSTALLED_APPS += ('django_tables2',)

2. Make sure the context-processor is installed:

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
      from django.conf import settings
      from django.urls import path, re_path, include
      from webframe.urls import urlpatterns as webframe

		urlpatterns = [
			#...
         path('webframe/', include((webframe, 'webframe'), namespace='webframe')),
		]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


Users
----
The WEBFRAME also support the User model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS` and showing the password field for user:

		#file: settings.py
		INSTALLED_APPS += ('django_tables2',)
      AUTH_PASSWORD_REQUIRED=True

2. Make sure the context-processor is installed:

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
      from django.conf import settings
      from django.urls import path, re_path, include
      from webframe.urls import urlpatterns as webframe

		urlpatterns = [
			#...
         path('webframe/', include((webframe, 'webframe'), namespace='webframe')),
		]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

Javascript Translation
----
The WEBFRAME also support the javascript translation. Just add the belows statement into your code.
1. Setup the preference views

		#urls.py
      from django.conf import settings
      from django.urls import path, re_path, include
      from webframe.urls import urlpatterns as webframe

		urlpatterns = [
			#...
         path('webframe/', include((webframe, 'webframe'), namespace='webframe')),
		]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

2. In HTML code add

		<script type="text/javascript" src="{%url 'webframe:js'%}"></script>


Social Authentication
------
The social authentication can be supported by django-social-app-auth. The Instruction can be found (here)[https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html].
