from django.shortcuts import redirect, render

from jobs.models import Job


def _page_context(request):
    embed_mode = request.GET.get("embed") == "1"
    return {"hide_nav": embed_mode, "hide_footer": embed_mode}


def home(request):
    if request.user.is_authenticated and not request.user.is_staff:
        return redirect('user-dashboard')
    jobs = Job.objects.select_related("poster")[:6]
    return render(request, 'pages/home.html', {"featured_jobs": jobs})


def about(request):
    return render(request, 'pages/about.html', _page_context(request))


def contact(request):
    return render(request, 'pages/contact.html', _page_context(request))