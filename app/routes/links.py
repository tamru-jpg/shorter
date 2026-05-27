import random
import string
import requests
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.db import db
from app.models import Link, Click

bp = Blueprint('links', __name__)


def generate_short_code():
    """Генерирует уникальный короткий код"""
    bases = ['link', 'page', 'site', 'doc', 'post', 'news', 'info', 'data', 'code']

    for _ in range(30):
        base = random.choice(bases)
        number = random.randint(10, 999)
        code = f"{base}{number}"

        if not Link.query.filter_by(short_code=code).first():
            return code

    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))


def get_visitor_info():
    """Получает информацию о посетителе: IP, гео, браузер, устройство"""
    from flask import request

    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr

    if ip == '127.0.0.1' or ip == '::1':
        ip = '8.8.8.8'

    geo_info = {}
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}', timeout=3)
        geo_data = response.json()
        if geo_data.get('status') == 'success':
            geo_info = {
                'country': geo_data.get('country', 'Unknown'),
                'city': geo_data.get('city', 'Unknown'),
                'region': geo_data.get('regionName', 'Unknown'),
            }
        else:
            geo_info = {'country': 'Unknown', 'city': 'Unknown', 'region': 'Unknown'}
    except Exception as e:
        print(f"GeoIP ошибка: {e}")
        geo_info = {'country': 'Unknown', 'city': 'Unknown', 'region': 'Unknown'}

    user_agent = request.headers.get('User-Agent', 'Unknown')

    device = 'Desktop'
    if 'Mobile' in user_agent or 'Android' in user_agent or 'iPhone' in user_agent:
        device = 'Mobile'
    elif 'iPad' in user_agent:
        device = 'Tablet'

    browser = 'Unknown'
    if 'Chrome' in user_agent and 'Edg' not in user_agent:
        browser = 'Chrome'
    elif 'Firefox' in user_agent:
        browser = 'Firefox'
    elif 'Safari' in user_agent and 'Chrome' not in user_agent:
        browser = 'Safari'
    elif 'Edg' in user_agent:
        browser = 'Edge'
    elif 'Opera' in user_agent:
        browser = 'Opera'

    os_type = 'Unknown'
    if 'Windows' in user_agent:
        os_type = 'Windows'
    elif 'Mac' in user_agent:
        os_type = 'macOS'
    elif 'Linux' in user_agent:
        os_type = 'Linux'
    elif 'Android' in user_agent:
        os_type = 'Android'
    elif 'iPhone' in user_agent or 'iPad' in user_agent:
        os_type = 'iOS'

    return {
        'ip': ip,
        'country': geo_info.get('country', 'Unknown'),
        'city': geo_info.get('city', 'Unknown'),
        'region': geo_info.get('region', 'Unknown'),
        'device': device,
        'browser': browser,
        'os': os_type,
        'user_agent': user_agent[:500],
        'referer': request.headers.get('Referer', 'Direct')
    }


@bp.route('/create-link', methods=['POST'])
@login_required
def create_link():
    """Создание короткой ссылки"""
    original_url = request.form.get('original_url')
    short_code = generate_short_code()

    link = Link(
        user_id=current_user.id,
        original_url=original_url,
        short_code=short_code
    )

    db.session.add(link)
    db.session.commit()

    flash(f'Ваша ссылка: {request.host_url}{short_code}', 'success')
    return redirect(url_for('main.main'))


@bp.route('/my_links')
@login_required
def show_links():
    """Отображает список всех ссылок текущего пользователя"""
    user_links = Link.query.filter_by(user_id=current_user.id).all()
    return render_template('my_links.html', links=user_links)


@bp.route('/stats')
@login_required
def overall_stats():
    """Общая статистика по всем ссылкам пользователя"""
    links = Link.query.filter_by(user_id=current_user.id).all()
    total_clicks = sum(link.clicks_count or 0 for link in links)
    return render_template('stats.html', links=links, total_clicks=total_clicks)


@bp.route('/api/link-stats/<int:link_id>')
@login_required
def api_link_stats(link_id):
    """API: возвращает детальную статистику по ссылке в формате JSON"""
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()

    clicks = Click.query.filter_by(link_id=link.id).order_by(Click.clicked_at.desc()).all()

    countries = db.session.query(
        Click.country,
        db.func.count(Click.id).label('count')
    ).filter_by(link_id=link.id).group_by(Click.country).all()

    cities = db.session.query(
        Click.city,
        Click.country,
        db.func.count(Click.id).label('count')
    ).filter_by(link_id=link.id).group_by(Click.city, Click.country).all()

    devices = db.session.query(
        Click.device,
        db.func.count(Click.id).label('count')
    ).filter_by(link_id=link.id).group_by(Click.device).all()

    browsers = db.session.query(
        Click.browser,
        db.func.count(Click.id).label('count')
    ).filter_by(link_id=link.id).group_by(Click.browser).all()

    os_stats = db.session.query(
        Click.os,
        db.func.count(Click.id).label('count')
    ).filter_by(link_id=link.id).group_by(Click.os).all()

    from datetime import timedelta
    daily_stats = []
    for i in range(7):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0)
        day_end = day.replace(hour=23, minute=59, second=59)
        count = Click.query.filter(
            Click.link_id == link.id,
            Click.clicked_at.between(day_start, day_end)
        ).count()
        daily_stats.append({'date': day.strftime('%Y-%m-%d'), 'count': count})

    return jsonify({
        'success': True,
        'link': {
            'id': link.id,
            'original_url': link.original_url,
            'short_code': link.short_code,
            'clicks_count': link.clicks_count or 0,
            'created_at': link.created_at.isoformat() if link.created_at else None
        },
        'clicks': [{
            'clicked_at': c.clicked_at.isoformat() if c.clicked_at else None,
            'country': c.country,
            'city': c.city,
            'device': c.device,
            'browser': c.browser,
            'os': c.os,
            'ip_address': c.ip_address,
            'referer': c.referer
        } for c in clicks[:100]],
        'countries': [{'name': c[0] or 'Неизвестно', 'count': c[1]} for c in countries],
        'cities': [{'city': c[0] or 'Неизвестно', 'country': c[1] or '—', 'count': c[2]} for c in cities],
        'devices': [{'name': d[0] or 'Неизвестно', 'count': d[1]} for d in devices],
        'browsers': [{'name': b[0] or 'Неизвестно', 'count': b[1]} for b in browsers],
        'os': [{'name': o[0] or 'Неизвестно', 'count': o[1]} for o in os_stats],
        'daily_stats': daily_stats[::-1]
    })


@bp.route('/stats/<int:link_id>')
@login_required
def show_stats(link_id):
    """Страница статистики для ссылки"""
    link = Link.query.filter_by(id=link_id, user_id=current_user.id).first_or_404()
    return render_template('stats_detail.html', link=link)


@bp.route('/api/delete-link/<int:link_id>', methods=['DELETE'])
@login_required
def api_delete_link(link_id):
    """Удаляет ссылку пользователя"""
    try:
        link = Link.query.filter_by(id=link_id, user_id=current_user.id).first()

        if not link:
            return jsonify({'success': False, 'error': 'Ссылка не найдена'}), 404

        db.session.delete(link)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Ссылка удалена'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/api/create-link', methods=['POST'])
@login_required
def api_create_link():
    """API: создание короткой ссылки через AJAX-запрос"""
    try:
        original_url = request.form.get('original_url')

        if not original_url:
            return jsonify({'success': False, 'error': 'URL не может быть пустым'}), 400

        if not original_url.startswith(('http://', 'https://')):
            original_url = 'https://' + original_url

        short_code = generate_short_code()

        link = Link(
            user_id=current_user.id,
            original_url=original_url,
            short_code=short_code
        )

        db.session.add(link)
        db.session.commit()

        short_url = request.host_url + short_code

        return jsonify({
            'success': True,
            'short_url': short_url,
            'short_code': short_code
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<short_code>')
def redirect_to_original(short_code):
    """Переход по короткой ссылке с записью статистики"""
    link = Link.query.filter_by(short_code=short_code).first_or_404()

    visitor = get_visitor_info()

    click = Click(
        link_id=link.id,
        clicked_at=datetime.utcnow(),
        ip_address=visitor['ip'],
        user_agent=visitor['user_agent'],
        referer=visitor['referer'],
        country=visitor['country'],
        city=visitor['city'],
        device=visitor['device'],
        browser=visitor['browser'],
        os=visitor['os']
    )

    link.clicks_count = (link.clicks_count or 0) + 1

    db.session.add(click)
    db.session.commit()

    return redirect(link.original_url)
