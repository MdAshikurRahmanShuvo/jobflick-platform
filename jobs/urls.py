
from django.urls import path

from . import views

urlpatterns = [
	path('post-job/', views.post_job, name="post_job"),
	path('jobs/', views.job_list, name="job_list"),
]
