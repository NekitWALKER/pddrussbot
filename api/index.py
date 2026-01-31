"""
Vercel Serverless Function для API
"""
import sys
import os

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database

app = Flask(__name__)
# Разрешаем CORS для веб-приложения на GitHub Pages и Vercel
CORS(app, origins=["https://nikirir.github.io", "https://pdd-duel-webapp.vercel.app", "http://localhost:*"])

db = Database()

@app.route('/api/duel/search/join', methods=['POST'])
def join_search():
    """Добавить пользователя в очередь поиска"""
    try:
        data = request.get_json()
        user_id_raw = data.get('user_id')
        
        # Обрабатываем как строку если это временный ID, иначе как int
        if isinstance(user_id_raw, str) and user_id_raw.startswith('temp-'):
            user_id = user_id_raw
        else:
            user_id = int(user_id_raw) if user_id_raw else None
            
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id required'}), 400
        
        db.add_to_search_queue(str(user_id))
        print(f"✅ Пользователь {user_id} добавлен в очередь поиска")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка добавления в очередь: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/duel/search/check', methods=['POST'])
def check_opponent():
    """Проверить, найден ли противник"""
    try:
        data = request.get_json()
        user_id_raw = data.get('user_id')
        
        # Обрабатываем как строку если это временный ID, иначе как int
        if isinstance(user_id_raw, str) and user_id_raw.startswith('temp-'):
            user_id = user_id_raw
        else:
            user_id = int(user_id_raw) if user_id_raw else None
            
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id required'}), 400
        
        opponent_id = db.find_opponent(str(user_id))
        
        if opponent_id:
            print(f"✅ Найден противник для {user_id}: {opponent_id}")
            return jsonify({'success': True, 'opponent_id': opponent_id})
        else:
            return jsonify({'success': True, 'opponent_id': None})
    except Exception as e:
        print(f"❌ Ошибка поиска противника: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/duel/search/leave', methods=['POST'])
def leave_search():
    """Покинуть очередь поиска"""
    try:
        data = request.get_json()
        user_id_raw = data.get('user_id')
        
        if isinstance(user_id_raw, str) and user_id_raw.startswith('temp-'):
            user_id = user_id_raw
        else:
            user_id = int(user_id_raw) if user_id_raw else None
            
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id required'}), 400
        
        db.remove_from_search_queue(str(user_id))
        print(f"✅ Пользователь {user_id} покинул очередь поиска")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка выхода из очереди: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/duel/progress/update', methods=['POST'])
def update_progress():
    """Обновить прогресс дуэли"""
    try:
        data = request.get_json()
        user_id_raw = data.get('user_id')
        opponent_id_raw = data.get('opponent_id')
        current_question = data.get('current_question', 0)
        user_score = data.get('user_score', 0)
        
        if isinstance(user_id_raw, str) and user_id_raw.startswith('temp-'):
            user_id = user_id_raw
        else:
            user_id = int(user_id_raw) if user_id_raw else None
            
        if isinstance(opponent_id_raw, str) and opponent_id_raw.startswith('temp-'):
            opponent_id = opponent_id_raw
        else:
            opponent_id = int(opponent_id_raw) if opponent_id_raw else None
        
        if not user_id or not opponent_id:
            return jsonify({'success': False, 'error': 'user_id and opponent_id required'}), 400
        
        db.update_duel_progress(str(user_id), str(opponent_id), current_question, user_score)
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка обновления прогресса: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/duel/progress/get', methods=['POST'])
def get_progress():
    """Получить прогресс противника"""
    try:
        data = request.get_json()
        user_id_raw = data.get('user_id')
        opponent_id_raw = data.get('opponent_id')
        
        if isinstance(user_id_raw, str) and user_id_raw.startswith('temp-'):
            user_id = user_id_raw
        else:
            user_id = int(user_id_raw) if user_id_raw else None
            
        if isinstance(opponent_id_raw, str) and opponent_id_raw.startswith('temp-'):
            opponent_id = opponent_id_raw
        else:
            opponent_id = int(opponent_id_raw) if opponent_id_raw else None
        
        if not user_id or not opponent_id:
            return jsonify({'success': False, 'error': 'user_id and opponent_id required'}), 400
        
        progress = db.get_opponent_progress(str(user_id), str(opponent_id))
        
        if progress:
            return jsonify({
                'success': True,
                'current_question': progress[0],
                'opponent_score': progress[1]
            })
        else:
            return jsonify({
                'success': True,
                'current_question': 0,
                'opponent_score': 0
            })
    except Exception as e:
        print(f"❌ Ошибка получения прогресса: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/top/players', methods=['GET'])
def get_top_players():
    """Получить топ игроков из базы данных"""
    try:
        top_users = db.get_top_users(limit=None)  # Получаем всех пользователей
        
        print(f"📊 Получено пользователей из БД: {len(top_users)}")
        
        players = []
        for user in top_users:
            # user может быть с photo_url и hide_username или без (в зависимости от версии БД)
            if len(user) >= 9:
                user_id, username, first_name, photo_url, hide_username, wins, losses, total_games, win_rate = user
            elif len(user) >= 8:
                user_id, username, first_name, photo_url, wins, losses, total_games, win_rate = user
                hide_username = 0
            else:
                user_id, username, first_name, wins, losses, total_games, win_rate = user
                photo_url = None
                hide_username = 0
            
            # Логируем для отладки
            print(f"👤 Пользователь {user_id}: username={username}, first_name={first_name}, photo_url={photo_url}, hide_username={hide_username}")
            
            players.append({
                'user_id': user_id,
                'username': username or '',  # Убеждаемся что это не None
                'first_name': first_name or '',  # Убеждаемся что это не None
                'photo_url': photo_url or '',  # Убеждаемся что это не None
                'hide_username': bool(hide_username),  # Преобразуем в boolean
                'wins': wins,
                'losses': losses,
                'total_games': total_games,
                'win_rate': win_rate
            })
        
        print(f"✅ Возвращаем {len(players)} игроков")
        
        return jsonify({
            'success': True,
            'players': players
        })
    except Exception as e:
        print(f"❌ Ошибка получения топа игроков: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Регистрация пользователя из бота или веб-приложения"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        username = data.get('username')
        first_name = data.get('first_name')
        nickname = data.get('nickname')  # Новое поле для псевдонима
        photo_url = data.get('photo_url')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'user_id required'}), 400
        
        # Преобразуем user_id в int если это не строка
        if isinstance(user_id, str) and not user_id.startswith('temp-'):
            try:
                user_id = int(user_id)
            except ValueError:
                pass
        
        # Если есть nickname, проверяем его уникальность
        if nickname:
            nickname = nickname.strip()[:10]  # Максимум 10 символов
            if not db.check_nickname_available(nickname, exclude_user_id=user_id):
                # Предлагаем похожие варианты
                suggestions = db.suggest_nicknames(nickname, limit=5)
                return jsonify({
                    'success': False,
                    'error': 'nickname_taken',
                    'message': 'Этот псевдоним уже занят',
                    'suggestions': suggestions
                }), 400
        
        # Используем nickname если есть, иначе first_name
        display_name = nickname if nickname else first_name
        
        # Используем Database напрямую для регистрации пользователя
        db.get_or_create_user(user_id, username, display_name, photo_url, nickname)
        
        print(f"✅ Пользователь {user_id} зарегистрирован через API: username={username}, first_name={display_name}, nickname={nickname}, photo_url={photo_url}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка регистрации пользователя: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/users/settings', methods=['POST'])
def update_user_settings():
    """Обновить настройки пользователя"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        setting_name = data.get('setting_name')
        setting_value = data.get('setting_value')
        
        if not user_id or not setting_name:
            return jsonify({'success': False, 'error': 'user_id and setting_name required'}), 400
        
        # Преобразуем user_id в int если это не строка
        if isinstance(user_id, str) and not user_id.startswith('temp-'):
            try:
                user_id = int(user_id)
            except ValueError:
                pass
        
        # Обновляем настройку
        db.update_user_setting(user_id, setting_name, setting_value)
        
        print(f"✅ Настройка {setting_name} для пользователя {user_id} обновлена: {setting_value}")
        
        return jsonify({'success': True})
    except Exception as e:
        print(f"❌ Ошибка обновления настроек пользователя: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    import time
    return jsonify({
        'status': 'ok',
        'timestamp': int(time.time())
    })

# Vercel требует функцию handler для Serverless Functions
# Экспортируем app для использования в Vercel
# Vercel автоматически найдет app и использует его как WSGI приложение

