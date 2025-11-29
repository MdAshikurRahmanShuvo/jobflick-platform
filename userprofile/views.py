from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.views.decorators.cache import never_cache

from jobs.models import Job, JobApplication

from .forms import UserProfileForm
from .models import UserProfile


@login_required
@never_cache
def dashboard_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	skills = [skill.strip() for skill in profile.skills.split(",") if skill.strip()]
	jobs = Job.objects.prefetch_related(
		Prefetch(
			"applications",
			queryset=JobApplication.objects.filter(applicant=request.user),
			to_attr="app_for_user",
		)
	)
	context = {
		"profile": profile,
		"skills": skills,
		"jobs": jobs,
		"job_count": jobs.count(),
		"hide_nav": True,
	}
	return render(request, "userprofile/dashboard.html", context)


@login_required
@never_cache
def edit_profile_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	if request.method == "POST":
		form = UserProfileForm(request.POST, request.FILES, instance=profile)
		if form.is_valid():
			form.save()
			messages.success(request, "Profile updated successfully.")
			return redirect("user-dashboard")
	else:
		form = UserProfileForm(instance=profile)

	return render(request, "userprofile/edit_profile.html", {"form": form, "profile": profile, "hide_nav": True})


@login_required
@never_cache
def chat_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/chat_placeholder.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def activity_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/activity_placeholder.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def help_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/help_placeholder.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def dashboard_about_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/about_panel.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def dashboard_contact_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/contact_panel.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def transactions_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	return render(request, "userprofile/transactions_placeholder.html", {"profile": profile, "hide_nav": True})


@login_required
@never_cache
def notifications_view(request):
	profile, _ = UserProfile.objects.get_or_create(user=request.user)
	notifications = request.user.notifications.all()
	request.user.notifications.filter(is_read=False).update(is_read=True)
	return render(
		request,
		"userprofile/notifications.html",
		{"profile": profile, "hide_nav": True, "notifications": notifications},
	)

# Create your views here.
