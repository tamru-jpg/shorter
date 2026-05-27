from flask import request
import requests


def get_client_ip():
    """Определяет реальный IP-адрес клиента с учётом прокси"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    if ip == '127.0.0.1':
        ip = '8.8.8.8'
    return ip


def get_country_by_ip(ip):
    """Определяет страну и город по IP через бесплатный API ip-api.com"""
    try:
        url = f'http://ip-api.com/json/{ip}'
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get('status') == 'success':
            country = data.get('country', 'Unknown')
            city = data.get('city', 'Unknown')
            return country, city
        else:
            return 'Unknown', 'Unknown'
    except Exception:
        return 'Unknown', 'Unknown'
