"""Inert fabricated archives; no build, install or archive extraction."""
import base64,csv,hashlib,importlib.util,io,tarfile,tempfile,tomllib,unittest,zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('agent_builder',ROOT/'tools/build_agent_evidence.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)


class ArchiveChecks(unittest.TestCase):
    def setUp(self):
        work=(ROOT/'work').resolve();work.mkdir(exist_ok=True)
        self.owned=tempfile.TemporaryDirectory(prefix='agent-archive-check-',dir=work)
        self.root=Path(self.owned.name).resolve();self.assertTrue(self.root.is_relative_to(work))
        original=ROOT/'packages/agent-evidence';self.source=self.root/'source'
        for path in original.rglob('*'):
            relative=path.relative_to(original)
            if path.is_file() and '__pycache__' not in relative.parts and not path.name.endswith(('.pyc','.pyo')):
                target=self.source/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(path.read_bytes())
        self.project=tomllib.loads((self.source/'pyproject.toml').read_text(encoding='utf-8'))['project']
        self.module='equity_feature_agent_evidence';self.version='0.1.0a2'

    def tearDown(self):self.owned.cleanup()

    def zip(self,names):
        p=self.root/'probe.whl'
        with zipfile.ZipFile(p,'w') as z:
            for name in names:z.writestr(name,b'' if name.endswith('/') else b'x')
        return p

    def tar(self,names):
        p=self.root/'probe.tar.gz'
        with tarfile.open(p,'w:gz') as t:
            for name in names:
                info=tarfile.TarInfo(name);info.type=tarfile.DIRTYPE if name.endswith('/') else tarfile.REGTYPE
                info.size=0 if info.isdir() else 1;t.addfile(info,None if info.isdir() else io.BytesIO(b'x'))
        return p

    def metadata(self,body):
        p=self.project
        fields=[('Metadata-Version','2.4'),('Name',p['name']),('Version',p['version']),('Summary',p['description']),
                ('Author','Equity Features contributors'),('License-Expression','Apache-2.0'),
                ('Project-URL','Repository, https://github.com/atulsrivas1/equity-features'),
                ('Requires-Python','<3.13,>=3.12'),('License-File','LICENSE'),('Description-Content-Type','text/markdown')]
        fields.extend(('Requires-Dist',value) for value in p['dependencies'])
        return ''.join(k+': '+v+'\n' for k,v in fields).encode('ascii')+b'\n'+body

    def wheel(self,metadata):
        module=self.module;dist=module+'-'+self.version+'.dist-info/'
        files={p.relative_to(self.source/'src').as_posix():p.read_bytes() for p in (self.source/'src'/module).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        files.update({dist+'METADATA':metadata,dist+'WHEEL':b'Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n',
                      dist+'top_level.txt':(module+'\n').encode(),dist+'licenses/LICENSE':(self.source/'LICENSE').read_bytes()})
        record=dist+'RECORD';stream=io.StringIO();writer=csv.writer(stream,lineterminator='\n')
        for name,data in files.items():writer.writerow([name,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode(),str(len(data))])
        writer.writerow([record,'','']);files[record]=stream.getvalue().encode()
        p=self.root/(module+'-'+self.version+'-py3-none-any.whl')
        with zipfile.ZipFile(p,'w') as z:
            for name,data in files.items():z.writestr(name,data)
        return p

    def sdist(self,readme,metadata):
        prefix=self.module+'-'+self.version+'/'
        files={prefix+'src/'+p.relative_to(self.source/'src').as_posix():p.read_bytes() for p in (self.source/'src'/self.module).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        files.update({prefix+'LICENSE':(self.source/'LICENSE').read_bytes(),prefix+'pyproject.toml':(self.source/'pyproject.toml').read_bytes(),prefix+'README.md':readme,prefix+'PKG-INFO':metadata})
        p=self.root/(self.module+'-'+self.version+'.tar.gz')
        with tarfile.open(p,'w:gz') as t:
            for name,data in files.items():
                info=tarfile.TarInfo(name);info.size=len(data);t.addfile(info,io.BytesIO(data))
        return p

    def test_full_member_positive_and_counts(self):
        for p in (self.zip(['a/','a/b']),self.tar(['a/','a/b'])):
            files,members=builder.contents(p,with_members=True)
            self.assertEqual(len(files),1);self.assertEqual(len(members),2)
            self.assertEqual(sorted(x['kind'] for x in members.values()),['directory','file'])

    def test_zip_unsafe_directories(self):
        for name in ('../outside/','C:/outside/','a//b/','./a/','.git/','a./'):
            with self.subTest(name=name),self.assertRaises(AssertionError):builder.contents(self.zip([name]))

    def test_zip_physical_backslash_nul_and_special(self):
        for replacement in (b'ab\\outside',b'ab\x00outside'):
            p=self.zip(['ab/outside']);raw=p.read_bytes();self.assertEqual(raw.count(b'ab/outside'),2)
            p.write_bytes(raw.replace(b'ab/outside',replacement))
            with self.assertRaises(AssertionError):builder.contents(p)
        p=self.root/'special.whl';info=zipfile.ZipInfo('link');info.create_system=3;info.external_attr=0o120777<<16
        with zipfile.ZipFile(p,'w') as z:z.writestr(info,b'target')
        with self.assertRaises(AssertionError):builder.contents(p)
        for name,mode,data in (('payload/',0o040755,b'opaque'),('file',0o040755,b''),('directory/',0o100644,b'')):
            info=zipfile.ZipInfo(name);info.create_system=3;info.external_attr=mode<<16
            with zipfile.ZipFile(p,'w') as z:z.writestr(info,data)
            with self.assertRaises(AssertionError):builder.contents(p)
        p=self.zip(['empty/']);data=bytearray(p.read_bytes())
        for signature,offset in ((b'PK\x03\x04',14),(b'PK\x01\x02',16)):
            pos=data.index(signature)+offset;data[pos:pos+4]=b'\x01\x00\x00\x00'
        p.write_bytes(data)
        with self.assertRaises(AssertionError):builder.contents(p)

    def test_tar_unsafe_directories_and_links(self):
        for name in ('../outside/','C:/outside/','a/../b/','a\\outside/','a /'):
            with self.subTest(name=name),self.assertRaises(AssertionError):builder.contents(self.tar([name]))
        p=self.root/'link.tar.gz'
        with tarfile.open(p,'w:gz') as t:
            info=tarfile.TarInfo('link');info.type=tarfile.SYMTYPE;info.linkname='target';t.addfile(info)
        with self.assertRaises(AssertionError):builder.contents(p)
        with tarfile.open(p,'w:gz') as t:
            info=tarfile.TarInfo('payload/');info.type=tarfile.DIRTYPE;info.size=6;t.addfile(info,io.BytesIO(b'opaque'))
        with self.assertRaises(AssertionError):builder.contents(p)

    def test_windows_aliases_and_file_ancestors(self):
        for names in (['A','a'],['a','a/b'],['CON'],['lpt1.txt'],['a','a/']):
            for factory in (self.zip,self.tar):
                with self.subTest(names=names),self.assertRaises(AssertionError):builder.contents(factory(names))

    def test_wheel_long_description_exact_source(self):
        body=(self.source/'README.md').read_bytes()
        self.assertTrue(builder.inspect(self.wheel(self.metadata(body)),'agent-evidence',self.source)['metadata_source_readme_verified'])
        with self.assertRaises(AssertionError):builder.inspect(self.wheel(self.metadata(b'WRONG PUBLIC README\n')),'agent-evidence',self.source)

    def test_sdist_readme_and_metadata_are_independent(self):
        body=(self.source/'README.md').read_bytes()
        self.assertTrue(builder.inspect(self.sdist(body,self.metadata(body)),'agent-evidence',self.source)['metadata_source_readme_verified'])
        for readme,metadata in ((b'wrong\n',self.metadata(body)),(body,self.metadata(b'wrong\n')),(b'wrong\n',self.metadata(b'wrong\n'))):
            with self.assertRaises(AssertionError):builder.inspect(self.sdist(readme,metadata),'agent-evidence',self.source)

    def test_extra_dependency_summary_author_metadata_refuse(self):
        body=(self.source/'README.md').read_bytes();good=self.metadata(body)
        for old,new in ((b'\n\n',b'\nProvides-Extra: unselected\n\n'),
                        (b'\n\n',b'\nRequires-Dist: unexpected==1\n\n'),
                        (self.project['description'].encode(),b'wrong description'),
                        (b'Equity Features contributors',b'Unknown author')):
            with self.assertRaises(AssertionError):builder.inspect(self.wheel(good.replace(old,new,1)),'agent-evidence',self.source)


if __name__=='__main__':unittest.main()
