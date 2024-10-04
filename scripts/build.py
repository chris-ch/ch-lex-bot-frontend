import pathlib
import gettext
import polib


def compile_po_file(po_file_path):
    mo_file_path = po_file_path.with_suffix('.mo')
    try:
        po = polib.pofile(str(po_file_path))
        po.save_as_mofile(str(mo_file_path))
        print(f"successfully compiled {po_file_path} to {mo_file_path}")
    except Exception as e:
        print(f"error compiling {po_file_path}: {str(e)}")


def compile_translations():
    locale_dir = pathlib.Path('resources/locale')
    for po_file in locale_dir.glob('**/LC_MESSAGES/*.po'):
        compile_po_file(po_file)


def build(setup_kwargs):
    compile_translations()
    return setup_kwargs


if __name__ == '__main__':
    compile_translations()
