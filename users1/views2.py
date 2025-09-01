from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.conf import settings

from users.forms import ProfileUpdateForm, UserUpdateForm, UserRegisterForm

def login(request):
    next = request.POST.get('next', request.GET.get('next', ''))
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect('/home')
            else:
                return HttpResponse('Inactive user')
        else:
            return HttpResponseRedirect(settings.LOGIN_URL)
    return render(request, 'users/login.html')
    # return render(request, "login.html")

def logout(request):
    auth.logout(request)
    # Redirect back to login page
    return HttpResponseRedirect(settings.LOGIN_URL)


@login_required
def home(request):
    return render(request, "home.html")


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Ваш аккаунт создан: можно войти на сайт.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        # profile = Profile.objects.get(user = request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                #    instance=profile)
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Ваш профиль успешно обновлен.')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)      
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }

    return render(request, 'users/profile.html', context)