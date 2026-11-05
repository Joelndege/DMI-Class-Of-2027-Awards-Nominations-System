from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile

def email_verification_sent_view(request):
    return render(request, 'accounts/email_verification_sent.html')

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        programme = request.POST.get('programme', '').strip()
        profile.programme = programme
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('nominate_wizard')
    return render(request, 'accounts/profile.html', {'profile': profile})

