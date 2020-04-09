from django.shortcuts import redirect, render
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.http import HttpResponse, request
from django.contrib.auth import logout,login
from django.http.response import HttpResponseRedirect
from account.views import my_random_string
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token

User = get_user_model()

def home(request):
    return render(request, 'index.html')

def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            login(request,user)
            return redirect('dash')
        else:
            messages.info(request, 'Invalid crenditals')
            return redirect('signin')

    else:
        return render(request, 'signin.html')

def signout(request):
    if request.method == "POST":
        request.user.is_active = False
        logout(request)
        return HttpResponseRedirect("/")


def register(request):
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        email = request.POST['email']
        location = request.POST['location']
        phone = request.POST['phone']
        uid = my_random_string(10)
        if User.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists.')
            return redirect('register')
        elif User.objects.filter(email=email).exists():
            messages.warning(request, "Email already exists.")
            return redirect('register')
        else:
            user = User.objects.create_user(user_id=uid,username=username, first_name=first_name, last_name=last_name,
                                                email=email, password=password1, location=location, phone=phone)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your SECRY account.'
            template = get_template('acc_active_email.txt')
            context = {'user': user,'domain': current_site.domain,'uid': urlsafe_base64_encode(force_bytes(uid)),'token': account_activation_token.make_token(user)}
            text_content = template.render(context)
            email = EmailMessage(mail_subject, text_content, 'admin@secrycloud.tech', [email])
            email.send(fail_silently=False)
            messages.info(request, 'Please confirm your email address to complete the registration')
            return render(request, 'response.html')
            
    else:
        return render(request, 'signup.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(user_id=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
        return render(request, 'response.html')
    else:
        messages.warning(request, 'Activation link is invalid!')
        return render(request, 'response.html')


def change(request):
    if(request.method == "POST"):
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        emailid = request.POST['email']
        if not User.objects.filter(email=emailid).exists():
            messages.info(request, "Email does not exists.")
            return render(request, 'signin.html')
        else:
            user = User.objects.get(email=emailid)
            user.set_password(password1)
            user.save()
            messages.success(request, "Your passsword has been changed.")
            return render(request, 'signin.html')


def contact(request):
    if request.method == 'POST':
        contact_name = request.POST['txtName']
        contact_email = request.POST['txtEmail']
        contact_phone = request.POST['txtPhone']
        form_content = request.POST['txtMsg']
        template = get_template('contact_template.txt')
        context = {'contact_name': contact_name,'contact_email': contact_email,'contact_phone':contact_phone,'form_content': form_content}
        content = template.render(context)
        email = EmailMessage("New contact form submission",content,contact_email,['admin@secrycloud.tech'],headers={'Reply-To': contact_email})
        email.send()
        return redirect('home')


def error_404(request,exception):
        data = {}
        return render(request, '404.html', data)


def error_500(request):
    return render(request, '500.html')

