
from django.urls import path,include
from . import views
urlpatterns = [
 path('post-job/',views.post_job,name="post_job"),
]
