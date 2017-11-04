from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import login
from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^items/$', views.items, name='items'),
    url(r'^additems/$', views.additems, name='additems'),
    url(r'^edititems/$', views.edititems, name='edititems'),
    url(r'^delitems/$', views.delitems, name='delitems'),
    url(r'^addtocart/$', views.addtocart, name='addtocart'),
    url(r'^checkout/$', views.checkout, name='checkout'),
    url(r'^remove/$', views.remove, name='remove'),
    url(r'^place/$', views.place, name='place'),
    url(r'^order/$', views.order, name='order'),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^pending/$', views.pending, name='pending'),
    url(r'^allorder/$', views.allorder, name='allorder'),
    url(r'^changestatus/$', views.changestatus, name='changestatus'),
    url(r'^deleteorder/$', views.deleteorder, name='deleteorder'),
    url(r'^editdetails/$', views.editdetails, name='editdetails'),
    url(r'^prevorder/$', views.prevorder, name='prevorder'),
    url(r'^offers/$', views.offers, name='offers'),
    url(r'^test/$', views.test, name='test'),  
]