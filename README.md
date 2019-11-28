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

      ```python    
      #file: settings.py
      INSTALLED_APPS += ('webframe', 'method_override')
      ```

3. Install the context-processors:

      ```python
      #file: settings.py #in Django 1.9
      TEMPLATES = [
         #...
         'context_processors':[
            #...
            'webframe.providers.absolute_path', 'webframe.providers.fmt_injection', 'webframe.providers.template_injection'
            #...
         ]
      ]

      # *Optional*: Specify the django_tables2 template for bootstrap4
      DJANGO_TABLES2_TEMPLATE = 'webframe/tables.html'
      ```

4. Install the Middleware

      ```python
      #file: settings.py
      MIDDLEWARE_CLASSES += [
         'method_override.middleware.MethodOverrideMiddleware',        #django 1.9 or belows
         'webframe.methodoverridemiddleware.MethodOverrideMiddleware', #django 1.10 or aboves
         'webframe.NextURLMiddleware.NextURLMiddleware',               #If using the social_auth_django
         'webframe.LangMiddleware.LangMiddleware',
         'webframe.CurrentUserMiddleware.CurrentUserMiddleware',
         'django.middleware.locale.LocaleMiddleware',
      ]
      ```

5. Setup the [login url](https://docs.djangoproject.com/en/2.0/ref/settings/#std:setting-LOGIN_URL)

      ```python
      #file: settings.py
      LOGIN_URL = 'webframe:login'
      STATIC_ROOT= 'static'
      MEDIA_URL  = '/media/'
      MEDIA_ROOT = 'media'
      DJANGO_TABLES2_TEMPLATE = 'webframe/tables.html'
      ```

Application
----
1. You can use the below script to get the current user. It very useful to implement the last_modified_by in model.

      ```python
      #file: modles.py
      from webframe.CurrentUserMiddleware import get_current_user

      #...
      class MyModel(models.Model):
         last_modify_by = models.ForeignKey(settings.AUTH_USER_MODEL,default=get_current_user)
      #...
      ```

2. Provide the logout features (Optional)

      ```python
      #urls.py
      from django.conf import settings
      from django.conf.urls.static import static
      from django.urls import path, re_path, include

      urlpatterns = [
         #...
         path('webframe/', include('webframe.urls', namespace='webframe')),
      ]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
      ```

Preference
----
The WEBFRAME also support the preference model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS`:

      ```python
      #file: settings.py
      INSTALLED_APPS += ('django_tables2',)
      ```

2. Make sure the context-processor is installed:

      ```python
      #file: settings.py #in Django 1.9
      TEMPLATES = [
         #...
         'context_processors':[
            #...
         'django.template.context_processors.request',
         #...
         ]
      ]
      ```

3. Setup the preference views

      ```python
      #urls.py
      from django.conf import settings
      from django.conf.urls.static import static
      from django.urls import path, re_path, include

      urlpatterns = [
         #...
         path('webframe/', include('webframe.urls', namespace='webframe')),
      ]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
      ```


Users
----
The WEBFRAME also support the User model and related layout. This can be applied into wirely type of application.

To use the preference, following the steps:

1. Add the `django_tables2` into `INSTALLED_APPS` and showing the password field for user:

      ```python
      #file: settings.py
      INSTALLED_APPS += ('django_tables2',)
      AUTH_PASSWORD_REQUIRED=True
      ```

2. Make sure the context-processor is installed:

      ```python
      #file: settings.py #in Django 1.9
      TEMPLATES = [
         #...
         'context_processors':[
            #...
         'django.template.context_processors.request',
         #...
         ]
      ]
      ```

3. Setup the preference views

      ```python
      #urls.py
      from django.conf import settings
      from django.conf.urls.static import static
      from django.urls import path, re_path, include

      urlpatterns = [
         #...
         path('webframe/', include('webframe.urls', namespace='webframe')),
      ]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
      ```

Javascript Translation
----
The WEBFRAME also support the javascript translation. Just add the belows statement into your code.
1. Setup the preference views

      ```python
      #urls.py
      from django.conf import settings
      from django.conf.urls.static import static
      from django.urls import path, re_path, include

      urlpatterns = [
         #...
         path('webframe/', include('webframe.urls', namespace='webframe')),
      ]
      urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
      ```

2. In HTML code add

      ```HTML
      <script type="text/javascript" src="{%url 'webframe:js'%}"></script>
      ```


Social Authentication
------
The social authentication can be supported by django-social-app-auth. The Instruction can be found (here)[https://simpleisbetterthancomplex.com/tutorial/2016/10/24/how-to-add-social-login-to-django.html].

Compile SCSS
----
The package is develed under scss code. It can be customizes the style by scss engine. Execute the following code to compile:

   ```bash
   docker run --rm -v $(pwd):$(pwd) -w $(pwd) jbergknoff/sass scss/base-theme.scss > static/css/base-theme.css
   docker run --rm -v $(pwd):$(pwd) -w $(pwd) jbergknoff/sass scss/rating.scss > static/css/rating.css
   ```


Impersonate Support
-----
The impersonate features are supported by [Impersonate](https://pypi.org/project/django-impersonate/) module.
The quick configuration are as belows:

1. Install the module:
   ```bash
   pip install django-impersonate
   ```

2. Add `impersonate` into INSTALLED_APPS;
3. Add `impersonate.middleware.ImpersonateMiddleware` into MIDDLEWARE;
4. Add impersonate's urls:
   ```python
   #conf/urls.py
   urlpattens=patterns('',
      #...
      url(r'^impersonate/', include('impersonate.urls')),
      #...
   )
   LOGIN_REDIRECT_URL = 'dashboard' #The URL that will redirected after login/impersonate.
   ```
5. Migrate the database settings:
   ```bash
   ./manage.py migrate
   ```

Django-Guardian Support
----
The [django-guardian](https://django-guardian.readthedocs.io/en/stable/overview.html) is the module to support item-level permission. 
The quick configuration are as belows:

1. Install the module:
   ```bash
   pip install django-guardian
   ```

2. Add `guardian` into INSTALLED_APPS;
3. Add `guardian.backends.ObjectPermissionBackend` into authentication backend:
   ```python
   AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'guardian.backends.ObjectPermissionBackend',
   )
   ```
4. Migrate the database settings:
   ```bash
   ./manage.py migrate
   ```

Django AD/LDAP login support
----
To support the AD/LDAP login, please following the below instruction.

1. Install the required package/library
```bash
pip install -y django-auth-ldap python-ldap
```

2. Add the below config into src/conf/settings.py:
```python
# django-auth-ldap
LDAP_ENABLED=os.getenv('LDAP_ENABLED', 'False').lower() in ['true', 't', 'yes', 'y', '1']
if LDAP_ENABLED:
   # LDAP Setting
   LDAP_SERVERS ={   
      'host': os.getenv('LDAP_HOST', 'Your-AD/LDAP-Host'),
      'port': int(os.getenv('LDAP_PORT', '389')),
      'use_ssl': os.getenv('LDAP_USE_SSL', 'False').lower() in ['true', 't', 'yes', 'y', '1'],
   }  
   LDAP_BIND_USER=os.getenv('LDAP_BIND_USER', 'CN=webmaster,OU=IT,OU=BT_Staff,DC=breakthrough,DC=org,DC=hk')
   LDAP_BIND_PWD =os.getenv('LDAP_BIND_PASS', 'BIND Password')
   LDAP_USER_BASE=os.getenv('LDAP_USER_BASE', 'OU=BT_STAFF,DC=breakthrough,DC=org,DC=hk')
   LDAP_GROUP_BASE=os.getenv('LDAP_GROUP_BASE', 'DC=breakthrough,DC=org,DC=hk')
   LDAP_USERNAME_FIELD=os.getenv('LDAP_USERNAME_FIELD', '(sAMAccountName=%(user)s)')
   LDAP_USER_FILTER = os.getenv('LDAP_USER_FILTER', "(&(sAMAccountName=%s)(objectClass=user))")
   LDAP_DEPT_FILTER = os.getenv('LDAP_DEPT_FILTER', "(&(department=%s)(objectClass=user))")
   LDAP_GROUP_FILTER= os.getenv('LDAP_GROUP_FILTER', "(objectClass=group)")
   LDAP_IS_STAFF_FILTER=os.getenv('LDAP_IS_STAFF_FILTER', 'CN=IT_Group,OU=IT,OU=BT_Staff,DC=breakthrough,DC=org,DC=hk|CN=Domain Admins,CN=Users,DC=breakthrough,DC=org,DC=hk')
   LDAP_IS_SUPERUSER_FILTER=os.getenv('LDAP_IS_SUPERUSER_FILTER', 'CN=IT_Group,OU=IT,OU=BT_Staff,DC=breakthrough,DC=org,DC=hk|CN=Domain Admins,CN=Users,DC=breakthrough,DC=org,DC=hk')
   LDAP_USER_FIELDS_MAPPING=os.getenv('LDAP_USER_FIELDS_MAPPING', '{"first_name": "givenName", "last_name": "sn", "email": "mail"}')
   import ldap, json
   from django_auth_ldap.config import LDAPSearch, NestedActiveDirectoryGroupType 

   AUTH_LDAP_SERVER_URI='ldap://%s:%s'%(LDAP_SERVERS['host'], LDAP_SERVERS['port'])
   AUTH_LDAP_BIND_DN=LDAP_BIND_USER
   AUTH_LDAP_BIND_PASSWORD=LDAP_BIND_PWD
   AUTH_LDAP_CONNECTION_OPTIONS={
      ldap.OPT_DEBUG_LEVEL: 1,
      ldap.OPT_REFERRALS: 0,
   }
   AUTH_LDAP_USER_SEARCH=LDAPSearch(LDAP_USER_BASE, ldap.SCOPE_SUBTREE, LDAP_USERNAME_FIELD)
   AUTH_LDAP_GROUP_SEARCH=LDAPSearch(LDAP_GROUP_BASE, ldap.SCOPE_SUBTREE, LDAP_GROUP_FILTER)
   AUTH_LDAP_GROUP_TYPE=NestedActiveDirectoryGroupType()
   AUTH_LDAP_USER_ATTR_MAP=json.loads(LDAP_USER_FIELDS_MAPPING)
   AUTH_LDAP_USER_FLAGS_BY_GROUP={
      # IS_STAFF is not used in this application;
      'is_staff': LDAP_IS_STAFF_FILTER.split('|'),

      # IS_SUPERUSER is used to generated the shortcut buttons
      'is_superuser': LDAP_IS_SUPERUSER_FILTER.split('|'),
   }
   AUTH_LDAP_MIRROR_GROUPS=True
   AUTHENTICATION_BACKENDS=(
      'django_auth_ldap.backend.LDAPBackend',
      'django.contrib.auth.backends.ModelBackend',
   )
```
