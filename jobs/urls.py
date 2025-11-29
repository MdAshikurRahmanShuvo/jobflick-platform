
from django.urls import path

from . import views

urlpatterns = [
	path('post-job/', views.post_job, name="post_job"),
	path('jobs/', views.job_list, name="job_list"),
	path('jobs/<int:job_id>/apply/', views.apply_to_job, name="apply_to_job"),
	path('applications/', views.manage_applications, name="manage_job_applications"),
	path('applications/<int:pk>/status/', views.update_application_status, name="update_application_status"),
]
