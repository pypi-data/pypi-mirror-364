from http.cookiejar import CookieJar, Cookie

from ...cffi_loader import addCookiesToSession, getCookiesFromSession


def add_cookies_to_session():
    raise NotImplementedError

def get_cookies_from_session():
    raise NotImplementedError
