"""Render pixel-art GitHub stats cards from live API data. No third party at runtime."""
import json, subprocess, os, datetime
from collections import Counter

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets')
USER = 'KomangKlomang'
PX = 3

F = {
 'A':'01110 10001 10001 11111 10001 10001 10001','B':'11110 10001 11110 10001 10001 10001 11110',
 'C':'01110 10001 10000 10000 10000 10001 01110','D':'11110 10001 10001 10001 10001 10001 11110',
 'E':'11111 10000 11110 10000 10000 10000 11111','F':'11111 10000 11110 10000 10000 10000 10000',
 'G':'01110 10001 10000 10111 10001 10001 01111','H':'10001 10001 10001 11111 10001 10001 10001',
 'I':'11111 00100 00100 00100 00100 00100 11111','J':'00111 00010 00010 00010 00010 10010 01100',
 'K':'10001 10010 10100 11000 10100 10010 10001','L':'10000 10000 10000 10000 10000 10000 11111',
 'M':'10001 11011 10101 10101 10001 10001 10001','N':'10001 11001 10101 10011 10001 10001 10001',
 'O':'01110 10001 10001 10001 10001 10001 01110','P':'11110 10001 10001 11110 10000 10000 10000',
 'Q':'01110 10001 10001 10001 10101 10010 01101','R':'11110 10001 10001 11110 10100 10010 10001',
 'S':'01111 10000 10000 01110 00001 00001 11110','T':'11111 00100 00100 00100 00100 00100 00100',
 'U':'10001 10001 10001 10001 10001 10001 01110','V':'10001 10001 10001 10001 10001 01010 00100',
 'W':'10001 10001 10001 10101 10101 11011 10001','X':'10001 10001 01010 00100 01010 10001 10001',
 'Y':'10001 10001 01010 00100 00100 00100 00100','Z':'11111 00001 00010 00100 01000 10000 11111',
 '0':'01110 10011 10101 10101 11001 10001 01110','1':'00100 01100 00100 00100 00100 00100 01110',
 '2':'01110 10001 00001 00010 00100 01000 11111','3':'11111 00010 00100 00010 00001 10001 01110',
 '4':'00010 00110 01010 10010 11111 00010 00010','5':'11111 10000 11110 00001 00001 10001 01110',
 '6':'00110 01000 10000 11110 10001 10001 01110','7':'11111 00001 00010 00100 01000 01000 01000',
 '8':'01110 10001 10001 01110 10001 10001 01110','9':'01110 10001 10001 01111 00001 00010 01100',
 '%':'11001 11010 00010 00100 01000 01011 10011','.':'00000 00000 00000 00000 00000 00000 00100',
 '-':'00000 00000 00000 01110 00000 00000 00000','/':'00001 00010 00010 00100 01000 01000 10000',
 '?':'01110 10001 00001 00010 00100 00000 00100','!':'00100 00100 00100 00100 00100 00000 00100',
 ' ':'00000 00000 00000 00000 00000 00000 00000',
}
for k in F:
    F[k] = F[k].split()


def text(s, ox, oy, fill):
    out, x0 = [], ox
    for ch in s.upper():
        g = F.get(ch, F[' '])
        for r, row in enumerate(g):
            c = 0
            while c < 5:
                if row[c] == '1':
                    n = 1
                    while c + n < 5 and row[c+n] == '1':
                        n += 1
                    out.append('<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>'
                               % ((x0+c)*PX, (oy+r)*PX, n*PX, PX, fill))
                    c += n
                else:
                    c += 1
        x0 += 6
    return ''.join(out)


def box(x, y, w, h, fill):
    return '<rect x="%d" y="%d" width="%d" height="%d" fill="%s"/>' % (x*PX, y*PX, w*PX, h*PX, fill)


def fetch():
    q = '''
    query($login:String!){ user(login:$login){
      followers{totalCount}
      contributionsCollection{ totalCommitContributions }
      repositories(first:100, ownerAffiliations:OWNER, isFork:false){
        totalCount
        nodes{ isPrivate stargazerCount
               languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{ name color } } } } }
    }}'''
    r = subprocess.run(['gh', 'api', 'graphql', '-f', 'query=' + q, '-f', 'login=' + USER],
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)['data']['user']


CARD, BORDER = '#1a0f2e', '#7e57c2'
LABEL, VALUE, TITLE, DIM = '#9d8ec4', '#e9dcff', '#d9c2f5', '#4a3168'

u = fetch()
repos = u['repositories']
priv = sum(1 for n in repos['nodes'] if n['isPrivate'])
rows = [('REPOS', str(repos['totalCount'])),
        ('PRIVATE', str(priv)),
        ('COMMITS YTD', str(u['contributionsCollection']['totalCommitContributions'])),
        ('FOLLOWERS', str(u['followers']['totalCount'])),
        ('STARS EARNED', str(sum(n['stargazerCount'] for n in repos['nodes'])))]

CW, PAD = 122, 5          # card width in font cells
def card(title, body_lines_h):
    return PAD*2 + 7 + 4 + 1 + 4 + body_lines_h

# ---- card 1: the numbers
STAMP = datetime.date.today().isoformat()
H1 = PAD*2 + 7 + 4 + 1 + 5 + len(rows)*11 - 3 + 11
p = [box(0, 0, CW, H1, CARD),
     '<rect x="0" y="0" width="%d" height="%d" fill="none" stroke="%s" stroke-width="%d"/>'
     % (CW*PX, H1*PX, BORDER, PX),
     text('GITHUB STATS', PAD, PAD, TITLE),
     box(PAD, PAD+10, CW-PAD*2, 1, DIM)]
y = PAD + 16
for k, v in rows:
    p.append(text(k, PAD, y, LABEL))
    p.append(text(v, CW - PAD - len(v)*6 + 1, y, VALUE))
    y += 11
p.append(box(PAD, y+1, CW-PAD*2, 1, DIM))
p.append(text('SNAPSHOT ' + STAMP, PAD, y+5, DIM))
card1 = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'shape-rendering="crispEdges" role="img" aria-label="GitHub stats">%s</svg>'
         % (CW*PX, H1*PX, CW*PX, H1*PX, ''.join(p)))

# ---- card 2: language bars
lang = Counter()
colors = {}
for n in repos['nodes']:
    for e in n['languages']['edges']:
        lang[e['node']['name']] += e['size']
        colors[e['node']['name']] = e['node']['color'] or '#8b7bb5'
tot = sum(lang.values()) or 1
top = lang.most_common(5)

NAMEW, PCTW = 10, 3
BARW = 122 - 5*2 - NAMEW*6 - PCTW*6 - 6
H2 = PAD*2 + 7 + 4 + 1 + 5 + len(top)*11 - 3 + 11
p = [box(0, 0, CW, H2, CARD),
     '<rect x="0" y="0" width="%d" height="%d" fill="none" stroke="%s" stroke-width="%d"/>'
     % (CW*PX, H2*PX, BORDER, PX),
     text('TOP LANGUAGES', PAD, PAD, TITLE),
     box(PAD, PAD+10, CW-PAD*2, 1, DIM)]
y = PAD + 16
for name, size in top:
    pct = size * 100.0 / tot
    label = name[:NAMEW]
    p.append(text(label, PAD, y, LABEL))
    bx = PAD + NAMEW*6 + 3
    p.append(box(bx, y+2, BARW, 4, DIM))
    filled = max(1, int(round(BARW * pct / 100.0)))
    p.append(box(bx, y+2, filled, 4, colors[name]))
    s = ('%d' % round(pct)).rjust(2) + '%'
    p.append(text(s, CW - PAD - len(s)*6 + 1, y, VALUE))
    y += 11
p.append(box(PAD, y+1, CW-PAD*2, 1, DIM))
p.append(text('SNAPSHOT ' + STAMP, PAD, y+5, DIM))
card2 = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
         'shape-rendering="crispEdges" role="img" aria-label="Top languages">%s</svg>'
         % (CW*PX, H2*PX, CW*PX, H2*PX, ''.join(p)))

open(os.path.join(OUT, 'stats-main.svg'), 'w', encoding='utf-8').write(card1)
open(os.path.join(OUT, 'stats-langs.svg'), 'w', encoding='utf-8').write(card2)
print('stats-main.svg   %dx%d  %.1f KB' % (CW*PX, H1*PX, len(card1)/1024))
print('stats-langs.svg  %dx%d  %.1f KB' % (CW*PX, H2*PX, len(card2)/1024))
print('data:', dict(rows), '| langs:', [(n, round(s*100.0/tot, 1)) for n, s in top])
