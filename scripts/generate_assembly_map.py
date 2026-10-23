"""Component-center diagram, explicitly mirrored bottom view (not pad artwork)."""
from html import escape
from common import ROOT, SPEC, keys
from circuit import components

def main():
    out=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1140 520">',
         '<rect width="1140" height="520" fill="#f5f5ed"/>',
         '<style>text{font-family:monospace;fill:#22392b} .label{font-size:9px} .key{fill:none;stroke:#c7cfc1;stroke-width:.5}</style>',
         '<text x="24" y="28" font-size="18">UNEXTENDED EC / A2 — SENSING PCB BOTTOM VIEW</text>',
         '<text x="24" y="48" font-size="11">MIRRORED component centers · UNROUTED · not a pad/orientation or fabrication drawing</text>']
    def pt(x,y):return 30+(285-x)*3.78,70+y*3.78
    def rect(x,y,w,h,color,stroke='none'):
        a,b=pt(x+w,y);out.append(f'<rect x="{a:.2f}" y="{b:.2f}" width="{w*3.78:.2f}" height="{h*3.78:.2f}" fill="{color}" stroke="{stroke}"/>')
    rect(0,0,285,94.6,'#e0e8d7','#66745f')
    for k in keys():
        x,y=pt(k['x'],k['y']);out.append(f'<circle class="key" cx="{x:.2f}" cy="{y:.2f}" r="22.7"/>')
    for c in components():
        if c['kind']=='EC':continue
        x,y=pt(c['x'],c['y']);large=c['ref'].startswith(('U','J','Q','SW'))
        out.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{5 if large else 2}" fill="{ "#294c36" if large else "#688b57"}"/>')
        dy=-9 if large else (-4 if int(c['ref'][1:])%2 else 10)
        out.append(f'<text class="label" x="{x+4:.2f}" y="{y+dy:.2f}">{escape(c["ref"])}</text>')
    out.extend(['<text x="24" y="458" font-size="12">J2 carrier interconnect | U2/U3 mux | U4 amplifier | R37 output isolation | J1 battery</text>',
                '<text x="24" y="480" font-size="11">No nano beneath spacebar. Native nano USB-C is exposed in the separate low-level case bay.</text>',
                '<text x="24" y="500" font-size="11">Coordinates originate at PCB top-left in TOP view. Use native KiCad for exact pad numbers and orientation.</text></svg>'])
    (ROOT/'renders/assembly-bottom.svg').write_text('\n'.join(out)+'\n')

if __name__=='__main__':main()
