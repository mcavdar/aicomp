import unittest
from dj.models import *
import datetime
import iaa
from django.test.client import Client
from django.test import client 
import pdb
import re
import os
import zipfile

try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from django.utils import simplejson

from dj.urls import patterns
from django.core.urlresolvers import reverse

# retrieves a set of links for any html page
def links(html):
    # get all href='s into a list
    pattern = """href=['"][^'"]*"""
    rawLinks = re.findall(pattern, html)

    # remove "href=" from each href
    for i in range(len(rawLinks)):
        rawLinks[i] = rawLinks[i][6:]

    return rawLinks

def lists_are_similar(a,b):
    """ Return true if 2 lists are equal """
    #pdb.set_trace()
    for i in a:
        if not i in b:
            return False
    return True

class IaaTestCase(unittest.TestCase):
    def setUp(self):
        self.annotator1 = Annotator.objects.create(id="100", username="100")
        self.annotator2 = Annotator.objects.create(id="101", username="101")
        self.project=Project.objects.create()
        self.doc1=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title1")
        self.doc2=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title2")
        self.annotator1.documents.add(self.doc1)
        self.annotator1.documents.add(self.doc2)
        self.annotator2.documents.add(self.doc1)
        self.annotator2.documents.add(self.doc2)
        self.annotationType=AnnotationType.objects.create(type="test",project=self.project)
        self.annotations=[]
        self.annotations.append(Annotation.objects.create(document=self.doc1,annotator=self.annotator1,annotation_type=self.annotationType, begin_index=0,end_index=10))
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator1,annotation_type=self.annotationType, begin_index=1,end_index=5))
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator2,annotation_type=self.annotationType, begin_index=1,end_index=5))

    def tearDown(self):
        self.annotator1.documents.clear()
        self.annotator2.documents.clear()
        Annotator.objects.all().delete()
        Document.objects.all().delete()
        AnnotationType.objects.all().delete()
        Annotation.objects.all().delete()

    def testGetAnnotations(self):
        r1,r2=iaa._getAnnotations(self.annotator1,self.annotator2,self.doc1)
        self.assert_(not r2)
        self.assertEquals(r1[0].end_index, 10)
        r1,r2 =iaa._getAnnotations(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r1[0].annotator.id,100)
        self.assertEquals(r2[0].annotator.id,101)

    def testMatchExactSpan(self):
        r=iaa.matchExactSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r.hits,1)
        self.assertEquals(r.misses1,0)
        self.assertEquals(r.misses2,0)
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator1,annotation_type=self.annotationType, begin_index=2,end_index=5))
        r=iaa.matchExactSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r.hits,1)
        self.assertEquals(r.misses1,1)
        self.assertEquals(r.misses2,0)
        doc=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title2")
        r=iaa.matchExactSpan(self.annotator1,self.annotator2,doc)
        self.assertEquals(r.hits,0)
        self.assertEquals(r.misses1,0)
        self.assertEquals(r.misses2,0)

    def testOverlap(self):
        self.assert_(iaa._overlap((1,2),(1,2)))
        self.assert_(iaa._overlap((1,5),(2,4)))
        self.assert_(iaa._overlap((1,5),(2,8)))
        self.assert_(iaa._overlap((2,4),(1,8)))
        self.assert_(not iaa._overlap((2,4),(4,6)))
        self.assert_(not iaa._overlap((2,4),(0,1)))

    def testMatchOverlapSpan(self):
        r=iaa.matchOverlapSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r.hits,1)
        self.assertEquals(r.misses1,0)
        self.assertEquals(r.misses2,0)
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator1,annotation_type=self.annotationType, begin_index=2,end_index=5))
        r=iaa.matchOverlapSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r.hits,2)
        self.assertEquals(r.misses1,0)
        self.assertEquals(r.misses2,0)
        doc=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title2")
        r=iaa.matchOverlapSpan(self.annotator1,self.annotator2,doc)
        self.assertEquals(r.hits,0)
        self.assertEquals(r.misses1,0)
        self.assertEquals(r.misses2,0)

    def testmatchClassOverlapSpan(self):
        at=AnnotationType.objects.create(type="new",project=self.project)
        r=iaa.matchClassOverlapSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r[self.annotationType.type].hits,1)
        self.assertEquals(r[self.annotationType.type].misses1,0)
        self.assertEquals(r[self.annotationType.type].misses2,0)
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator1,annotation_type=self.annotationType, begin_index=2,end_index=5))
        r=iaa.matchClassOverlapSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r[self.annotationType.type].hits,2)
        self.assertEquals(r[self.annotationType.type].misses1,0)
        self.assertEquals(r[self.annotationType.type].misses2,0)
        doc=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title2")
        r=iaa.matchClassOverlapSpan(self.annotator1,self.annotator2,doc)
        self.assertEquals(r[self.annotationType.type].hits,0)
        self.assertEquals(r[self.annotationType.type].misses1,0)
        self.assertEquals(r[self.annotationType.type].misses2,0)
        self.annotations.append(Annotation.objects.create(document=self.doc2,annotator=self.annotator1,annotation_type=at, begin_index=2,end_index=3))
        r=iaa.matchClassOverlapSpan(self.annotator1,self.annotator2,self.doc2)
        self.assertEquals(r[self.annotationType.type].hits,2)
        self.assertEquals(r[self.annotationType.type].misses1,0)
        self.assertEquals(r[self.annotationType.type].misses2,0)
        self.assertEquals(r[at.type].hits,0)
        self.assertEquals(r[at.type].misses1,1)
        self.assertEquals(r[at.type].misses2,0)

    def testStats(self):
        stats=iaa.Stats(1,1,1)
        stats+iaa.Stats(1,2,3)
        self.assertEquals(stats.hits,2)
        self.assertEquals(stats.misses1,3)
        self.assertEquals(stats.misses2,4)
        stats.hits=	298
        stats.misses1=770
        stats.misses2=920
        self.assertEquals(stats.precision(), 24.47)
        self.assertEquals(stats.recall(),27.90)
        self.assertEquals(stats.fscore(),26.07)
        self.assertEquals(stats.matches(),596.0)
        self.assertEquals(stats.nonMatches(),1690.0)
        self.assertEquals(stats.iaaPercent(), 26.07)
        
    def testIaa(self):
        iaaStats=iaa.iaa(self.annotator1,self.annotator2,self.project)
        self.assertEquals(len(iaaStats.docStats),2)
        self.assertEquals(iaaStats.exactSpan.hits,1)
        self.assertEquals(iaaStats.exactSpan.misses1,1)
        self.assertEquals(iaaStats.exactSpan.misses2,0)
        self.assertEquals(iaaStats.overlapSpan.hits,1)
        self.assertEquals(iaaStats.overlapSpan.misses1,1)
        self.assertEquals(iaaStats.overlapSpan.misses2,0)
        self.assertEquals(iaaStats.classExactSpan[self.annotationType.type].hits,1)
        self.assertEquals(iaaStats.classExactSpan[self.annotationType.type].misses1,1)
        self.assertEquals(iaaStats.classExactSpan[self.annotationType.type].misses2,0)
        self.assertEquals(iaaStats.classOverlapSpan[self.annotationType.type].hits,1)
        self.assertEquals(iaaStats.classOverlapSpan[self.annotationType.type].misses1,1)
        self.assertEquals(iaaStats.classOverlapSpan[self.annotationType.type].misses2,0)
        for doc in iaaStats.docStats:
            if doc.doc.title=="title1":
                self.assertEquals(doc.exactSpan.hits,0)
                self.assertEquals(doc.exactSpan.misses1,1)
                self.assertEquals(doc.exactSpan.misses2,0)
                self.assertEquals(doc.overlapSpan.hits,0)
                self.assertEquals(doc.overlapSpan.misses1,1)
                self.assertEquals(doc.overlapSpan.misses2,0)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].hits,0)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].misses1,1)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].misses2,0)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].hits,0)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].misses1,1)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].misses2,0)
            elif doc.doc.title=="title2":
                self.assertEquals(doc.exactSpan.hits,1)
                self.assertEquals(doc.exactSpan.misses1,0)
                self.assertEquals(doc.exactSpan.misses2,0)
                self.assertEquals(doc.overlapSpan.hits,1)
                self.assertEquals(doc.overlapSpan.misses1,0)
                self.assertEquals(doc.overlapSpan.misses2,0)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].hits,1)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].misses1,0)
                self.assertEquals(doc.classExactSpan[self.annotationType.type].misses2,0)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].hits,1)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].misses1,0)
                self.assertEquals(doc.classOverlapSpan[self.annotationType.type].misses2,0)

class ViewsTestCase(unittest.TestCase):
    def setUp(self):
        self.annotator1 = Annotator.objects.create(username="100")
        self.annotator1.set_password('test')
        self.annotator2 = Annotator.objects.create(username="101")
        self.annotator2.set_password('test')
        self.admin = User.objects.create(username="admin")
        self.admin.is_staff = True
        self.admin.is_superuser = True
        self.admin.set_password('test')
        self.admin.save()
        self.luser1 = User.objects.create(username="102")
        self.luser1.set_password('test')
        self.luser1.save()
        self.project=Project.objects.create()
        self.doc1=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title1")
        self.doc2=Document.objects.create(create_date=datetime.datetime.now(),text="01234567891023456789",project=self.project,title="title2")
        self.submitted_doc=Document.objects.create(create_date=datetime.datetime.now(), text="01234567891023456789",project=self.project,title="a submitted document")
        self.doc1.save()
        self.doc2.save()
        self.submitted_doc.save()
        self.annotator1.documents.add(self.doc1)
        self.annotator1.documents.add(self.doc2)
        self.annotator2.documents.add(self.submitted_doc)
        self.annotator2.save()
        self.annotator1.save()
        #self.annotation_types = []
        #for i in range(5):
            #self.annotation_types.append(AnnotationType('name', 'desc', 'color',

        #self.annotator2.save()

        self.cat1 = AnnotationType(**{'color': u'666666', 'project_id': 1L, 'type': u'disease', 'id': 1L, 'description': u'disease'})
        self.cat2 = AnnotationType(**{'color': u'FF0000', 'project_id': 1L, 'type': u'body_part', 'id': 2L, 'description': u'Body part'})
        self.cat3 = AnnotationType(**{'color': u'0000A0', 'project_id': 1L, 'type': u'imaging_procedure', 'id': 3L, 'description': u'Imaging Procedure'})
        self.cat4 = AnnotationType(**{'color': u'800080', 'project_id': 1L, 'type': u'imaging_observation', 'id': 4L, 'description': u'Imaging Observation'})
        self.cat5 = AnnotationType(**{'color': u'347C17', 'project_id': 1L, 'type': u'imaging_observation_characteristic', 'id': 5L, 'description': u'Imaging Observation Characteristic'})
        self.cat1.save()
        self.cat2.save()
        self.cat3.save()
        self.cat4.save()
        self.cat5.save()

        self.client=Client()

    def tearDown(self):
        Annotator.objects.all().delete()
        Document.objects.all().delete()
        Project.objects.all().delete()
        AnnotationType.objects.all().delete()
        User.objects.all().delete()

    def testIaaStats(self):
        self.client.login(username='admin', password='test')
        response = self.client.post(reverse('dj.views.iaaStats'), {'project_id': self.project.id})
        self.assertEquals(response.status_code, 200)

        response = self.client.post(reverse('dj.views.iaaStats', args=[self.annotator1.id, self.annotator2.id, self.project.id]), {'project_id': self.project.id, 'annotator1': self.annotator1.id, 'annotator2': self.annotator2.id})
        self.assertEquals(response.status_code, 200)

    def testDocCompare(self):
        self.client.login(username='admin', password='test')
        response = self.client.post(reverse('dj.views.docCompare', args=[self.doc1.id, self.annotator1.id, self.annotator2.id]))
        self.assertEquals(response.status_code, 200)

    def testProjectList(self):
        self.client.login(username='admin', password='test')
        
        # access project list
        response = self.client.get(reverse('dj.views.projectList'))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(True, lists_are_similar(response.context[0]['project_list'], Project.objects.all()))

        # test project delete with a project that has annotators&documents onboard
        response = self.client.post(reverse('dj.views.projectDelete'), {'project_ids' : [self.project.id]})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(True, lists_are_similar(response.context[0]['project_list'], Project.objects.all()))

        # delete annotators/documents & try again
        self.project.annotators.clear()
        Document.objects.all().delete()
        response = self.client.post(reverse('dj.views.projectDelete'), {'project_ids' : [self.project.id]})
        self.assertEquals(True, lists_are_similar(Project.objects.all(), []))
        self.client.logout()

        # access project list as normal user
        self.client.login(username='100', password='test')
        response = self.client.get(reverse('dj.views.projectList'))
        self.assertEquals(response.status_code, 403)
        self.client.logout()

    def testProjectSave(self):
        self.client.login(username='admin', password='test')
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : self.project.id})
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : ''})
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : self.project.id, 'projectAnnotator_%s' % (self.annotator1.id) : ''})
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : self.project.id, 'projectAnnotator_%s' % (self.annotator1.id) : '', 'annotator_%s_%s' % (self.doc1.id, self.annotator1.id) : ''})
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : self.project.id, 'projectAnnotator_%s' % (self.annotator1.id) : '', 'del_%s' % (self.doc1.id) : ''})
        self.client.logout()

        self.client.login(username='100', password='test')
        self.client.post(reverse('dj.views.projectSave'), {'project_title' : 'asdf', 'project_id' : self.project.id})
        self.client.logout()

    def testEditAnnotator(self):
        self.client.login(username='admin', password='test')
        self.client.post(reverse('dj.views.editAnnotator', args=[self.annotator1.id]), {'annotator_id' : self.annotator1.id})
        #self.client.post(reverse('dj.views.editAnnotator'), {'annotator_id' : self.annotator1.id, 'password' : 'test', 'username' : self.annotator1.username, 'date_joined' : '2009-09-01 10:11:51', 'email' : '', 'first_name' : '', 'is_active' : 'on', 'last_login' : '2009-09-01 10:11:51', 'last_name' : '', 'initial-date_joined' : '2009-09-01 10:11:51.977220', 'initial-date_login' : '2009-09-01 10:11:51.976788'})
        self.client.post(reverse('dj.views.editAnnotator', args=[self.annotator1.id]), {'annotator_id' : self.annotator1.id, 'password' : self.annotator1.password, 'username' : self.annotator1.username, 'date_joined' : '2009-09-01 10:11:51', 'email' : '', 'first_name' : '', 'is_active' : 'on', 'last_login' : '2009-09-01 10:11:51', 'last_name' : '', 'initial-date_joined' : '2009-09-01 10:11:51.977220', 'initial-date_login' : '2009-09-01 10:11:51.976788'})
        self.client.post(reverse('dj.views.editAnnotator', args=[self.annotator1.id]), {'password' : 'test'})

        self.client.get(reverse('dj.views.editAnnotator'))
        self.client.get(reverse('dj.views.editAnnotator', args=[self.annotator1.id]))
        self.client.logout()

    def testProjectEdit(self):
        self.client.login(username='admin', password='test')

        # access a specific project
        response = self.client.get(reverse('dj.views.projectEdit', args=[self.project.id]))
        self.assertEquals(True, lists_are_similar(response.context[0]['document_list'], Document.objects.filter(project=self.project)))
        self.assertEquals(True, lists_are_similar(response.context[0]['user_list'], self.project.annotators.all()))
        self.assertEquals(response.status_code, 200)

        # access a specific project
        response = self.client.get(reverse('dj.views.projectEdit', args=[self.project.id]))
        self.assertEquals(response.status_code, 200)

        ####### Annotation type code
        # create a new annotation type
        numAnnotations = len(AnnotationType.objects.all())
        response = self.client.post(reverse('dj.views.saveAnnotationType', args=[self.project.id]), {'color' : '#000000', 'title' : 'asdf', 'desc' : 'asdf'})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(numAnnotations+1, len(AnnotationType.objects.all()))
        response = self.client.post(reverse('dj.views.saveAnnotationType', args=[self.project.id]), {'color' : '#000000', 'title' : 'asdf', 'desc' : ''}) # without required description
      
    def testStart(self):
        # test an annotator accessing start page
        self.client.login(username='100', password='test')
        response = self.client.get(reverse('dj.views.start'))
        self.assertEquals(response.status_code,200)
        doc_list = response.context[0]['doc_list']
        doc_list2 = self.annotator1.documents.all()
        #doc_list2 = Document.objects.all(annotator=self.annotator1)
        self.assertEquals(True, lists_are_similar(doc_list, doc_list2))
        self.client.logout()

        # test a user who's not an annotator accessing index
        self.client.login(username='102', password='test')
        response = self.client.get(reverse('dj.views.start'))
        self.assertEquals(response.status_code, 200) 
        self.client.logout()

        # test an admin accessing start page
        self.client.login(username='admin', password='test')
        response = self.client.get(reverse('dj.views.start'))
        self.assertEquals(response.status_code,200)
        proj_list = response.context[0]['project_list']
        proj_list2 = Project.objects.all()
        self.assertEquals(True, lists_are_similar(proj_list, proj_list2))
        self.client.logout()

    def testUploadFile(self):
        self.client.login(username='admin', password='test')

        response = self.client.post(reverse('dj.views.upload_file', args=[self.project.id]))
        self.assertEquals(200, response.status_code)

        # upload a text document
        f = open('dj/tests/dada.txt', 'r')
        response = self.client.post(reverse('dj.views.upload_file', args=[self.project.id]), {'fileToUpload' : f})
        self.assertEquals(200, response.status_code)
        self.assertEquals(len(Document.objects.filter(project=self.project, title=os.path.split(f.name)[1])), 1)
        f.close()

        Document.objects.all().delete()

        # upload a zip document
        f = open('dj/tests/dada.zip', 'r')
        zipdata = f.read()
        zip = zipfile.ZipFile(StringIO.StringIO(zipdata))
        f.close()
        f = open('dj/tests/dada.zip', 'r')
        response = self.client.post(reverse('dj.views.upload_file', args=[self.project.id]), {'fileToUpload' : f})
        for file in zip.namelist(): # ensure every file from the zip was created
            self.assertEquals(len(Document.objects.filter(project=self.project, title=file)), 1)
        f.close()

        # upload a bad document
        f = open('dj/tests/dada.bad', 'r')
        response = self.client.post(reverse('dj.views.upload_file', args=[self.project.id]), {'fileToUpload' : f})
        self.assertEquals(200, response.status_code)
        f.close()

        self.client.logout()

        # test a normal user trying to access file upload form
        f = open('dj/tests/dada.bad', 'r')
        self.client.login(username='100', password='test')
        response = self.client.post(reverse('dj.views.upload_file', args=[self.project.id]), {'fileToUpload' : f})
        f.close()
        self.assertEquals(response.status_code, 403)
        self.client.logout()

    def testDoc(self):
        # annotator accessing a document owned by them
        self.client.login(username='100', password='test')
        response = self.client.get(self.doc1.get_absolute_url())
        self.assertEquals(response.status_code,200)
        self.assertEquals(response.context[0]['doc'].text, self.doc1.text)
        self.client.logout()

        # test a superuser accessing a document with a specific annotator ID
        self.client.login(username='admin', password='test')
        response = self.client.get(self.doc1.get_absolute_url(annotator_id=self.annotator1.id))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context[0]['doc'].text, self.doc1.text)

        self.client.logout()

    def testAnnotator(self):
        self.client.login(username='100', password='test')
        createAnnotation = lambda begin,end,category_id,document_id : self.client.post(reverse('dj.views.newAnnotation'), { 'newNecCategoryId' : category_id, 'document_id' : document_id, 'newNec' : Document.objects.get(id=document_id).text[begin:end]})
        deleteAnnotation = lambda begin,end,document_id : createAnnotation(begin, end, 'Delete', document_id)

        # try creating and  deleting some annotations as a normal user
        createAnnotation(1, 2, self.cat1.id, self.doc1.id)
        createAnnotation(1, 2, self.cat2.id, self.doc1.id)
        createAnnotation(0, 4, self.cat3.id, self.doc1.id)
        createAnnotation(3, 4, self.cat1.id, self.doc1.id)
        createAnnotation(0, 1, self.cat1.id, self.doc1.id)
        createAnnotation(0, 7, self.cat3.id, self.doc1.id)
        createAnnotation(2, 5, self.cat1.id, self.doc1.id)
        createAnnotation(4, 6, self.cat2.id, self.doc1.id)
        createAnnotation(0, 3, self.cat2.id, self.doc1.id)

        response = self.client.get(self.doc1.get_absolute_url())
        self.assertEquals(response.status_code,200)
       
        self.assertEquals(response.context[0]['doc'].text, '<a class="category2" id="annotation_38">012</a>3<a class="category2" id="annotation_36">45</a>6789<a class="category1" id="annotation_27">1</a><a class="category1" id="annotation_32">0</a>23<a class="category2" id="annotation_37">45</a>6789')
        createAnnotation(0, 3, self.cat2.id, self.doc1.id)
        createAnnotation(1, 5, self.cat1.id, self.doc1.id)
        createAnnotation(1, 5, self.cat1.id, self.doc1.id)

        createAnnotation(0, 0, self.cat1.id, self.doc1.id) # empty annotation test

        response = self.client.get(self.doc1.get_absolute_url())
        self.assertEquals(response.context[0]['doc'].text, '0<a class="category1" id="annotation_39">1234</a>56789<a class="category1" id="annotation_27">1</a><a class="category1" id="annotation_32">0</a>23<a class="category2" id="annotation_37">45</a>6789')
        self.client.logout()

        
