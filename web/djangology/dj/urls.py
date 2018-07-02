from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # Uncomment the next line to enable the admin:
    #(r'^admin/c/', include('django.contrib.admindocs.urls')),
    (r'^project/upload/(?P<project_id>\d+)/$', 'dj.views.upload_file'),
    (r'^project/upload/$', 'dj.views.upload_file'),
    (r'^project/$', 'dj.views.projectList'),
    (r'^projectEdit/(?P<project_id>\d+)/$', 'dj.views.projectEdit'),
    (r'^saveAnnotationType/(?P<project_id>\d+)/$', 'dj.views.saveAnnotationType'),
    (r'^saveAnnotationType/$', 'dj.views.saveAnnotationType'),
    (r'^projectEdit/$', 'dj.views.projectEdit'),
    (r'^projectDelete/$', 'dj.views.projectDelete'),
    (r'^projectSave/$', 'dj.views.projectSave'),
    (r'^projectSaveDocuments/$', 'dj.views.projectSaveDocuments'),
    (r'^editAnnotator/(?P<annotator_id>\d+)/$', 'dj.views.editAnnotator'),
    (r'^editAnnotator/$', 'dj.views.editAnnotator'),
    (r'^deleteAnnotator/$', 'dj.views.deleteAnnotator'),
    (r'^iaa/(?P<annotator_id1>\d+)/(?P<annotator_id2>\d+)/(?P<project_id>\d+)/$', 'dj.views.iaaStats'),
    (r'^iaa/', 'dj.views.iaaStats'),
    (r'^docCompare/(?P<document_id>\d+)/(?P<annotator_id1>\d+)/(?P<annotator_id2>\d+)/$', 'dj.views.docCompare'),
    (r'^index/$', 'dj.views.index'),
    (r'^documents/(?P<document_id>\d+)/(?P<annotator_id>\d+)/$', 'dj.views.documentByAnnotator'),
    (r'^documents/(?P<document_id>\d+)/$', 'dj.views.documentByAnnotator'),
    (r'^documents/jsonout/$', 'dj.views.jsonoutput'),
    (r'^documents/submit/$', 'dj.views.docSubmit'),
    (r'^documents/$', 'dj.views.start'),
    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name':'dj/login.html'}),
	(r'^$', 'django.contrib.auth.views.login', {'template_name':'dj/login.html'}),
	(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'template_name':'dj/logout.html'}),
    (r'^annotations/new/$', 'dj.views.newAnnotation'),   
    (r'^documents/(?P<document_id>\d+)/newQuestion/$', 'dj.views.newQuestion'),   
    (r'^documents/(?P<document_id>\d+)/newReponse/$', 'dj.views.newReponse'),   
    (r'^documents/(?P<docID>\d+)/delete/$', 'dj.views.deleteQuestion'),   
    (r'^annotations/update/$', 'dj.views.updateAnnotation'),   

)

