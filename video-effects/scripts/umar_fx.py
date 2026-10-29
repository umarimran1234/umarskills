# ---------- pack 3: creator + SaaS effects, by Umar Imran (github.com/umarimran1234) ----------
# Loaded by fx.py (exec'd into its globals), so helpers like rrect, place, comp, text_img, fit_text, font, shadowed,
# face_chip, heart, cached, pop, fade, clamp, ease_back, ease_out and @effect are all available here.
# The original 45 effects are (c) 2026 Vibha Ramprakash, MIT. These 5 are new.


def _down_arrow(s, col):
    s = int(s); im = Image.new('RGBA', (s, int(s * 1.2)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle([s * .36, 0, s * .64, s * .62], int(s * .1), fill=col + (255,))
    d.polygon([(s * .12, s * .55), (s * .88, s * .55), (s * .5, s * 1.18)], fill=col + (255,))
    return shadowed(im, 6, 4, 120)


def _star(s, col):
    s = int(s); im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    pts = []
    for i in range(10):
        r = s * 0.48 if i % 2 == 0 else s * 0.2; a = -math.pi / 2 + i * math.pi / 5
        pts.append((s / 2 + r * math.cos(a), s / 2 + r * math.sin(a)))
    ImageDraw.Draw(im).polygon(pts, fill=col + (255,)); return im


@effect('dm-popup', 'an Instagram DM notification drops in from the top with your message')
def fx_dm_popup(c, e):
    name = e.o.get('name', '@yourname'); msg = e.o.get('text', 'Here you go! Tap the button below')
    w, h = int(c.W * 0.9), int(c.W * 0.2)
    def build():
        im = rrect(w, h, h * 0.3, (250, 250, 252, 255)); d = ImageDraw.Draw(im)
        r = int(h * 0.36); av = face_chip(c, e, r * 2); ring = rrect(r * 2 + 10, r * 2 + 10, r + 5, (255, 75, 120, 255))
        m = Image.new('L', ring.size, 0); ImageDraw.Draw(m).ellipse([0, 0, ring.width - 1, ring.height - 1], fill=255); ring.putalpha(m)
        im.alpha_composite(ring, (int(h * 0.14), int(h / 2 - r - 5))); im.alpha_composite(av, (int(h * 0.14) + 5, int(h / 2 - r)))
        x = int(h * 0.14 + 2 * r + h * 0.22)
        d.text((x, h * 0.34), name, font=font('uib', h * 0.25), fill=(20, 20, 24, 255), anchor='lm')
        size = h * 0.22
        while size > 10 and font('ui', size).getlength(msg) > w - x - h * 0.9: size *= 0.94
        d.text((x, h * 0.67), msg, font=font('ui', size), fill=(90, 90, 100, 255), anchor='lm')
        d.text((w - h * 0.28, h * 0.34), 'now', font=font('ui', h * 0.2), fill=(150, 150, 160, 255), anchor='rm')
        d.ellipse([w - h * 0.4, h * 0.6, w - h * 0.2, h * 0.8], fill=(255, 48, 90, 255))
        return shadowed(im, 14, 10, 130)
    im = cached(e, 'dm', build)
    y0 = c.H * 0.07 + h / 2
    enter = ease_back(c.lt / 0.5); leave = ease_out((c.lt - (e.d - 0.35)) / 0.35) if c.lt > e.d - 0.35 else 0
    y = -h + (y0 + h) * clamp(enter, 0, 1.08) - leave * (y0 + h * 1.2)
    place(c, im, c.W / 2, y, 1.0, 0, 1.0)


@effect('step-cards', 'numbered step cards pop in one after another under your chin')
def fx_step_cards(c, e):
    steps = e.o.get('text', 'Install the skill|Connect Claude|Make your reel').split('|')[:5]
    n = len(steps); w, h, gap = int(c.W * 0.78), int(c.W * 0.14), int(c.W * 0.025); col = rgb(e.o.get('color'), (255, 75, 58))
    def build(i, s):
        im = rrect(w, h, h * 0.28, (250, 246, 236, 255)); d = ImageDraw.Draw(im); r = h * 0.34
        d.ellipse([h * 0.2, h / 2 - r, h * 0.2 + 2 * r, h / 2 + r], fill=col + (255,))
        d.text((h * 0.2 + r, h / 2), str(i + 1), font=font('bold', r * 1.1), fill=(255, 255, 255, 255), anchor='mm')
        t = fit_text(s, w - h * 1.25, 'montb', int(h * 0.48), fill=INK)
        im.alpha_composite(t, (int(h * 1.0), int(h / 2 - t.height / 2)))
        return shadowed(im, 12, 8, 120)
    total = n * h + (n - 1) * gap
    y0 = min(c.H - total - c.H * 0.05, max(c.fy + c.fw * 1.9, c.H * 0.52))
    per = min(0.6, max(0.2, (e.d - 0.5) / n))
    for i, s in enumerate(steps):
        k = pop(c, 0.15 + i * per * 0.9, 0.35)
        if k <= 0: continue
        im = cached(e, ('s', i), lambda i=i, s=s: build(i, s))
        slide = (1 - clamp(k)) * c.W * 0.25 * (1 if i % 2 == 0 else -1)
        place(c, im, c.W / 2 + slide, y0 + i * (h + gap) + h / 2, 0.85 + 0.15 * min(k, 1.1), 0, fade(c, e) * clamp(k * 2), guard=True)


@effect('stat-counter', 'a big number counts up above your head, like users or followers')
def fx_stat_counter(c, e):
    to, frm = float(e.o.get('to', 12400)), float(e.o.get('from', 0)); label = e.o.get('text', 'new users'); col = rgb(e.o.get('color'), (255, 210, 63))
    p = ease_out(c.lt / max(0.5, min(2.2, e.d * 0.7))); v = frm + (to - frm) * p
    num = text_img(f"{int(round(v)):,}{e.o.get('suffix', '+')}", int(c.W * 0.15), 'bold', fill=(255, 255, 255), shadow=8)
    lab = cached(e, 'lab', lambda: text_img(label.upper(), int(c.W * 0.04), 'mono', fill=col, shadow=4))
    k = ease_back(c.lt / 0.3); al = fade(c, e) * clamp(c.lt / 0.15)
    top = c.fy - c.fw * 2.3; room = top >= num.height * 0.75 + c.H * 0.03   # room above the head? else sit under the chin
    y = top if room else min(c.H * 0.74, c.fy + c.fw * 3.4)
    bw, bh = int(max(num.width, lab.width) * 0.86), int(num.height * 1.25)
    plate = cached(e, 'plate', lambda: rrect(bw, bh, bh * 0.3, (14, 14, 20, 175)))   # dark plate so the number reads on any shirt
    place(c, plate, c.W / 2, y + num.height * 0.2, 0.8 + 0.2 * clamp(k, 0, 1.1), 0, al, behind=room)
    place(c, num, c.W / 2, y, 0.8 + 0.2 * clamp(k, 0, 1.1), 0, al, behind=room)
    place(c, lab, c.W / 2, y + num.height * 0.52, 1.0, 0, al, behind=room)


@effect('cta-pill', 'a big COMMENT: WORD pill pulses near the bottom with a bouncing arrow')
def fx_cta_pill(c, e):
    word = e.o.get('text', 'SKILL').upper(); lead = e.o.get('lead', 'COMMENT:'); col = rgb(e.o.get('color'), (255, 75, 58))
    w, h = int(c.W * 0.82), int(c.W * 0.17)
    def build():
        im = rrect(w, h, h / 2, col + (255,), (255, 255, 255, 255), max(4, h // 18))
        t = fit_text(f'{lead} {word}', w * 0.76, 'bold', int(h * 0.55), fill=(255, 255, 255)); im.alpha_composite(t, (int(w / 2 - t.width / 2), int(h / 2 - t.height / 2)))
        return shadowed(im, 16, 10, 150)
    pill = cached(e, 'p', build); arrow = cached(e, 'a', lambda: _down_arrow(c.W * 0.08, (255, 255, 255)))
    k = clamp(ease_back(c.lt / 0.4), 0, 1.1); pulse = 1 + 0.035 * math.sin(c.lt * 7); al = fade(c, e) * clamp(c.lt / 0.2)
    y = c.H * 0.86
    place(c, pill, c.W / 2, y, k * pulse, 0, al)
    bob = abs(math.sin(c.lt * 5)) * c.W * 0.03
    place(c, arrow, c.W / 2, y - h * 0.95 - bob, k, 0, al)


@effect('reaction-burst', 'hearts and stars float up from the bottom corner like live reactions')
def fx_reaction_burst(c, e):
    n = int(e.o.get('count', 18)); cols = [(255, 48, 64), (255, 120, 150), (255, 200, 60), (124, 92, 255), (255, 255, 255)]
    parts = cached(e, 'parts', lambda: [(random.Random(i).random() * max(0.2, e.d - 1.0), 0.62 + 0.34 * random.Random(i + 11).random(),
                                         0.35 + 0.3 * random.Random(i + 21).random(), c.W * (0.02 + 0.05 * random.Random(i + 31).random()),
                                         c.W * (0.07 + 0.06 * random.Random(i + 41).random()), i % 3, cols[i % len(cols)]) for i in range(n)])
    for i, (t0, x0, speed, sway, size, kind, col) in enumerate(parts):
        lt = c.lt - t0
        if lt < 0: continue
        y = c.H * 1.04 - lt * speed * c.H
        if y < -size: continue
        im = cached(e, ('i', i), lambda size=size, col=col, kind=kind: _star(size, col) if kind == 2 else heart(size, col))
        a = clamp(lt / 0.2) * clamp(y / (c.H * 0.25)) * fade(c, e)
        place(c, im, c.W * x0 + math.sin(lt * 3 + i) * sway, y, 1.0, math.sin(lt * 2 + i) * 14, a)
