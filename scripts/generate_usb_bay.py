"""A2: direct native USB-C in the actual V1 port, with a lowered carrier.

This is an envelope-level mechanical design, not a manufacturer module STEP
or an EMI qualification. The sensing assembly's Z datum remains provisional.
"""
import hashlib,json,math
import cadquery as cq
from common import ROOT,SPEC

def box(w,d,h,x,y,z):
    return cq.Workplane('XY').box(w,d,h).translate((x,y,z)).val()

def main():
    path=ROOT/'mechanical/reference/Unextended_V1_220331.step'
    case=cq.importers.importStep(str(path)).val();module=SPEC['module'];placement=module['carrier_to_case']
    candidates=[]
    for face in case.Faces():
        bb=face.BoundingBox()
        if face.geomType()=='PLANE' and bb.ylen<1e-5 and 50<bb.ymin<51 and bb.xlen>250:
            for wire in face.innerWires():
                b=wire.BoundingBox()
                if 10<b.xlen<20 and 5<b.zlen<10:candidates.append(b)
    assert len(candidates)==1,'Could not uniquely identify actual V1 USB opening'
    opening=candidates[0];mouth=[(opening.xmin+opening.xmax)/2,opening.ymin,(opening.zmin+opening.zmax)/2]
    assert max(abs(a-b) for a,b in zip(mouth,module['case_usb_mouth_center']))<1e-4
    ox,oy,top=placement['x_offset'],placement['y_origin'],placement['pcb_top_z']
    def world(shape):return shape.mirror('XZ').translate((ox,oy,top))
    carrier=box(24,52,.8,12,26,-.4)
    mounts=[(1.5,1.5),(22.5,1.5),(1.5,44.5),(22.5,44.5)]
    for x,y in mounts:carrier=carrier.cut(cq.Solid.makeCylinder(.8,2,cq.Vector(x,y,-1)))
    # Footprint has body x=-17.78..15.24 before rotation; USB face x=-19.304.
    body=box(17.78,33.02,3.2,12,16.73,module['module_pcb_midplane_z']-top)
    socket=box(9,5.08,3.2,11.873,1.236,module['module_pcb_midplane_z']-top)
    connector=box(17.8,4,2,12,48.5,1)
    capacitor=box(2,1.25,.9,12,24,-1.25)
    parts={'carrier':world(carrier),'module_envelope':world(body.fuse(socket)),
           'ffc_connector':world(connector),'adc_capacitor':world(capacitor)}
    # Widen/extend only the internal low pocket; retain the external USB opening.
    # Explicit world extents: x=ox-.3..ox+24.3, y=oy-52.3..oy+.3.
    pocket=box(24.6,52.6,10,12+ox,oy-26,7.8)
    modified=case.cut(pocket)
    for x,y in mounts:
        wx,wy=x+ox,oy-y
        boss=cq.Solid.makeCylinder(1.4,2.1545,cq.Vector(wx,wy,2))
        modified=modified.fuse(boss)
        pilot=cq.Solid.makeCylinder(.525,2.5,cq.Vector(wx,wy,1.6545))
        modified=modified.cut(pilot)
    assert modified.isValid() and len(modified.Solids())==1
    plug=box(12,16,6,mouth[0],mouth[1]+8,mouth[2])
    parts['external_plug_envelope']=plug
    collisions={name:{'original_case_mm3':case.intersect(shape).Volume(),
                      'modified_case_mm3':modified.intersect(shape).Volume()} for name,shape in parts.items()}
    assert all(v['modified_case_mm3']<1e-5 for v in collisions.values()),collisions
    native_mouth=[11.873+ox,oy+1.304,module['module_pcb_midplane_z']]
    assert max(abs(a-b) for a,b in zip(native_mouth,mouth))<1e-4
    rf=world(box(12,18,12,12,35,8))
    rf_overlap=modified.intersect(rf).Volume()
    assembly=cq.Assembly(name='UnextendedEC_A2_direct_USB')
    assembly.add(modified,name='modified_PC_V1_case',color=cq.Color(.65,.7,.68,.35))
    for name,shape in parts.items():assembly.add(shape,name=name,color=cq.Color(.2,.45,.3) if name=='carrier' else cq.Color(.45,.45,.45))
    assembly.save(str(ROOT/'mechanical/direct-usb-assembly.step'))
    cq.exporters.export(modified,str(ROOT/'mechanical/Unextended_V1_EC_direct_USB.step'))
    cq.exporters.export(carrier,str(ROOT/'mechanical/usb-carrier-envelope.step'))
    render=ROOT/'mechanical/usb-render';render.mkdir(exist_ok=True)
    cutaway=modified.intersect(box(400,200,13,0,0,6.5))
    cq.exporters.export(cutaway,str(render/'case-cutaway.stl'),tolerance=.06,angularTolerance=.15)
    for name,shape in parts.items():cq.exporters.export(shape,str(render/(name+'.stl')),tolerance=.05,angularTolerance=.15)
    report={'revision':SPEC['revision'],'case_reference_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'actual_case_usb_opening_center_mm':mouth,'native_module_usb_mouth_mm':native_mouth,
            'nominal_port_alignment_error_mm':max(abs(a-b) for a,b in zip(mouth,native_mouth)),
            'internal_usb_extension':False,'usb_daughterboard':False,'module_on_sensing_pcb':False,
            'carrier_pcb_mm':[24,52,.8],'collisions':collisions,'rf_volume_case_overlap_mm3':rf_overlap,
            'case_internal_pocket_modified':True,'minimum_pocket_floor_z_mm':2.8,
            'mounting':'Four M1.4 plastic-thread-forming screws, head diameter <=2.5 mm, PCB holes 1.6 mm; pilot/retention must be prototyped',
            'limitations':['Module envelope uses footprint geometry and nominal 3.2 mm total thickness, not a vendor STEP',
                          'Actual USB socket-to-PCB offset, plug tolerance, mount retention and board stack height require measurements',
                          'PC non-metallized case required; conductive version needs separate RF design',
                          'No physical EC noise, BLE, charging or latency test has been performed']}
    (ROOT/'reports/direct-usb-mechanical.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
