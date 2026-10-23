"""Tessellate real V1 case and parametric keycap envelopes for concept renders.

The display transform is provisional, not an assembly-clearance result.
"""
import json,math
import cadquery as cq
from common import ROOT,keys

def main():
    out=ROOT/'mechanical/render';out.mkdir(parents=True,exist_ok=True)
    case=cq.importers.importStep(str(ROOT/'mechanical/reference/Unextended_V1_220331.step'))
    cq.exporters.export(case,str(out/'case.stl'),tolerance=.08,angularTolerance=.15)
    caps=[]
    for k in keys():
        w=k['width']*19.05-.9
        bottom=cq.Workplane('XY').sketch().rect(w,18.15).vertices().fillet(1).finalize().extrude(.01).faces('<Z').wires().val()
        top=cq.Workplane('XY').sketch().rect(w-3.3,14.85).vertices().fillet(1.5).finalize().extrude(.01).faces('<Z').wires().translate((0,0,7)).val()
        cap=cq.Workplane('XY').newObject([cq.Solid.makeLoft([bottom,top])]).translate((k['x'],k['y'],10.8))
        cap=cap.mirror('XZ').rotate((0,0,0),(1,0,0),5.4).translate((-142.5,43.7,27.8))
        path=out/(k['ref']+'.stl');cq.exporters.export(cap,str(path),tolerance=.08,angularTolerance=.2)
        angle=math.radians(5.4);y=-k['y']*math.cos(angle)-17.9*math.sin(angle)+43.7;z=-k['y']*math.sin(angle)+17.9*math.cos(angle)+27.8
        caps.append(dict(ref=k['ref'],label=k['label'],x=k['x']-142.5,y=y,z=z))
    (out/'caps.json').write_text(json.dumps(caps,indent=2)+'\n')
    print('Real V1 case + 61 envelope keycaps; display transform only')

if __name__=='__main__':main()
