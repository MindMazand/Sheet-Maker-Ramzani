import design as D
from design import INK, PAPER, GRAPHITE
s = D.Sheet('tmp/t_sep.pdf', bg=PAPER, w=120, h=40)
s.fa('+۲۸٫۸۵   +۲۸.۸۵   +۲۸/۸۵', 22, 8, 18, INK)
s.fa('محدوده A — بخش فوقانی', 12, 8, 32, INK)
s.fa('محدوده آ — بخش فوقانی', 12, 8, 40, INK)
s.save()
