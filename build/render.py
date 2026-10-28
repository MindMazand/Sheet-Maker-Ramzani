import os, sys, importlib, subprocess
import pymupdf

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sheets')
PREV = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tmp')
os.makedirs(OUT, exist_ok=True); os.makedirs(PREV, exist_ok=True)

def render(mod, names, dpi=110, both=True):
    m = importlib.import_module(mod)
    for n in names:
        pdf = os.path.join(OUT, f'{n}.pdf')
        fn = getattr(m, n)
        fn(pdf, OUT)
        d = pymupdf.open(pdf)
        d[0].get_pixmap(dpi=dpi).save(os.path.join(PREV, f'{n}.png'))
        print('ok', n, round(os.path.getsize(pdf)/1e6,2), 'MB')

if __name__ == '__main__':
    mod = sys.argv[1]
    names = sys.argv[2:]
    render(mod, names)
