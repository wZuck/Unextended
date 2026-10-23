"""Shared UnextendedEC dimensions; PCB top z=0, x right, y toward typist."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SPEC = json.loads((ROOT / "design/unextended_ec.json").read_text())
def keys():
    result=[]
    for row in SPEC['rows']:
        for x,width,label in row['keys']:
            result.append(dict(ref=f'EC{len(result)+1}', row=row['y'], col=int(x+width/2),
                u=x,width=width,label=label,
                x=SPEC['pcb']['first_center'][0]+(x+width/2-.5)*SPEC['pitch'],
                y=SPEC['pcb']['first_center'][1]+row['y']*SPEC['pitch']))
    return result
