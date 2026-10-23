"""KiCad: escape real EC electrodes, route a simplified DSN, verify natively.

The proxy is never a fabrication artifact. Each proxy PTH corresponds to an
actual via connected to the original custom electrode by a fixed copper stub.
Native geometry and the pre-route seed are retained for session import/DRC.
"""
import math
import pcbnew as p
from common import ROOT, keys

def v(x, y): return p.VECTOR2I(p.FromMM(x), p.FromMM(y))

def main():
    native = p.LoadBoard(str(ROOT/'hardware/UnextendedEC.kicad_pcb'))
    assert not list(native.GetTracks()), 'Start from generate_pcb.py; do not overwrite routed work'
    footprints = {f.GetReference(): f for f in native.GetFootprints()}
    escapes = {}
    for k in keys():
        f = footprints[k['ref']]
        x, y = k['x'], k['y']
        destinations = {'1': (x-6.6, y), '2': (x+6.6, y), '3': (x, y+7.8)}
        if k['ref']=='EC8':destinations['3']=(x,y-7.8)
        # Escape away from the inherited center mounting hole and bottom ICs.
        if k['ref']=='EC34':destinations['2']=(x+5.5,y-3.8)
        if k['ref']=='EC35':destinations['1']=(x-5.5,y-3.8)
        if k['row']==4 and k['col']==10:destinations['2']=(x+6.6,y-4)
        if k['row']==4 and k['col']==11:destinations['1']=(x-5,y-5)
        pads = {a.GetNumber(): a for a in f.Pads()}
        for number, (dx,dy) in destinations.items():
            net = pads[number].GetNetCode()
            via = p.PCB_VIA(native); via.SetPosition(v(dx,dy)); via.SetWidth(p.FromMM(.6))
            via.SetDrill(p.FromMM(.3)); via.SetViaType(p.VIATYPE_THROUGH)
            via.SetLayerPair(p.F_Cu,p.B_Cu); via.SetNetCode(net); native.Add(via)
            direction=-1 if dy<y else 1
            starts = [(x-1,y,p.F_Cu)] if number=='1' else [(x+1,y,p.F_Cu)] if number=='2' else [(x,y+direction*6.5,p.F_Cu),(x,y+direction*6.2,p.B_Cu)]
            for sx,sy,layer in starts:
                track=p.PCB_TRACK(native);track.SetStart(v(sx,sy));track.SetEnd(v(dx,dy))
                track.SetWidth(p.FromMM(.15));track.SetLayer(layer);track.SetNetCode(net);native.Add(track)
        escapes[k['ref']]=destinations
    p.SaveBoard(str(ROOT/'hardware/UnextendedEC-escape-seed.kicad_pcb'),native)
    proxy=p.BOARD();proxy.SetCopperLayerCount(4)
    proxy.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
    netcodes={}
    for net in native.GetNetsByNetcode().values():
        if not net.GetNetname():continue
        clone=p.NETINFO_ITEM(proxy,net.GetNetname());proxy.Add(clone);netcodes[net.GetNetCode()]=clone
    for old in native.GetFootprints():
        if old.GetReference() not in escapes:
            f=p.FOOTPRINT(old);proxy.Add(f)
            for a in f.Pads():
                if a.GetNetCode() in netcodes:a.SetNet(netcodes[a.GetNetCode()])
            continue
        f=p.FOOTPRINT(proxy);f.SetFPID(old.GetFPID());f.SetReference(old.GetReference());f.SetPosition(old.GetPosition());proxy.Add(f)
        nets={a.GetNumber():a.GetNetCode() for a in old.Pads()}
        for number,(dx,dy) in escapes[f.GetReference()].items():
            a=p.PAD(f);a.SetNumber(number);a.SetPosition(v(dx,dy));a.SetSize(v(.6,.6));a.SetDrillSize(v(.3,.3))
            a.SetShape(p.PAD_SHAPE_CIRCLE);a.SetAttribute(p.PAD_ATTRIB_PTH)
            a.SetLayerSet(p.LSET(p.LSET.AllCuMask()));a.SetNet(netcodes[nets[number]]);f.Add(a)
        # Prevent the router crossing the actual electrode or its escape stub.
        z=p.ZONE(proxy);z.SetIsRuleArea(True);layers=p.LSET();layers.AddLayer(p.F_Cu);z.SetLayerSet(layers)
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        x,y=p.ToMM(f.GetPosition().x),p.ToMM(f.GetPosition().y)
        for i in range(48):poly.Append(p.FromMM(x+6.15*math.cos(i*math.pi/24)),p.FromMM(y+6.15*math.sin(i*math.pi/24)))
        proxy.Add(z)
        # The real cell includes a narrow B.Cu ground guard, absent from the
        # simplified PTH representation. Preserve its occupied copper corridor.
        z=p.ZONE(proxy);z.SetIsRuleArea(True);layers=p.LSET();layers.AddLayer(p.B_Cu);z.SetLayerSet(layers)
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        lower=6.75 if old.GetReference()=='EC8' else 7.25
        upper=-7.25 if old.GetReference()=='EC8' else -6.75
        for dx,dy in [(-.25,upper),(.25,upper),(.25,lower),(-.25,lower)]:poly.Append(p.FromMM(x+dx),p.FromMM(y+dy))
        proxy.Add(z)
        z=p.ZONE(proxy);z.SetIsRuleArea(True);layers=p.LSET();layers.AddLayer(p.F_Cu);z.SetLayerSet(layers)
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        for dx,dy in [(-.25,-7.25),(.25,-7.25),(.25,7.25),(-.25,7.25)]:poly.Append(p.FromMM(x+dx),p.FromMM(y+dy))
        proxy.Add(z)
    for d in native.GetDrawings():proxy.Add(d.Duplicate())
    for z in native.Zones():proxy.Add(p.ZONE(z))
    for f in native.GetFootprints():
        if not (f.GetReference().startswith('H') or f.GetReference()=='REF**'):continue
        for pad in f.Pads():
            drill=p.ToMM(pad.GetDrillSize().x)
            if not drill:continue
            clearance=p.ToMM(pad.GetLocalClearance() or p.FromMM(.2))
            radius=drill/2+clearance+.05
            x,y=p.ToMM(pad.GetPosition().x),p.ToMM(pad.GetPosition().y)
            z=p.ZONE(proxy);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask())
            z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
            poly=z.Outline();poly.NewOutline()
            for i in range(32):poly.Append(p.FromMM(x+radius*math.cos(i*math.pi/16)),p.FromMM(y+radius*math.sin(i*math.pi/16)))
            proxy.Add(z)
    # Freerouting's default edge spacing is smaller than the native project's
    # 0.5 mm gate. Sweep a conservative 0.6 mm collar around actual Edge.Cuts.
    def collar(a,b):
        theta=math.atan2(b[1]-a[1],b[0]-a[0]);points=[]
        for center,start in [(a,theta+math.pi/2),(b,theta-math.pi/2)]:
            for i in range(7):points.append((center[0]+.6*math.cos(start+i*math.pi/6),center[1]+.6*math.sin(start+i*math.pi/6)))
        z=p.ZONE(proxy);z.SetIsRuleArea(True);z.SetLayerSet(p.LSET.AllCuMask())
        z.SetDoNotAllowTracks(True);z.SetDoNotAllowVias(True);z.SetDoNotAllowZoneFills(True)
        poly=z.Outline();poly.NewOutline()
        for x,y in points:poly.Append(p.FromMM(x),p.FromMM(y))
        proxy.Add(z)
    edges=[s for f in native.GetFootprints() for s in f.GraphicalItems() if s.GetLayer()==p.Edge_Cuts]
    for edge in edges:
        start=(p.ToMM(edge.GetStart().x),p.ToMM(edge.GetStart().y));end=(p.ToMM(edge.GetEnd().x),p.ToMM(edge.GetEnd().y))
        if edge.GetShape()==p.SHAPE_T_SEGMENT:collar(start,end)
        elif edge.GetShape()==p.SHAPE_T_ARC:
            center=(p.ToMM(edge.GetCenter().x),p.ToMM(edge.GetCenter().y));radius=math.dist(start,center)
            angle=math.atan2(start[1]-center[1],start[0]-center[0]);sweep=edge.GetArcAngle().AsRadians()
            if math.dist((center[0]+radius*math.cos(angle+sweep),center[1]+radius*math.sin(angle+sweep)),end)>.01:sweep=-sweep
            count=max(2,math.ceil(abs(sweep)*radius/.4))
            points=[(center[0]+radius*math.cos(angle+sweep*i/count),center[1]+radius*math.sin(angle+sweep*i/count)) for i in range(count+1)]
            for a,b in zip(points,points[1:]):collar(a,b)
        else:raise ValueError('Unsupported board edge geometry')
    p.SaveBoard(str(ROOT/'hardware/UnextendedEC-routing-proxy.kicad_pcb'),proxy)
    assert p.ExportSpecctraDSN(proxy,str(ROOT/'hardware/UnextendedEC-routing-proxy.dsn'))
    print('Prepared 183 real escape vias and compact routing proxy; native seed requires DRC')

if __name__=='__main__':main()
