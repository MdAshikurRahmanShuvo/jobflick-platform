from django.shortcuts import render


def _page_context(request):
    return {"hide_nav": request.GET.get("embed") == "1"}


def home(request):
    return render(request, 'pages/home.html')


def about(request):
    return render(request, 'pages/about.html', _page_context(request))


def contact(request):
    return render(request, 'pages/contact.html', _page_context(request))