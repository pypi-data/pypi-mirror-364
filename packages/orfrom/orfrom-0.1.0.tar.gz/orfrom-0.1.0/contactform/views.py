from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .forms import MessageForm

def contact_view(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'form.html', {
                'form': MessageForm(),
                'success': True
            })
    else:
        form = MessageForm()
    return render(request, 'form.html', {'form': form})
