"""Export NIZ plate and fit coupon; candidate dimensions, not production approval."""
import json
import cadquery as cq
from common import ROOT,SPEC,keys

def rect(w,h,r,z,t):
    return cq.Workplane('XY').sketch().rect(w,h).vertices().fillet(r).finalize().extrude(t).translate((0,0,z))

def main():
    w,h=SPEC['pcb']['width'],SPEC['pcb']['height']
    z=SPEC['plate']['pcb_top_to_plate_bottom'];t=SPEC['plate']['thickness']
    plate=rect(w,h,2,z,t).translate((w/2,h/2,0))
    holes=json.loads((ROOT/'design/clamp-holes.json').read_text())
    for k in keys():
        plate=plate.cut(rect(14,14,.5,z-1,t+2).translate((k['x'],k['y'],0)))
        if k['width']>=2:
            d=50 if k['width']==6.25 else 11.90625
            for x in [k['x']-d,k['x']+d]:
                cut=cq.Workplane('XY').box(6.75,12.3,t+2).translate((x,k['y'],z+t/2))
                latch=cq.Workplane('XY').box(3.3,1.2,t+2).translate((x,k['y']+6.75,z+t/2))
                plate=plate.cut(cut).cut(latch)
    for a in holes:
        plate=plate.cut(cq.Workplane('XY').center(a['x'],a['y']).circle(1.1).extrude(t+2).translate((0,0,z-1)))
    # Radio has moved to the low USB bay. Do not cut an obsolete RF window
    # through the spacebar stabilizer region of the sensing assembly.
    coupon=rect(85,32,2,0,t).translate((42.5,16,0))
    for x,s in [(12,13.9),(34,14),(56,14.1)]:
        coupon=coupon.cut(rect(s,s,.5,-1,t+2).translate((x,15,0)))
    coupon=coupon.cut(cq.Workplane('XY').box(6.75,12.3,t+2).translate((76,15,t/2)))
    coupon=coupon.cut(cq.Workplane('XY').box(3.3,1.2,t+2).translate((76,21.75,t/2)))
    report={'status':'CANDIDATE; housing latch, stabs, preload and V1 fit require actual checks',
            'clamp_holes':len(holes),'keys':len(keys()),'plate_bottom_above_pcb_top_mm':z}
    for name,obj in [('niz-ansi-plate',plate),('niz-fit-coupon',coupon)]:
        shape=obj.val();assert shape.isValid();assert len(shape.Solids())==1
        cq.exporters.export(obj,str(ROOT/f'mechanical/{name}.step'))
        cq.exporters.export(obj.faces('<Z').wires(),str(ROOT/f'mechanical/{name}.dxf'))
        report[name]={'valid':True,'solids':len(shape.Solids()),'volume_mm3':shape.Volume()}
    # Record the real model without guessing a PCB-to-case assembly transform.
    case=cq.importers.importStep(str(ROOT/'mechanical/reference/Unextended_V1_220331.step')).val()
    b=case.BoundingBox()
    report['upstream_case']={'valid':case.isValid(),'solids':len(case.Solids()),
        'bounds_mm':[getattr(b,n) for n in ['xmin','ymin','zmin','xmax','ymax','zmax']],
        'assembly_alignment_verified':False}
    (ROOT/'reports/mechanical.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
