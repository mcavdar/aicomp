from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # Uncomment the next line to enable the admin:
    (r'^admin/c/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
    (r'^admin/doc/$', include('django.contrib.admindocs.urls')),
	(r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': './dj/media/'}),  
    # include all dj urls
    (r'^', include('dj.urls')),

)

