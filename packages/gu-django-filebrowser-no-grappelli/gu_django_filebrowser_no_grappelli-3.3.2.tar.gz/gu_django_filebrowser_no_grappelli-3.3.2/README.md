gu-django-filebrowser-no-grappelli
==================================

django-filebrowser for default Django admin site.  
Based on https://github.com/wardi/django-filebrowser-no-grappelli,
https://github.com/sehmaschine/django-filebrowser v3.1 

Added two methods:

- filebrowser.get_default_dir

- filebrowser.set_default_dir(dir)

Get/set a dir, in which filebrowsers, which will be rendered in current request/thread will be opened.

##Changelist

###v3.3.2
- compatibility with Django 4 (deprecated template tags ifequal ifnotequal)

###v3.3.1
- compatibility with Django 4

###v3.2.5
- compatibility with a CVE-2022-23833 django fix

###v3.2.4 
- template layout reworked to match Django 3 standart

###v3.2.3, v3.2.2, v3.2.1 
- Python 3 / Dajngo 3 compatibility 
