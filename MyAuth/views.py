# coding:utf-8
from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Create your views here.


def login_account(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            if username is None and password is None:
                return render(request, 'MyAuth/login.html')
            else:
                return render(request, 'MyAuth/login.html', {'login_err': u'用户名或密码错误'})
    else:
        return render(request, 'MyAuth/login.html')


@login_required
def index(request):
    return render(request, 'MyAuth/index.html')


@login_required
def logout_account(request):
    logout(request)
    return HttpResponseRedirect('/')
