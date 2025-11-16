from flask import request, make_response, redirect, url_for
import requests
import os

# Загрузка OAuth credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

def login():
    """Перенаправление на Яндекс для авторизации"""
    auth_url = (
        f"https://oauth.yandex.ru/authorize?"
        f"response_type=code&"
        f"client_id={CLIENT_ID}&" 
        f"redirect_uri={REDIRECT_URI}"
    )
    return redirect(auth_url)

def autorisationYA():
    error = None
    error_description = None

    # 1. Проверка ошибок от Яндекс
    if 'error' in request.args:
        error = request.args.get('error')
        error_description = request.args.get('error_description', '')
        return f"Ошибка авторизации: {error} - {error_description}", 400

    # 2. Получаем код авторизации
    auth_code = request.args.get('code')
    if not auth_code:
        return make_response("Ошибка: код авторизации не получен", 400)

    # 3. Запрос токена
    token_url = "https://oauth.yandex.ru/token"
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    response = requests.post(token_url, data=data, headers=headers)
    response.raise_for_status()
    token_data = response.json()
    access_token = token_data['access_token']

    # 4. Получаем данные пользователя
    user_info_response = requests.get(
        'https://login.yandex.ru/info',
        params={'format': 'json'},
        headers={'Authorization': f'OAuth {access_token}'}
    )
    user_info_response.raise_for_status()
    user_info = user_info_response.json()

    return access_token, token_data, user_info
