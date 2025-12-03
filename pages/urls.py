from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.home,name="home"),
    path('about/',views.about,name="about"),
    path('contact/',views.contact,name="contact"),
    path('privacy/', views.privacy_policy, name="privacy"),
    path('terms/', views.terms_and_conditions, name="terms"),
    path('faqs/', views.faqs, name="faqs"),
    path('help-center/', views.help_center, name="help-center"),
]