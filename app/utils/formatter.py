from datetime import datetime

def format_timestamp(ts):
    if not ts:
        return "N/A"
    return datetime.fromtimestamp(int(ts).strftime("%Y-%m-%d %H:%M:%S"))

def format_xtream_response(data):
    user = data.user_info
    server = data.server_info
    
    return f"""
    Estado: {user.status}
    Usuario: {user.username}
    Expira: {format_timestamp(user.exp_date)}
    Creado: {format_timestamp(user.created_at)}
    Conexiones: {user.active_cons}/{user.max_connections}
    Zona: {server.timezone}
"""