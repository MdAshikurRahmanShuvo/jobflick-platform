from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import never_cache

from userprofile.models import UserProfile
from userprofile.utils import notify_staff

from .forms import JobForm
from .models import Job, JobApplication


@login_required
@never_cache
def post_job(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if not profile.has_active_subscription:
        messages.warning(request, "You need an active subscription to post jobs.")
        return redirect("userprofile-subscription")
    if request.method == "POST":
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.poster = request.user
            job.save()
            notify_staff(
                message=(
                    f"{request.user.username} submitted '{job.work_title}' (Tracking {job.tracking_code}) for approval."
                ),
                link=f"{reverse('adminpanel-dashboard')}?section=post-approvals",
            )
            messages.success(request, "Job submitted for review. We'll publish it once an admin approves.")
            return redirect("user-dashboard")
    else:
        form = JobForm()
    return render(
        request,
        "jobs/post_job.html",
        {"form": form, "profile": profile, "hide_nav": True, "hide_footer": True},
    )


@login_required
@never_cache
def job_list(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    location_filter = request.GET.get("location", "").strip()
    category_filter = request.GET.get("category", "").strip()
    jobs = (
        Job.objects.filter(status=Job.Status.APPROVED)
        .exclude(poster=request.user)
        .prefetch_related(
            Prefetch(
                "applications",
                queryset=JobApplication.objects.filter(applicant=request.user),
                to_attr="app_for_user",
            )
        )
    )
    active_location = None
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
        active_location = location_filter
    active_category = None
    if category_filter:
        jobs = jobs.filter(worker_type__icontains=category_filter)
        active_category = category_filter
    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "profile": profile,
            "hide_nav": True,
            "hide_footer": True,
            "active_location": active_location,
            "active_category": active_category,
        },
    )


@login_required
@never_cache
def apply_to_job(request, job_id):
    job = get_object_or_404(Job, pk=job_id, status=Job.Status.APPROVED)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    redirect_target = request.POST.get("redirect_to")
    if redirect_target and not redirect_target.startswith("/"):
        redirect_target = None
    if request.method != "POST":
        return redirect(redirect_target or "job_list")
    if job.is_filled:
        messages.info(request, "Hiring has already been completed for this job.")
        return redirect(redirect_target or "job_list")
    if not profile.has_active_subscription:
        messages.warning(request, "An active subscription is required to apply for jobs.")
        return redirect("userprofile-subscription")
    if job.poster_id == request.user.id:
        messages.error(request, "You cannot apply to a job you posted.")
        return redirect(redirect_target or "job_list")
    application, created = JobApplication.objects.get_or_create(
        job=job,
        applicant=request.user,
        defaults={"cover_letter": request.POST.get("cover_letter", "").strip()},
    )
    if not created:
        messages.info(request, "You already applied to this job.")
    else:
        messages.success(request, "Application submitted successfully.")
        notify_staff(
            message=(
                f"{request.user.username} applied for '{job.work_title}' (Tracking {job.tracking_code})."
            ),
            link=f"{reverse('adminpanel-dashboard')}?section=approvals",
        )
    return redirect(redirect_target or "job_list")


@staff_member_required
@never_cache
def manage_applications(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    applications = (
        JobApplication.objects.select_related("job", "applicant", "decided_by")
        .order_by("-created_at")
    )
    return render(
        request,
        "jobs/application_list.html",
        {"applications": applications, "profile": profile, "hide_nav": True},
    )


@staff_member_required
@never_cache
def update_application_status(request, pk):
    application = get_object_or_404(JobApplication, pk=pk)
    if request.method != "POST":
        return redirect("manage_job_applications")
    action = request.POST.get("action")
    if action not in {"approve", "reject"}:
        messages.error(request, "Invalid action.")
        return redirect("manage_job_applications")
    if action == "approve" and application.job.is_filled and application.status != JobApplication.Status.APPROVED:
        messages.error(request, "This job is already marked as hired.")
        return redirect("manage_job_applications")
    application.status = (
        JobApplication.Status.APPROVED if action == "approve" else JobApplication.Status.REJECTED
    )
    application.decided_by = request.user
    application.decision_at = timezone.now()
    application.save()
    if application.status == JobApplication.Status.APPROVED and not application.job.is_filled:
        application.job.is_filled = True
        application.job.filled_at = timezone.now()
        application.job.save(update_fields=["is_filled", "filled_at"])
    messages.success(request, f"Application marked as {application.get_status_display().lower()}.")
    return redirect("manage_job_applications")