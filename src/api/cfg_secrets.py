from cfg_handler import load_config


def load_config_secrets():
    return load_config("json/cfg_secrets.json", 'local')

cfg = load_config_secrets()

GOOGLE_SERVICE_ACCOUNT = cfg.get('google_service_account')  # for services, such as Speach-to-Text