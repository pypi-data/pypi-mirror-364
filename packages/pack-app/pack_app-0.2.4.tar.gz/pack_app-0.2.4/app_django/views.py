from django.http import HttpResponse

def home(request):
    return HttpResponse("Bienvenue dans votre application Django modulaire !")
