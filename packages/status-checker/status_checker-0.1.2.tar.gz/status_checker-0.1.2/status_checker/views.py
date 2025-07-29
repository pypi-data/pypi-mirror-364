from django.shortcuts import render
import requests
import time
from .forms import URLForm

def check_site_status(url):
    try:
        start = time.time()
        response = requests.get(url, timeout=5)
        duration = round((time.time() - start) * 1000)  # ms
        return {
            "status_code": response.status_code,
            "response_time": duration,
            "online": response.status_code == 200
        }
    except requests.exceptions.RequestException:
        return {
            "status_code": None,
            "response_time": None,
            "online": False
        }

def index(request):
    result = None
    form = URLForm(request.POST or None)
    if form.is_valid():
        url = form.cleaned_data["url"]
        result = check_site_status(url)
        result["url"] = url
    return render(request, "site_status_checker/index.html", {"form": form, "result": result})
