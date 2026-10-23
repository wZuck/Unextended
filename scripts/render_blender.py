"""Blender 4.5: studio renders from actual V1 CAD + labelled cap envelopes."""
import bpy,math,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
GEO=ROOT/'mechanical/render';OUT=ROOT/'renders';OUT.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)

def material(name,color,metal=0,rough=.4):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1);bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    return m
shell=material('Mist silver — appearance concept',(.39,.44,.43),.65,.28)
ivory=material('Warm ivory',(.79,.78,.68),0,.34)
muted=material('Sage modifiers',(.35,.42,.37),0,.38)
accent=material('Acid accent',(.61,.78,.09),0,.3)
ink=material('Legends',(.055,.075,.055),0,.6)
ground=material('Warm paper',(.74,.74,.69),0,.85)
def load(path,mat):
    bpy.ops.wm.stl_import(filepath=str(path));o=bpy.context.object;o.data.materials.append(mat)
    for poly in o.data.polygons:poly.use_smooth=True
    bevel=o.modifiers.new('Soft manufactured edge','BEVEL');bevel.width=.25;bevel.segments=3
    normals=o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
load(GEO/'case.stl',shell)
caps=json.loads((GEO/'caps.json').read_text())
for c in caps:
    modifier=c['label'] in ['Tab','Caps','Shift','RShift','Enter','Backspace','LCTRL','RCTRL','LGUI','Menu','LAlt','RAlt','Fn']
    load(GEO/(c['ref']+'.stl'),accent if c['label']=='Esc' else muted if modifier else ivory)
    text={'LCTRL':'ctrl','RCTRL':'ctrl','LGUI':'cmd','LAlt':'alt','RAlt':'alt','RShift':'shift','Shift':'shift','Backspace':'delete','Enter':'return','Menu':'menu','Space':''}.get(c['label'],c['label'])
    if not text:continue
    curve=bpy.data.curves.new('Legend','FONT');curve.body=text;curve.align_x='CENTER';curve.align_y='CENTER';curve.size=2.25 if len(text)<3 else 1.8;curve.extrude=.005
    ob=bpy.data.objects.new('Legend '+text,curve);bpy.context.collection.objects.link(ob);ob.location=(c['x'],c['y'],c['z']+.08);ob.rotation_euler=(math.radians(5.4),0,0);curve.materials.append(ink)
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.02));bpy.context.object.data.materials.append(ground);bpy.context.object.is_shadow_catcher=True
def area(name,loc,power,size,target=(0,0,10)):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    o=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
area('Large window',(-180,-180,350),2500000,260)
area('Edge light',(120,160,240),1800000,200)
area('Soft fill',(240,-60,180),900000,200)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.world.color=(.25,.25,.25);scene.render.resolution_x=1920;scene.render.resolution_y=1280;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
cam=bpy.data.cameras.new('Camera');ob=bpy.data.objects.new('Camera',cam);bpy.context.collection.objects.link(ob);scene.camera=ob;cam.type='ORTHO';cam.ortho_scale=390
for name,loc,target in [('hero',(230,-340,300),(0,0,15)),('top',(0,-80,450),(0,0,0))]:
    ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'unextended-concept.blend'))
