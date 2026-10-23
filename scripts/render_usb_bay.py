"""Blender engineering cutaway of the actual modified V1 and module envelopes."""
import bpy,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];GEO=ROOT/'mechanical/usb-render'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def mat(name,color,metal=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=.4
    return m
materials={'case-cutaway':mat('PC case cut at world Z13',(.48,.55,.49)),
           'carrier':mat('carrier PCB',(.035,.16,.08)),
           'module_envelope':mat('nano mechanical envelope',(.09,.11,.1)),
           'ffc_connector':mat('FFC connector',(.67,.66,.51)),
           'adc_capacitor':mat('ADC capacitor',(.5,.33,.16)),
           'external_plug_envelope':mat('external USB plug envelope',(.61,.73,.12))}
for name,material in materials.items():
    bpy.ops.wm.stl_import(filepath=str(GEO/(name+'.stl')));o=bpy.context.object;o.data.materials.append(material)
    bevel=o.modifiers.new('small edges','BEVEL');bevel.width=.1;bevel.segments=2
world=bpy.context.scene.world;world.color=(.45,.45,.45)
for name,loc in [('Key',(-40,100,120)),('Fill',(60,0,70))]:
    d=bpy.data.lights.new(name,'AREA');d.energy=300000;d.shape='DISK';d.size=90
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector((0,25,4))-o.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.cameras.new('Camera');o=bpy.data.objects.new('Camera',cam);bpy.context.collection.objects.link(o)
o.location=(65,110,100);o.rotation_euler=(Vector((0,25,5))-o.location).to_track_quat('-Z','Y').to_euler();cam.type='ORTHO';cam.ortho_scale=95
scene=bpy.context.scene;scene.camera=o;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1440;scene.render.resolution_y=1100;scene.render.resolution_percentage=100
scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.render.filepath=str(ROOT/'renders/direct-usb-cutaway.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'renders/direct-usb-cutaway.blend'))
