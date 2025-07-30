from django.shortcuts import render

def show_page(request):
    return render(request, "web_show/show.html")