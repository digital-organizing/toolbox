from django.shortcuts import redirect, render


# Create your views here.
async def index(request):
    return redirect('https://digitalorganizing.ch/')
