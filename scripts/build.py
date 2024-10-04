import subprocess
from pathlib import Path

def compile_translations():
    locale_dir = Path('resources/locale')
    for po_file in locale_dir.glob('**/LC_MESSAGES/*.po'):
        print(f"compiling file {po_file}")
        mo_file = po_file.with_suffix('.mo')
        subprocess.run(['msgfmt', str(po_file), '-o', str(mo_file)], check=True)

def build(setup_kwargs):
    compile_translations()
    return setup_kwargs

if __name__ == '__main__':
    compile_translations()
