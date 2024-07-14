# users/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('profile')
    else:
        form = AuthenticationForm()
    return render(request, 'user_login.html', {'form': form})

def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'user_register.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'profile.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')


from books.models import Borrow  # Ensure this import is correct based on your project structure

def profile(request):
    user = request.user
    borrowed_books = Borrow.objects.filter(user=user).select_related('book')  # Fetch borrowed books with related book details

    context = {
        'user': user,
        'borrowed_books': borrowed_books,
    }
    return render(request, 'profile.html', context)