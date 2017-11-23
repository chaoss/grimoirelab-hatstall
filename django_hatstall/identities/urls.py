from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='identities index'),
    url(r'^list$', views.list, name='identities list'),
    url(r'^(?P<identity_id>[0-9]+)/$', views.identity, name='show identity'),
]
