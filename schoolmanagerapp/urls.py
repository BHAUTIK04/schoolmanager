from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$',views.index_view, name='index'),
    url(r'login/$',views.loggin, name='login'),
    url(r'createuser/$',views.CreateUser, name='createuser'),
    url(r'dashboard/$',views.dashboard, name='dashboard'),
    url(r'logout/$',views.loggout, name='logout'),
    url(r'classlist/$',views.classList, name='classlist'),
    url(r'studentlist/$',views.studentList, name='studentlist'),
    url(r'listallstudents/$',views.allStudentList, name='studentlist'),
    url(r'listallteachers/$',views.teacherList, name='teacherlist'),
    url(r'listallschools/$',views.allSchoolList, name='teacherlist'),
    url(r'profile/$',views.profile, name='teacherlist'),
]