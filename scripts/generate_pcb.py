"""KiCad 10 Python: generate the unrouted wireless EC board from named nets.

Outline and clamp holes come from the MIT EC60 reference. Component placements
are initial candidates; native DRC and case clearance remain development gates.
"""
import csv
import json
from pathlib import Path
import pcbnew as p
from common import ROOT, SPEC, keys
from circuit import components, controller_components

LIB = Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints')
OUT = ROOT/'hardware'

def v(x,y): return p.VECTOR2I(p.FromMM(x),p.FromMM(y))

def main(controller=False, overwrite_routed=False):
    name='UnextendedEC-controller' if controller else 'UnextendedEC'
    target=OUT/(name+'.kicad_pcb')
    if target.exists() and list(p.LoadBoard(str(target)).GetTracks()) and not overwrite_routed:
        raise RuntimeError('Refusing to overwrite a routed PCB. Regenerate only in a disposable checkout with --overwrite-routed.')
    board=p.BOARD()
    board.SetCopperLayerCount(2 if controller else 4)
    board.GetDesignSettings().SetBoardThickness(p.FromMM(.8 if controller else 1.6))
    cs=controller_components() if controller else components()
    nets={}
    for name in sorted({n for c in cs for n in c['pins'].values() if n}):
        net=p.NETINFO_ITEM(board,name);board.Add(net);nets[name]=net
    for name in ['SPST_PIGTAIL_2.54','RESET_2.54_TH']:
        f=p.FOOTPRINT(None);f.SetFPID(p.LIB_ID('UnextendedEC',name))
        for i,x in [(1,-1.27),(2,1.27)]:
            a=p.PAD(f);a.SetNumber(str(i));a.SetPosition(v(x,0));a.SetSize(v(1.8,1.8));a.SetDrillSize(v(1,1))
            a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetAttribute(p.PAD_ATTRIB_PTH)
            ls=p.LSET(p.LSET.AllCuMask());ls.AddLayer(p.F_Mask);ls.AddLayer(p.B_Mask);a.SetLayerSet(ls);f.Add(a)
        p.FootprintSave(str(OUT/'UnextendedEC.pretty'),f)
    for c in cs:
        lib,name=c['footprint'].split(':')
        folder=OUT/'UnextendedEC.pretty' if lib=='UnextendedEC' else LIB/(lib+'.pretty')
        f=p.FootprintLoad(str(folder),name)
        if f is None: raise RuntimeError(c['footprint'])
        f.SetFPID(p.LIB_ID(lib,name));f.SetReference(c['ref']);f.SetValue(c['value'])
        if c['kind'] in ['MODULE','EC']: f.Models().clear()
        f.SetPosition(v(c['x'],c['y']));board.Add(f)
        if c['side']=='B': f.Flip(f.GetPosition(),False)
        if 'rotation' in c:f.SetOrientationDegrees(c['rotation'])
        if c['kind']=='MODULE':f.SetAttributes(f.GetAttributes() & ~p.FP_EXCLUDE_FROM_BOM)
        for a in f.Pads():
            net=c['pins'].get(a.GetNumber())
            if net:a.SetNet(nets[net])
        f.Value().SetVisible(False)
    ref=p.LoadBoard(str(OUT/'reference/EC60.kicad_pcb'))
    offset=v(-71.812704,-103.90966)
    clamps=[]
    for f in ([] if controller else ref.GetFootprints()):
        if '60_Outline-Modded' in str(f.GetFPID().GetLibItemName()):
            outline=p.FOOTPRINT(f);outline.Move(offset)
            for g in list(outline.GraphicalItems()):
                if g.GetLayer()!=p.Edge_Cuts:outline.Remove(g)
            outline.Reference().SetLayer(p.Dwgs_User);outline.Reference().SetVisible(False)
            outline.Value().SetVisible(False);board.Add(outline)
        elif f.GetReference().startswith('H'):
            hole=p.FOOTPRINT(f);hole.Move(offset)
            for a in hole.Pads():a.SetNetCode(0)
            board.Add(hole)
            for a in hole.Pads():
                if a.GetDrillSize().x:
                    pos=a.GetPosition()
                    clamps.append(dict(ref=f.GetReference(),x=p.ToMM(pos.x),y=p.ToMM(pos.y),diameter=p.ToMM(a.GetDrillSize().x)))
    if controller:
        for a,b in zip([(0,0),(24,0),(24,52),(0,52)],[(24,0),(24,52),(0,52),(0,0)]):
            s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*b));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));board.Add(s)
        z=p.ZONE(board);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask())
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        x1,y1,x2,y2=SPEC['module']['antenna_keepout']
        for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:poly.Append(p.FromMM(x),p.FromMM(y))
        board.Add(z)
        for x1,y1,x2,y2 in [(0,0,24,.6),(0,51.4,24,52),(0,.6,.6,51.4),(23.4,.6,24,51.4)]:
            z=p.ZONE(board);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask())
            z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
            poly=z.Outline();poly.NewOutline()
            for x,y in [(x1,y1),(x2,y1),(x2,y2),(x1,y2)]:poly.Append(p.FromMM(x),p.FromMM(y))
            board.Add(z)
        for i,(x,y) in enumerate([(1.5,1.5),(22.5,1.5),(1.5,44.5),(22.5,44.5)],1):
            f=p.FOOTPRINT(None);f.SetReference(f'MH{i}');f.Value().SetVisible(False);f.Reference().SetVisible(False)
            a=p.PAD(f);a.SetAttribute(p.PAD_ATTRIB_NPTH);a.SetShape(p.PAD_SHAPE_CIRCLE)
            a.SetSize(v(1.6,1.6));a.SetDrillSize(v(1.6,1.6));a.SetLayerSet(p.LSET(p.LSET.AllCuMask()))
            f.Add(a);f.SetPosition(v(x,y));board.Add(f)
    # Sensing PCB: preserve every EC electrode; no radio module or RF cut-out.
    if not controller:
        import math
        layers=p.LSET();layers.AddLayer(p.In1_Cu);layers.AddLayer(p.In2_Cu)
        for k in keys():
            z=p.ZONE(board);z.SetIsRuleArea(True);z.SetLayerSet(layers)
            z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
            poly=z.Outline();poly.NewOutline()
            for i in range(64):poly.Append(p.FromMM(k['x']+6*math.cos(i*math.pi/32)),p.FromMM(k['y']+6*math.sin(i*math.pi/32)))
            board.Add(z)
    text=p.PCB_TEXT(board);text.SetText('A2 DIRECT USB - NOT FOR FAB')
    text.SetPosition(v(12,37) if controller else v(142,68));text.SetLayer(p.Dwgs_User);text.SetMirrored(not controller);board.Add(text)
    name='UnextendedEC-controller' if controller else 'UnextendedEC'
    p.SaveBoard(str(OUT/(name+'.kicad_pcb')),board)
    p.ExportSpecctraDSN(board,str(OUT/(name+'.dsn')))
    if not controller:(ROOT/'design/clamp-holes.json').write_text(json.dumps(clamps,indent=2)+'\n')
    (OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "UnextendedEC")(type "KiCad")(uri "${KIPRJMOD}/UnextendedEC.pretty")(options "")(descr "Wireless EC prototype")))\n')
    (ROOT/('design/controller-circuit.json' if controller else 'design/circuit.json')).write_text(json.dumps(cs,indent=2)+'\n')
    with (OUT/('BOM-controller.csv' if controller else 'BOM.csv')).open('w') as stream:
        writer=csv.writer(stream,lineterminator='\n');writer.writerow(['Reference','Value','Footprint','Side','X_mm','Y_mm'])
        for c in cs:writer.writerow([c[k] for k in ['ref','value','footprint','side','x','y']])
    print(f'{len(cs)} components; {len(nets)} nets; {len(list(board.GetTracks()))} tracks')

if __name__=='__main__':
    import sys
    main('--controller' in sys.argv, '--overwrite-routed' in sys.argv)
