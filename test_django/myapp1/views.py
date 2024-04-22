import datetime

from django.db.models import Q
from django.shortcuts import render, redirect
from myapp1.models import Categories, Ads, Replies
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import send_mail
from django.contrib import messages, auth
from django.core.mail import EmailMessage


def index_page(request):
    return render(request, 'index.html')


def reg_page(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not username or not email or not password:
            messages.warning(request, 'Введите все данные')
            return redirect('register')

        new_user = User.objects.create_user(username, email, password)
        new_user.is_active = False
        new_user.save()
        print("Юзер создан", new_user.id)


        #TODO site_url в данный момент указывает на стандартный адрес тестового сервера
        #Если переносить проект на сервер - надо изменить переменную
        site_url = "http://127.0.0.1:8000"

        subject = 'Регистрация на сайте'  #Заголовок письма
        contact_message = f"""Вы зарегестрировались на нашем сайте
Для активации аккаунта можете перейти по этой ссылке: {site_url}/activate_user?id={new_user.id}"""
        from_email = settings.EMAIL_HOST_USER
        to_email = [request.POST.get("email")]
        send_mail(subject, contact_message, from_email, to_email, fail_silently=False)
    return render(request, 'reg.html')

def auth_page(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")

        print("Введенное имя пользователя:", username)
        print("Введенный пароль:", password)

        user = authenticate(request, username=username, password=password)  # Сама проверка, есть ли пользователь в БД
        print("Результат аутентификации:", user)

        if user is not None:
            # Если пользователь найден, выполняем вход
            login(request, user)
            # Перенаправляем пользователя на другую страницу после успешной аутентификации
            return redirect('/')  # Перекидывает на страницу успешной авторизации, если успешно
        else:

            error_message = 'Неверное имя пользователя или пароль'  # сообщение, если пользователь не найден

    return render(request, 'login.html', {'error_message': error_message if 'error_message' in locals() else ''})


def log_out(request):
    logout(request)
    return redirect('/')


def activate_user(request):
    id = request.GET['id']
    if not id:
        messages.warning(request, 'Неверная ссылка')
        return redirect('register')

    our_user = User.objects.get(id=id)
    #Eсли юзер зарегестрирован более чем трое суток назад - активация невозможна
    if abs(our_user.date_joined.date() - datetime.date.today()).days < 3:
        our_user.is_active = True
        our_user.save()

    return redirect('login')


def create_ad(request):
    if request.user.id:
        if request.method == 'POST':
            title = request.POST.get('title')
            text = request.POST.get('text')
            cat = request.POST.get('category')

            if title and text and cat:
                Ads.objects.create(title=title, text=text, cat_id=cat, user_id=request.user.id)

        categories = Categories.objects.all()
        data = {'сategories': categories, 'user': request.user.id}
    else:
        data = {'user': request.user.id}
    return render(request, "content.html", context=data)


def view_ad(request):
    if request.method == 'POST':
        text = request.POST.get('text')
        ad_id = request.POST.get('ad_id')

        if text and ad_id and request.user.id:
            Replies.objects.create(ads_id=ad_id, user_id=request.user.id, text=text)

            subject = 'Ответ на ваше сообщение'  # Заголовок письма
            contact_message = f"""На ваше объявление есть следующий отклик:
{text}
---
Посетите сайт, чтобы посмотреть!"""
            from_email = settings.EMAIL_HOST_USER
            to_email = [User.objects.get(id=Ads.objects.get(id=ad_id).user_id).email]
            send_mail(subject, contact_message, from_email, to_email, fail_silently=False)

    #Фильтр на все объявления отправленные НЕ текущим пользователем
    ads = Ads.objects.filter(~Q(user_id=request.user.id)).select_related('cat')
    data = {'ads': ads}

    return render(request, "ads.html", context=data)


def user(request):
    if request.method == 'POST':
        ad_id = request.POST.get('ad_id')
        rep_id = request.POST.get('rep_id')
        action = request.POST.get('action')

        if ad_id and rep_id and action and request.user.id:
            if action == "delete":
                Replies.objects.get(id=rep_id).delete()
            elif action == 'ok':
                user_id = Replies.objects.get(id=rep_id).id

                subject = 'Ваш отклик на объявление принят'  # Заголовок письма
                contact_message = "Ваш отклик на объявление принят! Посетите сайт, чтобы посмотреть!"
                from_email = settings.EMAIL_HOST_USER
                to_email = [User.objects.get(id=user_id).email]
                send_mail(subject, contact_message, from_email, to_email, fail_silently=False)


    #Вложенный запрос - берём id всех объявлений по id текущего пользователя
    inner_qs = Ads.objects.filter(user_id=request.user.id).values("id")
    #По списку id объявлений берём отклики
    replies = Replies.objects.filter(ads_id__in=inner_qs)
    data = {'replies': replies}

    return render(request, "user.html", context=data)


