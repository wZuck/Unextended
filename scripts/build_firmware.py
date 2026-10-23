"""Run inside the pinned ZMK build container with the west workspace as cwd.

Initialize an empty workspace with `west init -l config && west update` first.
The configuration should use firmware/west-lock.yml as config/west.yml.
"""
import argparse,subprocess
from pathlib import Path
from prepare_firmware import prepare

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--workspace',type=Path,required=True)
args=parser.parse_args();workspace=args.workspace.resolve()
prepare(workspace)
for suffix,snippets in [('',[]),('-calibrator',['-S','enable_ec_calibrator'])]:
    subprocess.run(['west','build','-p','always','-s','zmk/app','-d',f'build/unextended_ec{suffix}',
        '-b','nice_nano@2.0.0/nrf52840/zmk',*snippets,'--',
        f'-DZephyr_DIR={workspace}/zephyr/share/zephyr-package/cmake',
        f'-DZMK_CONFIG={workspace}/config','-DSHIELD=unextended_ec'],cwd=workspace,check=True)
