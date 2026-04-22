from django.shortcuts import render


def dashboard_view(request):
    context = {
        "page_title": "Pokeparty",
    }
    return render(request, "roster/dashboard.html", context)