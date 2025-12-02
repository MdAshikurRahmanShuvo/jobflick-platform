from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from jobs.models import Job, JobApplication


def _page_context(request):
    embed_mode = request.GET.get("embed") == "1"
    return {"hide_nav": embed_mode, "hide_footer": embed_mode}


def home(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('user-dashboard')
    jobs = Job.objects.filter(status=Job.Status.APPROVED).select_related("poster")[:6]
    stats = {
        "total_users": get_user_model().objects.count(),
        "total_jobs": Job.objects.filter(status=Job.Status.APPROVED).count(),
        "total_applications": JobApplication.objects.count(),
    }
    context = {"featured_jobs": jobs, **stats}
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