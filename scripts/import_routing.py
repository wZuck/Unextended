"""KiCad Python: import a Specctra session, then run native DRC separately."""
import sys
import pcbnew as p
from common import ROOT
name=sys.argv[1]
assert name in ['UnextendedEC','UnextendedEC-controller']
path=ROOT/f'hardware/{name}.kicad_pcb'
b=p.LoadBoard(str(path))
assert not list(b.GetTracks()), 'Refusing to overlay routing on existing tracks'
proxy='--proxy' in sys.argv
session='UnextendedEC-routing-proxy' if proxy else name
if '--session' in sys.argv:
    session=sys.argv[sys.argv.index('--session')+1]
    assert session.startswith('UnextendedEC') and '/' not in session
session_path=ROOT/f'hardware/{session}.ses'
if True:  # Import named routes only; retain authoritative native placements.
    from specctra_session import routes
    layers={'F.Cu':p.F_Cu,'In1.Cu':p.In1_Cu,'In2.Cu':p.In2_Cu,'B.Cu':p.B_Cu}
    def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
    for item in routes(session_path.read_text()):
        if item['kind']=='via':
            t=p.PCB_VIA(b);t.SetPosition(v(item['x'],item['y']));t.SetWidth(p.FromMM(item['diameter']))
            t.SetDrill(p.FromMM(item['drill']));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(p.F_Cu,p.B_Cu)
        else:
            t=p.PCB_TRACK(b);t.SetStart(v(*item['a']));t.SetEnd(v(*item['b']))
            # Widen any router neckdown to the native project's 0.15 mm limit;
            # final native DRC, not the proxy score, determines acceptance.
            t.SetWidth(p.FromMM(max(.15,item['width'])));t.SetLayer(layers[item['layer']])
        net=b.FindNet(item['net']);assert net and net.GetNetname()==item['net'];t.SetNet(net);b.Add(t)
if proxy:
    assert name=='UnextendedEC'
    seed=p.LoadBoard(str(ROOT/'hardware/UnextendedEC-escape-seed.kicad_pcb'))
    for t in seed.GetTracks():
        if isinstance(t,p.PCB_VIA):
            clone=p.PCB_VIA(b);clone.SetPosition(t.GetPosition());clone.SetWidth(t.GetWidth(p.F_Cu))
            clone.SetDrill(t.GetDrillValue());clone.SetViaType(t.GetViaType());clone.SetLayerPair(t.TopLayer(),t.BottomLayer())
        else:
            clone=p.PCB_TRACK(b);clone.SetStart(t.GetStart());clone.SetEnd(t.GetEnd())
            clone.SetWidth(t.GetWidth());clone.SetLayer(t.GetLayer())
        clone.SetNet(b.FindNet(t.GetNetname()));b.Add(clone)
    path=ROOT/'hardware/UnextendedEC-routed-candidate.kicad_pcb'
p.SaveBoard(str(path),b)
print(name,len(list(b.GetTracks())),'tracks/vias')
