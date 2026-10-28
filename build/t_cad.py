import design as D, cad_draw as C
from design import *
s = D.Sheet('tmp/t_cad.pdf', bg=PAPER_C)
sc = 8.2
x0, y0 = 60, 40
C.draw_elevation(s, x0, y0, sc, y_from=0, y_to=29.2)
# levels to the left
C.grounded_levels(s, x0 - 6, y0, sc, 0, 29.2)
C.zone_bracket(s, x0 + 10.7*sc + 6, y0 + (29.2-28.85)*sc, y0 + (29.2-20.75)*sc, 'A')
C.zone_bracket(s, x0 + 10.7*sc + 6, y0 + (29.2-20.75)*sc, y0 + (29.2-13.65)*sc, 'B')
C.zone_bracket(s, x0 + 10.7*sc + 6, y0 + (29.2-13.65)*sc, y0 + (29.2-0)*sc, 'C')
C.locator(s, 250, 40, 22, 74, active='A')
s.save()
