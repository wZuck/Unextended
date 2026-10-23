"""Strict reader for route-only Freerouting SES output; no placement import.

Keeps net names explicit rather than relying on a different board's numeric
net codes. Supports the four-layer through-via padstack exported here only.
"""
import json
import re

def parse(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text)
    stack=[];root=None
    for token in tokens:
        if token=='(':
            node=[]
            if stack:stack[-1].append(node)
            else:assert root is None;root=node
            stack.append(node)
        elif token==')':assert stack;stack.pop()
        else:
            assert stack
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack and root and root[0]=='session'
    return root

def child(node,name):
    found=[v for v in node[1:] if isinstance(v,list) and v and v[0]==name]
    assert len(found)==1,(name,len(found))
    return found[0]

def routes(text):
    root=parse(text);section=child(root,'routes');resolution=child(section,'resolution')
    assert resolution[1]=='um';scale=1000*float(resolution[2])
    library=child(section,'library_out');padstacks={p[1]:p for p in library[1:]}
    out=[]
    for net in child(section,'network_out')[1:]:
        assert net[0]=='net';name=net[1]
        for item in net[2:]:
            if item[0]=='wire':
                path=child(item,'path');layer=path[1];width=float(path[2])/scale
                points=[(float(path[i])/scale,-float(path[i+1])/scale) for i in range(3,len(path),2)]
                assert layer in ('F.Cu','In1.Cu','In2.Cu','B.Cu') and len(points)>=2
                for a,b in zip(points,points[1:]):out.append(dict(kind='track',net=name,layer=layer,width=width,a=a,b=b))
            elif item[0]=='via':
                assert item[1] in ('Via[0-3]_600:300_um','Via[0-1]_600:300_um') and item[1] in padstacks
                for shape in padstacks[item[1]][2:]:
                    if shape[0]=='shape':assert float(shape[1][2])/scale==.6
                out.append(dict(kind='via',net=name,x=float(item[2])/scale,y=-float(item[3])/scale,diameter=.6,drill=.3))
            else:raise ValueError('Unsupported SES route item: '+str(item[0]))
    return out
