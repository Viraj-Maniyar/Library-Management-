# books/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Book, Borrow
from .forms import BookForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
import requests
from django.urls import reverse
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

def home(request):
    return render(request, 'home.html')

def google_login(request):
    google_redirect_uri = reverse('google_callback')  # URL name for the callback
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=email%20profile"
    )
    return redirect(google_auth_url)

def google_callback(request):
    code = request.GET.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_payload = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': settings.GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    }

    token_response = requests.post(token_url, data=token_payload)
    tokens = token_response.json()
    id_token_value = tokens.get('id_token')

    try:
        idinfo = id_token.verify_oauth2_token(id_token_value, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
        # Process user data from 'idinfo'
        email = idinfo.get('email')
        user, created = User.objects.get_or_create(email=email, defaults={
            'username': email,
            'password': User.objects.make_random_password(),  # Ensure a default password for new users
        })
        if created:
            user.set_unusable_password()
            user.save()
        login(request, user)  # Log in the user
        return redirect('/')  # Redirect to home page or wherever needed after successful login
    except ValueError:
        return redirect('/')  # Handle failed login

@login_required
def book_list(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(title__icontains=query)
    else:
        books = Book.objects.all()
    
    context = {
        'books': books,
        'query': query
    }
    
    return render(request, 'book_list.html', context)

@login_required
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'book_detail.html', {'book': book})

@login_required
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm()
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('book_list')
    else:
        form = BookForm(instance=book)
    return render(request, 'book_form.html', {'form': form})

@login_required
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'book_confirm_delete.html', {'book': book})

@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    if book.quantity > 0:
        due_date = timezone.now() + timedelta(days=14)
        
        Borrow.objects.create(
            user=request.user,
            book=book,
            due_date=due_date
        )
        
        book.quantity -= 1
        book.save()
        
        return redirect('book_list')
    else:
        return HttpResponse("No available copies to borrow.", status=400)
