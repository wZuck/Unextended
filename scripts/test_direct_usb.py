"""A2 structural safety regressions, not an electrical hardware simulation."""
import csv,json,math,unittest
from common import ROOT,SPEC
from circuit import components,controller_components,FFC_PINS,module_pins
from specctra_session import routes

class DirectUSB(unittest.TestCase):
    def test_module_separated(self):
        self.assertFalse(any(c['kind']=='MODULE' for c in components()))
        nano=next(c for c in controller_components() if c['ref']=='U1')
        self.assertEqual(nano['rotation'],270);self.assertEqual(nano['pins'],module_pins())

    def test_interconnect_matches(self):
        a=next(c for c in components() if c['ref']=='J2')['pins']
        b=next(c for c in controller_components() if c['ref']=='J2')['pins']
        self.assertEqual(a,b);self.assertEqual(len(a),24)
        self.assertFalse({'SENSE','AMP_OUT','FB','VBUS','USB_DP','USB_DM'} & set(a.values()))
        self.assertEqual([a[str(i)] for i in (19,20,21)],['GND','ADC','GND'])

    def test_front_end_local(self):
        owners={}
        for c in components():
            for pin,net in c['pins'].items():owners.setdefault(net,set()).add((c['ref'],pin))
        self.assertEqual(owners['SENSE'],{('U2','3'),('U3','3'),('U4','3'),('R32','2'),('C4','1')})
        self.assertEqual(owners['AMP_OUT'],{('U4','6'),('R30','1'),('R37','1')})
        self.assertEqual(owners['ADC'],{('R37','2'),('J2','20')})

    def test_filter(self):
        resistor=next(c for c in components() if c['ref']=='R37')
        cap=next(c for c in controller_components() if c['ref']=='C6')
        self.assertEqual(resistor['value'],'47');self.assertEqual(cap['value'],'1n_C0G')
        self.assertEqual(cap['pins'],{'1':'ADC','2':'GND'})
        self.assertLess(math.dist((183,84),(170,84)),20)

    def test_native_adc_mapping(self):
        rows=list(csv.DictReader((ROOT/'design/pin-map.csv').open()))
        adc=next(r for r in rows if r['Signal']=='ADC')
        self.assertEqual((adc['Controller_U1_pad'],adc['J2_FFC_pin']),('18','20'))
        self.assertEqual(FFC_PINS[22],'BAT_SW')

    def test_mechanical_envelope_gate(self):
        r=json.loads((ROOT/'reports/direct-usb-mechanical.json').read_text())
        self.assertLess(r['nominal_port_alignment_error_mm'],1e-4)
        self.assertTrue(r['case_internal_pocket_modified'])
        self.assertFalse(r['internal_usb_extension']);self.assertFalse(r['module_on_sensing_pcb'])
        self.assertTrue(any(v['original_case_mm3']>1 for v in r['collisions'].values()))
        self.assertTrue(all(v['modified_case_mm3']<1e-5 for v in r['collisions'].values()))
        self.assertGreaterEqual(len(r['limitations']),4)

    def test_route_only_parser(self):
        for layers in ('0-1','0-3'):
            text='''(session X (routes (resolution um 10)
             (library_out (padstack "Via[%s]_600:300_um" (shape (circle F.Cu 6000 0 0))))
             (network_out (net ROW1 (wire (path B.Cu 2000 10000 -20000 30000 -40000))
               (via "Via[%s]_600:300_um" 30000 -40000)))))'''%(layers,layers)
            result=routes(text);self.assertEqual(result[0]['net'],'ROW1')
            self.assertEqual(result[0]['a'],(1,2));self.assertEqual(result[0]['b'],(3,4))
            self.assertEqual(result[0]['width'],.2);self.assertEqual(result[1]['drill'],.3)

if __name__=='__main__':
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(DirectUSB)
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    (ROOT/'reports/direct-usb-regression.json').write_text(json.dumps({'tests':result.testsRun,'passed':result.wasSuccessful(),
        'scope':'Structural net partition, pin map, RC placement, nominal geometry and SES parsing only; no physical electrical test'},indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
