import design as D
from design import INK, PAPER, GOLD
s = D.Sheet('tmp/t_rtl.pdf', bg=PAPER, w=160, h=90)
s.fa('ساختمان', 22, 10, 20, INK)          # expect leftmost = ن
s.fa('ابج', 22, 80, 20, INK)              # expect leftmost = ج
s.fa('نمای ساختمان', 14, 10, 45, INK)
s.fa('مرحبا بالعالم', 14, 10, 65, INK)
s.en('ABCD abcd 123', 12, 10, 82, INK)
s.save()
