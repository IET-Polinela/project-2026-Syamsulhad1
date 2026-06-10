from django.shortcuts import render
def about_city(request):
    return render(request, 'about/about.html')