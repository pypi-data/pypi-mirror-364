from urllib.parse import unquote
from urllib.parse import quote

baseURL = 'https://molar-app-prod-v5.oss-cn-hangzhou.aliyuncs.com/'

def unqt(str):
    return unquote(str)

def qt(str):
    return quote(str)