"""Verify built transports and package both UF2 files with source hashes."""
import argparse,hashlib,json,shutil
from common import ROOT

def main(workspace):
    output=ROOT/'firmware/prebuilt';output.mkdir(exist_ok=True);records={}
    for suffix in ['', '-calibrator']:
        source=workspace/f'build/unextended_ec{suffix}/zephyr';conf=(source/'.config').read_text()
        for option in ['CONFIG_ZMK_USB=y','CONFIG_ZMK_BLE=y','CONFIG_BT=y','CONFIG_USB_DEVICE_STACK=y']:
            assert option in conf, option
        assert 'CONFIG_ZMK_SLEEP=y' not in conf
        assert ('CONFIG_ZMK_KSCAN_EC_MATRIX_CALIBRATOR=y' in conf)==bool(suffix)
        name=f'unextended-ec{suffix}.uf2';target=output/name
        shutil.copyfile(source/'zmk.uf2',target);assert target.read_bytes()[:4]==b'UF2\n'
        records[name]={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,'hardware_tested':False}
    (output/'SHA256SUMS').write_text(''.join(f'{r["sha256"]}  {name}\n' for name,r in records.items()))
    files=sorted((ROOT/'firmware/config').rglob('*'))+[ROOT/'firmware/patches/manifest.json']
    report={'target':'nice_nano@2.0.0/nrf52840/zmk','images':records,
            'sources':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files if f.is_file()}}
    (ROOT/'reports/firmware-build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(records,indent=2))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workspace',required=True,type=__import__('pathlib').Path)
    main(parser.parse_args().workspace)
