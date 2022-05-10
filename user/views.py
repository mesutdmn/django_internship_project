from django.shortcuts import render,redirect
from .forms import LoginForm
from article.models import Article
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required

# Create your views here.

def loginUser(request):
    keyword = request.GET.get("keyword")
    if keyword:
        etkinlikler = Article.objects.filter(title__icontains=keyword)
        return render(request,"index.html",{"etkinlikler" : etkinlikler})

    form = LoginForm(request.POST or None)

    context = {
        "form":form
    }
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        user=authenticate(username=username,password=password)

        if user is None:
            messages.info(request,"Kullanıcı Adı veya Parola Hatalı")
            return render (request,"login.html",context)
        
        messages.success(request,"Giriş Yapıldı")
        login(request,user)
        return redirect("index")
    return render(request,"login.html",context)

@login_required(login_url = "user:login")
def logoutUser(request):
    logout(request)
    messages.success(request,"Çıkış Yapıldı")
    return redirect("index")