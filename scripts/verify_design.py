"""KiCad Python: cross-check firmware, two schematics and native PCBs."""
import json,re,xml.etree.ElementTree as ET
import pcbnew as p
from common import ROOT,keys
from circuit import components,controller_components,FFC_PINS,module_pins

def main():
    ks=keys();assert len(ks)==61;assert len({(k['row'],k['col']) for k in ks})==61
    overlay=(ROOT/'firmware/config/boards/shields/unextended_ec/unextended_ec.overlay').read_text()
    mapping=[tuple(map(int,m)) for m in re.findall(r'RC\((\d+),(\d+)\)',overlay)]
    assert mapping==[(k['row'],k['col']) for k in ks]
    masks=[int(n,0) for n in re.search(r'strobe-input-masks = <([^>]+)>',overlay)[1].split()]
    for r in range(5):assert masks[r]==sum(1<<c for c in range(15) if (r,c) not in mapping)
    boards={}
    for name,cs,netfile in [('UnextendedEC',components(),'schematic.net.xml'),('UnextendedEC-controller',controller_components(),'controller.net.xml')]:
        b=p.LoadBoard(str(ROOT/f'hardware/{name}.kicad_pcb'));footprints={f.GetReference():f for f in b.GetFootprints()};native={}
        netroot=ET.parse(ROOT/f'reports/{netfile}')
        schematic_footprints={c.attrib['ref']:c.findtext('footprint') for c in netroot.findall('./components/comp')}
        for n in netroot.findall('./nets/net'):
            if n.attrib['name'].startswith('unconnected-'):continue
            for node in n.findall('node'):native[(node.attrib['ref'],node.attrib['pin'])]=n.attrib['name']
        for c in cs:
            f=footprints[c['ref']];pads={a.GetNumber():a for a in f.Pads()}
            assert schematic_footprints[c['ref']]==c['footprint'],(name,c['ref'],'schematic footprint drift')
            assert abs(p.ToMM(f.GetPosition().x)-c['x'])<1e-6
            assert abs(p.ToMM(f.GetPosition().y)-c['y'])<1e-6
            for num,net in c['pins'].items():
                if not net:continue
                assert str(pads[num].GetNetname())==net,(name,c['ref'],num,net)
                assert native[(c['ref'],num)]==net,(name,c['ref'],num,net)
        boards[name]={'components':len(cs),'tracks':len(list(b.GetTracks())),'schematic_pcb_net_parity':True,'copper_layers':b.GetCopperLayerCount()}
    main_j2=next(c for c in components() if c['ref']=='J2')['pins']
    carrier_j2=next(c for c in controller_components() if c['ref']=='J2')['pins']
    assert main_j2==carrier_j2=={str(k):v for k,v in FFC_PINS.items()}
    assert not {'SENSE','USB_DP','USB_DM','VBUS'} & set(main_j2.values())
    assert FFC_PINS[19]==FFC_PINS[21]=='GND' and FFC_PINS[20]=='ADC'
    assert not any(c['kind']=='MODULE' for c in components())
    assert next(c for c in controller_components() if c['ref']=='U1')['pins']==module_pins()
    assert next(c for c in components() if c['ref']=='U4')['pins']['6']=='AMP_OUT'
    assert next(c for c in components() if c['ref']=='R37')['pins']=={'1':'AMP_OUT','2':'ADC'}
    report={'key_count':61,'matrix_masks':[hex(n) for n in masks],'firmware_transform_matches':True,
            'architecture':'Low USB-bay carrier; native nice!nano USB-C directly external',
            'j2_pin_parity':True,'adc_ground_guards':[19,21],'high_impedance_sense_leaves_mainboard':False,
            'usb_extension':False,'module_on_sensing_pcb':False,'boards':boards,
            'fabrication_ready':False,'reason':'Physical EC/noise, RF, charging, retention and final sensing-stack assembly untested; no fabrication release'}
    (ROOT/'reports/design-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':main()
