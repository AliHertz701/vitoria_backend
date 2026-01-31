from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Product, Inquiry, Message, Branch
from .forms import InquiryForm, ContactForm, ProductForm, BranchForm

def home(request):
    return render(request, 'main/home.html')

def about(request):
    return render(request, 'main/about.html')

def products(request):
    products = Product.objects.all()
    return render(request, 'main/products.html', {'products': products})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'main/contact.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'main/login.html')

def dashboard(request):
    products = Product.objects.all()
    inquiries = Inquiry.objects.all()
    messages = Message.objects.all()
    branches = Branch.objects.all()
    return render(request, 'main/dashboard.html', {
        'products': products,
        'inquiries': inquiries,
        'messages': messages,
        'branches': branches,
    })