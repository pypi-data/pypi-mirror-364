from django.conf import settings


def get_config(key, default=None):
    return getattr(settings, key, default)


CUSTOM_KEY = get_config('CUSTOM_KEY', "Fox-Cola-Tools")
CUSTOM_IV = get_config('CUSTOM_IV', "Fox-Cola-Tools")
