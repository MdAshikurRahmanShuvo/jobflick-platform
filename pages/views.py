from types import SimpleNamespace

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.db.models import Prefetch
from django.shortcuts import redirect, render
from django.urls import reverse

from jobs.models import Job, JobApplication
from userprofile.models import UserProfile

TOP_CITY_NAMES = ["Uttara", "Mirpur", "Banani", "Dhanmondi", "Gulshan", "Motijheel"]

def _page_context(request):
    embed_mode = request.GET.get("embed") == "1"
    return {"hide_nav": embed_mode, "hide_footer": embed_mode}


def home(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('user-dashboard')
    base_jobs = Job.objects.filter(status=Job.Status.APPROVED).select_related("poster").order_by("-created_at")
    location_filter = request.GET.get("location", "").strip()
    profile = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        jobs = base_jobs.prefetch_related(
            Prefetch(
                "applications",
                queryset=JobApplication.objects.filter(applicant=request.user),
                to_attr="app_for_user",
            )
        )
    else:
        jobs = base_jobs
    active_location = None
    if location_filter:
        jobs = jobs.filter(location__icontains=location_filter)
        active_location = location_filter
    apply_profile = profile or SimpleNamespace(has_active_subscription=False, wallet_balance=0)
    all_locations = [
        (loc or "").lower()
        for loc in Job.objects.filter(status=Job.Status.APPROVED).values_list("location", flat=True)
        if loc
    ]
    top_cities = [
        {
            "name": city,
            "has_jobs": any(city.lower() in location for location in all_locations),
        }
        for city in TOP_CITY_NAMES
    ]
    featured_jobs = base_jobs[:6]
    stats = {
        "total_users": get_user_model().objects.count(),
        "total_jobs": Job.objects.filter(status=Job.Status.APPROVED).count(),
        "total_applications": JobApplication.objects.count(),
        "total_completed": Job.objects.filter(status=Job.Status.APPROVED, is_filled=True).count(),
    }
    context = {
        "featured_jobs": featured_jobs,
        "job_cards": jobs,
        "profile": profile,
        "apply_profile": apply_profile,
        "apply_redirect_path": reverse('job_list'),
        "top_cities": top_cities,
        "active_location": active_location,
        **stats,
    }
    return render(request, 'pages/home.html', context)


def about(request):
    return render(request, 'pages/about.html', _page_context(request))


def contact(request):
    context = _page_context(request)
    context["contact_status"] = None
    context["form_data"] = {
        "user_name": "",
        "user_email": "",
        "message": "",
    }

    if request.method == "POST":
        name = request.POST.get("user_name", "").strip()
        email = request.POST.get("user_email", "").strip()
        body = request.POST.get("message", "").strip()

        context["form_data"] = {
            "user_name": name,
            "user_email": email,
            "message": body,
        }

        if not (name and email and body):
            context["contact_status"] = {
                "level": "error",
                "message": "Please fill in your name, email, and message so we can reach back."
            }
        else:
            recipient = getattr(settings, "JOBFLICK_CONTACT_EMAIL", "jobflick0@gmail.com")
            subject = f"Jobflick Contact • Message from {name}"
            email_body = (
                "Hello Jobflick Crew,\n\n"
                "You have a fresh note from the Jobflick contact page.\n\n"
                f"Name  : {name}\n"
                f"Email : {email}\n"
                "Message:\n"
                f"{body}\n\n"
                "— Sent automatically by the Jobflick website concierge"
            )

            sender = getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@jobflick.com")

            mail = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=sender,
                to=[recipient],
                reply_to=[email],
            )

            try:
                mail.send(fail_silently=False)
            except Exception:
                context["contact_status"] = {
                    "level": "error",
                    "message": "We couldn't deliver your note just now. Please try again in a moment."
                }
            else:
                context["contact_status"] = {
                    "level": "success",
                    "message": "Thanks! Your message is en route to the Jobflick inbox. We'll reply soon."
                }
                context["form_data"] = {"user_name": "", "user_email": "", "message": ""}

    return render(request, 'pages/contact.html', context)


def privacy_policy(request):
    return render(request, 'pages/privacy.html', _page_context(request))


def terms_and_conditions(request):
    return render(request, 'pages/terms.html', _page_context(request))


def faqs(request):
    return render(request, 'pages/faqs.html', _page_context(request))


def help_center(request):
    return render(request, 'pages/help_center.html', _page_context(request))