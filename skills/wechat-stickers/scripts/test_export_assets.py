"""Anonymous test fixtures only; these are not sticker artwork."""
import json
import shutil
import uuid
import unittest
import zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from export_assets import export,package,align_frames,write_gif,inspect_gif

class ExportTests(unittest.TestCase):
    def setUp(self):
        self.root=(Path.cwd()/('wechat-test-'+uuid.uuid4().hex)).resolve();self.root.mkdir()
        if self.root.parent != Path.cwd().resolve():raise RuntimeError('Test directory outside workspace')
        self.frames=[]
        for n in range(4):
            f=Image.new('RGBA',(100,100));d=ImageDraw.Draw(f)
            d.rectangle((35,40,65,90),fill='#203c58');d.ellipse((30+n*4,10,60+n*4,40),fill='#eeae66')
            f.save(self.root/f'f{n}.png');self.frames.append({'path':f'f{n}.png','anchor':[50,90]})
        Image.new('RGB',(900,600),'#327a68').save(self.root/'banner.png')
        self.manifest=self.root/'manifest.json'
        self.jobs={'album':'Test','stickers':[{'name':'hello','frames':self.frames,'sequence':[0,1,2,3,2,1],'durations_ms':[250,150,150,350,150,150]}],'materials':[{'kind':'banner','path':'banner.png'},{'kind':'cover','path':'f0.png'},{'kind':'icon','path':'f0.png'}]}
        self.manifest.write_text(json.dumps(self.jobs),encoding='utf-8')
    def tearDown(self):
        if self.root.parent != Path.cwd().resolve() or not self.root.name.startswith('wechat-test-'):raise RuntimeError('Unsafe cleanup path')
        shutil.rmtree(self.root)
    def test_export_and_package(self):
        out=self.root/'out';report=export(self.manifest,out)
        self.assertEqual(report['status'],'pending_visual_review')
        self.assertFalse(report['full_album_count'])
        self.assertEqual(report['stickers'][0]['cycle_ms'],1200)
        self.assertEqual(report['stickers'][0]['distinct_frames'],4)
        archive=package(out)
        with zipfile.ZipFile(archive) as z:
            self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),6)
            self.assertNotIn('manifest.local.json',z.namelist())
        with self.assertRaises(ValueError):export(self.manifest,out)
        with self.assertRaises(ValueError):package(out)
    def test_reject_opaque(self):
        Image.new('RGB',(100,100),'white').save(self.root/'f0.png')
        with self.assertRaisesRegex(ValueError,'transparent'):align_frames(self.frames,self.root)
    def test_reject_bad_crop(self):
        self.frames[0]['box']=[0,0,101,100]
        with self.assertRaisesRegex(ValueError,'Crop'):align_frames(self.frames,self.root)
    def test_reject_bad_anchor(self):
        self.frames[0]['anchor']=[500,0]
        with self.assertRaisesRegex(ValueError,'Anchor'):align_frames(self.frames,self.root)
    def test_shared_scale_preserves_anchor(self):
        frames,record=align_frames(self.frames,self.root)
        self.assertEqual(len(record['source_anchors']),4)
        def body_center(im):
            # Lower torso excludes the moving head/torso overlap and resampling halo.
            pts=[(x,y) for y in range(170,220) for x in range(240) if im.getpixel((x,y))==(32,60,88,255)]
            return sum(x for x,y in pts)/len(pts),sum(y for x,y in pts)/len(pts)
        centers=[body_center(f) for f in frames]
        self.assertEqual(centers,[centers[0]]*4)
    def test_reject_fake_animation_and_timing(self):
        frames,_=align_frames(self.frames,self.root)
        with self.assertRaisesRegex(ValueError,'distinct'):write_gif(frames,[0]*4,[150]*4,self.root/'bad.gif')
        with self.assertRaisesRegex(ValueError,'Duration'):write_gif(frames,[0,1,2,3],[10]*4,self.root/'bad.gif')
    def test_reject_path_name(self):
        self.jobs['stickers'][0]['name']='../escape';self.manifest.write_text(json.dumps(self.jobs),encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'Unsafe'):export(self.manifest,self.root/'out')

if __name__=='__main__':unittest.main()
