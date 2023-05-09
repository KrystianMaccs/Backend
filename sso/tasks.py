import secrets
import uuid

def get_access_token() -> str:
    return secrets.token_urlsafe()

def secret_key_gen() -> str:
    length = 128
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'+str(uuid.uuid4())

    secret_key = ''.join(secrets.choice(chars) for i in range(length))

    return secret_key

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    return request.META['HTTP_USER_AGENT']
