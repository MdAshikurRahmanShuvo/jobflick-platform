from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from userprofile.models import UserProfile

from .forms import JobForm
from .models import Job


@login_required
@never_cache
def post_job(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect("user-dashboard")
    else:
        form = JobForm()
    return render(request, "jobs/post_job.html", {"form": form, "profile": profile, "hide_nav": True})


@login_required
@never_cache
def job_list(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    jobs = Job.objects.all()
    return render(request, "jobs/job_list.html", {"jobs": jobs, "profile": profile, "hide_nav": True})