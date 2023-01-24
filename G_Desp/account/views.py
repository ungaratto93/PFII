
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import MagicKey
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.core.mail import BadHeaderError, send_mail

# Create your views here.
@login_required(login_url='/account/login')
def user_details(request):
    user = None
    try:
        user = User.objects.\
        filter(
            username=request.user.username
        )[0]
    except Exception as exc:
        messages.error(request, "An error was occurred" + str(exc))
        redirect(request, '/cashflow/home')
    return render(
        request,
        'account/user_details.html',
        {
            'user': user,
        }
    )


def sign_in(request):
    try:

        if request.POST:
            username = request.POST['username']
            password = request.POST['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                redirect('/cashflow/home')
            else:
                messages.error(
                    request,
                    'Verify your credentials'
                )
                redirect('/account/sign_in')

    except Exception as exc:
        messages.error(
            request,
            "An error was occured!" + str(exc)
        )
    return render(
        request,
        'account/login.html',
        {}
    )


def sign_up(request):
    try:

        if request.POST:
            username = request.POST['username']
            username_exists = User.objects.\
                filter(
                    username__iexact=username
                )

            if username_exists:
                messages.error(
                    request,
                    "Username unavaible!"
                )
                redirect('/account/sign_up')
            else:

                try:
                    first_name = request.POST['nome']
                    last_name = request.POST['sobrenome']
                    username = request.POST['username']
                    email = request.POST['email']
                    password = request.POST['password']
                    cpassword = request.POST['cpassword']

                    if str(password) == str(cpassword):
                        user = User.objects.create_user(
                            username,
                            email,
                            password,
                            first_name=first_name,
                            last_name=last_name
                        )
                        user.save()
                        messages.success(
                            request,
                            "User was created!"
                        )
                        return redirect(
                            settings.LOGIN_URL,
                            request.path
                        )
                    else:
                        messages.error(
                            request,
                            "Wrong confirm password!"
                        )
                        redirect('/account/sign_up')
                except Exception as exc:
                    messages.error(request, "User was not created, because an error was occured!" + str(exc))

    except Exception as exc:
        messages.error(request, "An error was occured!" + str(exc))
    return render(request, "account/user_create.html")


def sign_out(request):
    try:
        logout(request)
        return render(request, 'account/logout.html')
    except Exception as e:
        raise e
    return HttpResponse('An error was occured on the logout proccess!')


def reset_password(request, key):
    """Verify if the password is correct and change it"""

    resposta = ''
    valido = False

    try:
        if request.POST:
            magickey = MagicKey.objects.get(
                key=key
            )
            if magickey:
                usuario = magickey.created_by
                nova_senha = request.POST['nova_senha']
                confirma_nova_senha = request.POST['confirma_nova_senha']
                if (nova_senha == confirma_nova_senha):
                    valido = True
                    user = User.objects.get(
                        email__iexact=usuario.email
                    )
                    user.set_password(nova_senha)
                    user.save()
                    resposta = 'Your password was updated.'
                    messages.success(
                        request,
                        resposta
                    )
                else:
                    resposta = 'Your password was not updated.'
                    messages.warning(
                        request,
                        resposta
                    )

    except Exception as exc:
        messages.warning(
            request,
            'ERROR_UPDATE_PASSWORD'
        )
    return render(
        request,
        'account/reset_password.html',
        {
        'valido': valido,
        'resposta': resposta
        }
    )


def send_email_for_reset_password(email, request):
    """Generate magic link and send this via email"""

    response = 'Um email foi enviado com o link para redefinir sua senha.'

    try:

        user = User.objects.get(
            email__iexact=email
        )
        if user:
            magickey = MagicKey()
            magickey.created_by = user
            magickey.save()

            key = magickey.key
            link = 'http://' + request.get_host() + '/account/reset_password/' + str(key)
            send_mail(
                'Redefinir sua senha',
                'Clique neste link para redefinir sua senha.\r\n' + link,
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
    except Exception as exc:
        raise exc
    return response


def request_reset_password(request):
    """Request a link for reset the password"""

    response = ''
    try:
        if request.POST:
            user = User.objects.get(
                email__iexact=request.POST['email']
            )

            if user:
                response = send_email_for_reset_password(
                    user.email,
                    request
                )
            else:
                if email:
                    response = 'Um email foi enviado com o link para redefinir sua senha.'
    except Exception as exc:
        response = 'Falha ao redefinir a senha.'
        messages.warning(
            request,
            'Falha ao redefinir a nova senha.'
        )
    return render(
        request,
        'account/request_reset_password.html',
        {
            'response': response,
        }
    )