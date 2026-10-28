import design as D
from design import INK, PAPER
s = D.Sheet('tmp/t_rtl2.pdf', bg=PAPER, w=200, h=120)
for i, w in enumerate(['با', 'اب', 'بابا', 'سلام', 'کتاب', 'ساختمان', 'نمای']):
    s.fa(w, 34, 20, 22 + i*16, INK)
    s.en(f'{i}', 8, 6, 22 + i*16, INK)
s.save()
