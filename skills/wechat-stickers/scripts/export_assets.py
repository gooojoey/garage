#!/usr/bin/env python3
"""Deterministic export of approved transparent art; no drawing, matting or network."""
import argparse
import hashlib
import html
import json
import re
import zipfile
from pathlib import Path
from PIL import Image, ImageOps, ImageSequence

PROFILES = {'banner': (750,400,500000,False), 'cover': (240,240,500000,True),
            'icon': (50,50,100000,True), 'avatar': (240,240,500000,None),
            'reward_guide': (750,560,500000,False), 'reward_thanks': (750,750,500000,False)}

def require(test, message):
    if not test:
        raise ValueError(message)

def safe_name(value):
    require(isinstance(value,str) and value.strip(), 'Empty name')
    require(not re.search(r'[<>:"/\\|?*\x00-\x1f]',value), 'Unsafe filename')
    require(value not in {'.','..'} and not value.endswith((' ','.')), 'Unsafe filename')
    return value

def crop_checked(im, box):
    if box is None:
        return im.copy()
    require(len(box)==4 and all(type(v) is int for v in box), 'Box must contain four integers')
    x,y,r,b=box
    require(0<=x<r<=im.width and 0<=y<b<=im.height, 'Crop outside source')
    return im.crop(box)

def transparent(im):
    require(im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255), 'Real transparent RGBA required')
    require(all(im.getpixel(p)[3]==0 for p in [(0,0),(im.width-1,0),(0,im.height-1),(im.width-1,im.height-1)]), 'Transparent corners required; inspect matte')

def resize_alpha(im,size):
    return im.convert('RGBa').resize(size,Image.Resampling.LANCZOS).convert('RGBA')

def fit_transparent(im,size,pad):
    transparent(im)
    box=im.getchannel('A').getbbox()
    require(box is not None,'Empty artwork')
    im=im.crop(box);scale=min((size[0]-pad*2)/im.width,(size[1]-pad*2)/im.height)
    part=resize_alpha(im,(max(1,round(im.width*scale)),max(1,round(im.height*scale))))
    out=Image.new('RGBA',size);out.alpha_composite(part,((size[0]-part.width)//2,(size[1]-part.height)//2))
    return out

def align_frames(items,base):
    records=[]
    for f in items:
        with Image.open(base/f['path']) as src:
            im=crop_checked(src.convert('RGBA'),f.get('box'))
        transparent(im)
        ax,ay=f['anchor']
        require(all(isinstance(v,(int,float)) and float('-inf')<v<float('inf') for v in [ax,ay]),'Invalid anchor')
        require(0<=ax<=im.width and 0<=ay<=im.height,'Anchor outside crop')
        box=im.getchannel('A').getbbox();require(box is not None,'Empty frame')
        records.append((im,ax,ay,box))
    require(len(records)>=4,'Need at least four source frames')
    left=min(b[0]-x for im,x,y,b in records);right=max(b[2]-x for im,x,y,b in records)
    top=min(b[1]-y for im,x,y,b in records);bottom=max(b[3]-y for im,x,y,b in records)
    scale=min(228/(right-left),228/(bottom-top))
    ox=120-(left+right)*scale/2;oy=120-(top+bottom)*scale/2
    frames=[]
    for im,x,y,b in records:
        part=resize_alpha(im,(max(1,round(im.width*scale)),max(1,round(im.height*scale))))
        out=Image.new('RGBA',(240,240));out.alpha_composite(part,(round(ox-x*scale),round(oy-y*scale)));frames.append(out)
    return frames,{'scale':scale,'target_anchor':[ox,oy],'source_anchors':[[x,y] for im,x,y,b in records]}

def write_gif(frames,seq,durations,dest):
    require(len(seq)==len(durations) and len(seq)>=4,'Sequence/duration mismatch')
    require(all(type(i) is int and 0<=i<len(frames) for i in seq),'Frame index outside range')
    require(all(type(t) is int and t>=50 and t%10==0 for t in durations),'Duration must be >=50ms and divisible by 10')
    require(len({frames[i].tobytes() for i in seq})>=4,'Too few distinct selected frames')
    atlas=Image.new('RGB',(240*len(frames),240))
    for i,f in enumerate(frames):
        atlas.paste(f.convert('RGB'),(240*i,0))
    for count in (192,160,128,96):
        shared=atlas.quantize(colors=count,dither=Image.Dither.NONE)
        palette=[0,0,0]+shared.getpalette()[:count*3];palette += [0]*(768-len(palette))
        result=[]
        for i in seq:
            f=frames[i];q=f.convert('RGB').quantize(palette=shared,dither=Image.Dither.NONE)
            # Shift indices rather than reallocating colors; reserve zero for transparency.
            q=q.point([min(v+1,255) for v in range(256)]);q.putpalette(palette)
            q.paste(0,mask=f.getchannel('A').point(lambda a:255 if a<145 else 0));result.append(q)
        result[0].save(dest,save_all=True,append_images=result[1:],duration=durations,loop=0,transparency=0,disposal=2,optimize=False)
        if dest.stat().st_size<=500000:
            return
    raise ValueError('GIF remains over 500000 bytes; redesign rather than silently omit motion')

def inspect_gif(path):
    with Image.open(path) as im:
        require(im.format=='GIF' and im.size==(240,240) and im.info.get('loop')==0,'Invalid GIF format/size/loop')
        hashes=set();durations=[];changes=[];previous=None
        for raw in ImageSequence.Iterator(im):
            f=raw.convert('RGBA');transparent(f);a=f.getchannel('A')
            require(not any(a.crop(b).getbbox() for b in [(0,0,240,2),(0,238,240,240),(0,0,2,240),(238,0,240,240)]),'Frame touches safety edge')
            data=f.tobytes();hashes.add(hashlib.sha256(data).hexdigest());durations.append(raw.info.get('duration',0))
            if previous is not None:
                changes.append(round(sum(x!=y for x,y in zip(previous,data))/len(data),4))
            previous=data
        require(len(hashes)>=4,'Export lost distinct frames')
        require(all(t>=50 and t%10==0 for t in durations),'Invalid GIF timing')
        require(path.stat().st_size<=500000,'GIF too large')
        return {'frames':im.n_frames,'distinct_frames':len(hashes),'cycle_ms':sum(durations),'loop':0,'transparent':True,'bytes':path.stat().st_size,'adjacent_byte_change':changes}

def inspect_material(path,kind):
    w,h,limit,alpha=PROFILES[kind]
    with Image.open(path) as im:
        require(im.size==(w,h),'Material dimensions mismatch')
        require(im.format==('JPEG' if alpha is False else 'PNG'),'Material format mismatch')
        if alpha is True:transparent(im)
        if alpha is False:require(im.mode=='RGB','Opaque RGB required')
    require(path.stat().st_size<=limit,'Material over size limit')
    return {'kind':kind,'pixels':[w,h],'bytes':path.stat().st_size,'transparent_required':alpha}

def export(manifest,out):
    require(not out.exists(),'Output directory exists; choose a new version')
    jobs=json.loads(manifest.read_text(encoding='utf-8'));base=manifest.parent
    title=jobs.get('album','微信表情');require(isinstance(title,str),'Invalid title')
    stickers=jobs.get('stickers',[]);materials=jobs.get('materials',[])
    require(stickers or materials,'No assets requested')
    require(len(stickers)<=24,'More than 24 stickers')
    names=[safe_name(j['name']) for j in stickers];require(len(names)==len(set(names)),'Duplicate sticker names')
    kinds=[j['kind'] for j in materials];require(len(kinds)==len(set(kinds)) and all(k in PROFILES for k in kinds),'Duplicate/unknown material kind')
    out.mkdir(parents=True);report={'album':title,'status':'pending_visual_review','full_album_count':8<=len(stickers)<=24,'stickers':[],'materials':[]};cards=[]
    for folder in ('gif','thumbnails','materials'):(out/folder).mkdir()
    for n,j in enumerate(stickers,1):
        frames,alignment=align_frames(j['frames'],base);stem=f'{n:02d}_{j["name"]}'
        dest=out/'gif'/f'{stem}.gif';write_gif(frames,j['sequence'],j['durations_ms'],dest)
        thumb=j.get('thumbnail_frame',j['sequence'][-1]);require(type(thumb) is int and 0<=thumb<len(frames),'Invalid thumbnail index')
        thumbnail=out/'thumbnails'/f'{stem}.png';frames[thumb].save(thumbnail,optimize=True)
        require(thumbnail.stat().st_size<=500000,'Thumbnail too large')
        report['stickers'].append({'file':dest.relative_to(out).as_posix(),'name':j['name'],'alignment':alignment,**inspect_gif(dest)})
        cards.append(f'<article><img width="240" height="240" src="{html.escape(dest.relative_to(out).as_posix(),quote=True)}"><p>{html.escape(j["name"])}</p></article>')
    for j in materials:
        kind=j['kind'];w,h,limit,alpha=PROFILES[kind]
        with Image.open(base/j['path']) as raw:im=crop_checked(raw.convert('RGBA'),j.get('crop'))
        if alpha is True:
            image=fit_transparent(im,(w,h),1 if kind=='icon' else 6)
        else:
            if alpha is False:require(im.getchannel('A').getextrema()==(255,255),'Opaque artwork required; do not silently flatten transparency')
            image=ImageOps.fit(im.convert('RGB') if alpha is False else im,(w,h),method=Image.Resampling.LANCZOS)
        dest=out/'materials'/f'{kind}_{w}x{h}.{"jpg" if alpha is False else "png"}'
        image.save(dest,**({'quality':93,'subsampling':0,'optimize':True} if alpha is False else {'optimize':True}))
        report['materials'].append({'file':dest.relative_to(out).as_posix(),**inspect_material(dest,kind)})
        cards.append(f'<article><img style="max-width:100%;height:auto" src="{dest.relative_to(out).as_posix()}"><p>{kind} {w}×{h}</p></article>')
    page='<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(title)+'</title><style>body{font-family:system-ui;background:#e9f1ed;padding:20px}main{display:flex;flex-wrap:wrap;gap:16px}article{background:#fff;padding:12px;text-align:center;border-radius:12px}.dark article{background:#344c60;color:white}button{padding:12px}</style><h1>'+html.escape(title)+'</h1><button onclick="document.body.classList.toggle(\'dark\')">切换深浅底</button><p>检查全部循环与首尾衔接；静态参数验证不等于视觉通过。</p><main>'+''.join(cards)+'</main></html>'
    (out/'preview.html').write_text(page,encoding='utf-8');(out/'manifest.local.json').write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return report

def package(out):
    require(out.is_dir(),'Export directory missing')
    report=json.loads((out/'report.json').read_text(encoding='utf-8'))
    # Fixed directories only: never bundle source images or manifests with private paths.
    for r in report['stickers']:inspect_gif(out/r['file'])
    for r in report['materials']:inspect_material(out/r['file'],r['kind'])
    archive=out/'wechat-assets.zip';require(not archive.exists(),'Archive exists; do not overwrite')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for folder in ('gif','thumbnails','materials'):
            for p in sorted((out/folder).iterdir()):
                require(p.is_file() and not p.is_symlink(),'Unexpected package entry')
                z.write(p,p.relative_to(out))
        z.write(out/'preview.html','preview.html')
    with zipfile.ZipFile(archive) as z:require(z.testzip() is None,'ZIP integrity failed')
    return archive

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('manifest',type=Path,nargs='?');parser.add_argument('output',type=Path,nargs='?');parser.add_argument('--package',type=Path)
    args=parser.parse_args()
    try:
        if args.package:print(package(args.package))
        else:
            require(args.manifest is not None and args.output is not None,'Provide manifest and output')
            report=export(args.manifest,args.output);print(json.dumps({'stickers':len(report['stickers']),'materials':len(report['materials']),'status':report['status']}))
    except (ValueError,KeyError,OSError,TypeError) as exc:
        parser.exit(2,f'Export stopped: {exc}\n')
