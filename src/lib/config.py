import os
import configparser

lib_dir = os.path.dirname(__file__)
env_config = configparser.ConfigParser()


# 파일을 읽을 때 인코딩을 명시적으로 지정합니다.
with open(os.path.join(lib_dir, 'config.ini'), 'r', encoding='utf-8') as f:
    env_config.read_file(f)

api_key = env_config['AUTH']['api_key']
api_secret = env_config['AUTH']['api_secret']
protocol = env_config['SERVER']['protocol']
domain = env_config['SERVER']['domain']
prefix = env_config['SERVER']['prefix'] and env_config['SERVER']['prefix'] or ''


def get_url(path):
    url = '%s://%s' % (protocol, domain)
    if prefix != '':
        url = url + prefix
    url = url + path
    return url
