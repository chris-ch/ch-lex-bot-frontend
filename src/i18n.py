import gettext
import os


def load_translations(lang: str):
    localedir = os.path.abspath(os.path.join(os.path.curdir, 'resources', 'locale'))
    if not os.path.exists(localedir):
        raise BaseException(f"Locale folder not found: {localedir}")
    translate = gettext.translation('messages', localedir, languages=[lang])
    translate.install()
    return translate.gettext
