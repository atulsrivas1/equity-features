"""Hand-declared miniature archives and malicious raw-member controls."""
import base64
import csv
import hashlib
import importlib.util
import io
import os
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location('continuous_archives',ROOT/'tools/continuous_archives.py')
POLICY=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(POLICY)
MODULE='synthetic_package';VERSION='0.1.0a1';DIST=MODULE+'-'+VERSION+'.dist-info/'
PREFIX=MODULE+'-'+VERSION+'/'
EGG='src/'+MODULE+'.egg-info/'
SOURCE={'LICENSE':b'synthetic license\n','README.md':b'# Synthetic\n',
    'pyproject.toml':b'''[project]
name = "synthetic-package"
version = "0.1.0a1"
description = "Synthetic fixture"
authors = [{name = "Synthetic author"}]
dependencies = ["synthetic-dependency==1"]
[project.urls]
Repository = "https://example.invalid/synthetic"
''', 'src/'+MODULE+'/__init__.py':b'VALUE=1\n','src/'+MODULE+'/py.typed':b''}
METADATA=b'''Metadata-Version: 2.4
Name: synthetic-package
Version: 0.1.0a1
Summary: Synthetic fixture
Author: Synthetic author
License-Expression: Apache-2.0
Project-URL: Repository, https://example.invalid/synthetic
Requires-Python: <3.13,>=3.12
Description-Content-Type: text/markdown
License-File: LICENSE
Dynamic: license-file
Requires-Dist: synthetic-dependency==1

# Synthetic
'''.replace(b'\n',os.linesep.encode())


def wheel_files():
    files={MODULE+'/__init__.py':b'VALUE=1\n',MODULE+'/py.typed':b'',
        DIST+'METADATA':METADATA,DIST+'licenses/LICENSE':b'synthetic license\n',
        DIST+'top_level.txt':b'synthetic_package\n',
        DIST+'WHEEL':b'Wheel-Version: 1.0\nGenerator: setuptools (80.9.0)\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n'}
    record=io.StringIO();writer=csv.writer(record,lineterminator='\n')
    for name,body in files.items():
        digest=base64.urlsafe_b64encode(hashlib.sha256(body).digest()).rstrip(b'=').decode()
        writer.writerow([name,'sha256='+digest,len(body)])
    writer.writerow([DIST+'RECORD','','']);files[DIST+'RECORD']=record.getvalue().encode()
    return files


def sdist_files():
    files=dict(SOURCE)
    files.update({'PKG-INFO':METADATA,'setup.cfg':b'[egg_info]\ntag_build = \ntag_date = 0\n\n'.replace(b'\n',os.linesep.encode()),
        EGG+'PKG-INFO':METADATA,EGG+'dependency_links.txt':b'\n',
        EGG+'requires.txt':b'synthetic-dependency==1\n',EGG+'top_level.txt':b'synthetic_package\n'})
    names=set(SOURCE)|{EGG+name for name in ('PKG-INFO','SOURCES.txt','dependency_links.txt','requires.txt','top_level.txt')}
    files[EGG+'SOURCES.txt']=('\n'.join(sorted(names))+'\n').encode()
    return {PREFIX+name:body for name,body in files.items()}


class ClosedArchives(unittest.TestCase):
    def write(self,root,form,files,extra=(),mode=0o644):
        path=root/(MODULE+'-'+VERSION+('-py3-none-any.whl' if form=='wheel' else '.tar.gz'))
        if form=='wheel':
            with zipfile.ZipFile(path,'w') as archive:
                for name,body in [*files.items(),*extra]:
                    item=zipfile.ZipInfo(name);item.create_system=3
                    item.external_attr=(stat.S_IFREG|mode)<<16
                    archive.writestr(item,body)
        else:
            with tarfile.open(path,'w:gz') as archive:
                for name in (PREFIX.rstrip('/'),PREFIX+'src',PREFIX+'src/'+MODULE,PREFIX+EGG.rstrip('/')):
                    item=tarfile.TarInfo(name);item.type=tarfile.DIRTYPE;item.mode=0o755;archive.addfile(item)
                for name,body in [*files.items(),*extra]:
                    item=tarfile.TarInfo(name);item.size=len(body);item.mode=mode;archive.addfile(item,io.BytesIO(body))
        return path

    def reject(self,form,files,extra=(),mode=0o644):
        with tempfile.TemporaryDirectory(prefix='continuous-archive-negative-') as directory:
            path=self.write(Path(directory),form,files,extra,mode)
            with self.assertRaises((AssertionError,ValueError,KeyError)):
                POLICY.inspect(path,SOURCE,MODULE)

    def test_closed_wheel_and_sdist_with_expected_ancestors(self):
        for form,files in [('wheel',wheel_files()),('sdist',sdist_files())]:
            with self.subTest(form=form),tempfile.TemporaryDirectory(prefix='continuous-archive-positive-') as directory:
                path=self.write(Path(directory),form,files)
                actual,_=POLICY.inspect(path,SOURCE,MODULE)
                self.assertEqual(actual,files)

    def test_raw_path_duplicate_namespace_and_mode_negatives(self):
        for form,files in [('wheel',wheel_files()),('sdist',sdist_files())]:
            for name in ('../../outside.py','/outside.py','synthetic\\outside.py','EXTRA.md','equity_features/__init__.py'):
                with self.subTest(form=form,extra=name):self.reject(form,files,[(name,b'bad')])
            existing=next(iter(files))
            for name in (existing,existing.upper()):
                with self.subTest(form=form,collision=name):self.reject(form,files,[(name,b'bad')])
            self.reject(form,files,mode=0o755)

    def test_missing_source_license_readme_and_metadata_drift(self):
        for form,original in [('wheel',wheel_files()),('sdist',sdist_files())]:
            for name in list(original):
                if name.endswith(('/__init__.py','/LICENSE','/README.md','/py.typed','/METADATA','/PKG-INFO')):
                    files=dict(original);files[name]+=b'corrupted'
                    with self.subTest(form=form,drift=name):self.reject(form,files)
            files=dict(original);del files[(MODULE+'/' if form=='wheel' else PREFIX+'src/'+MODULE+'/')+'py.typed']
            self.reject(form,files)
        for field in (b'Requires-Dist: unselected==1\n',b'Provides-Extra: unselected\n',b'Unknown-Header: value\n'):
            files=wheel_files();files[DIST+'METADATA']=field.replace(b'\n',os.linesep.encode())+METADATA
            self.reject('wheel',files)
        files=wheel_files();files[DIST+'WHEEL']=files[DIST+'WHEEL'].replace(b'py3-none-any',b'cp312-native-any');self.reject('wheel',files)

    def test_record_sources_and_generated_metadata_negatives(self):
        for change in ('missing','duplicate','digest','size','self'):
            files=wheel_files();rows=list(csv.reader(io.StringIO(files[DIST+'RECORD'].decode())))
            if change=='missing':rows.pop(0)
            elif change=='duplicate':rows.append(rows[0])
            elif change=='digest':rows[0][1]='sha256=invalid'
            elif change=='size':rows[0][2]='999'
            else:rows[-1][1]='sha256=invalid'
            stream=io.StringIO();csv.writer(stream,lineterminator='\n').writerows(rows);files[DIST+'RECORD']=stream.getvalue().encode()
            self.reject('wheel',files)
        for relative in ('setup.cfg',EGG+'SOURCES.txt',EGG+'requires.txt',EGG+'top_level.txt',EGG+'dependency_links.txt'):
            files=sdist_files();files[PREFIX+relative]+=b'extra\n';self.reject('sdist',files)

    def test_link_device_directory_raw_types(self):
        for kind in (tarfile.SYMTYPE,tarfile.LNKTYPE,tarfile.CHRTYPE,tarfile.DIRTYPE):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory(prefix='continuous-archive-types-') as directory:
                path=Path(directory)/(MODULE+'-'+VERSION+'.tar.gz')
                with tarfile.open(path,'w:gz') as archive:
                    item=tarfile.TarInfo(PREFIX+'unselected');item.type=kind;item.linkname='outside';archive.addfile(item)
                with self.assertRaises(AssertionError):POLICY.inspect(path,SOURCE,MODULE)
        for duplicate in (True,False):
            with tempfile.TemporaryDirectory(prefix='continuous-archive-directories-') as directory:
                path=self.write(Path(directory),'sdist',sdist_files(),[(PREFIX.rstrip('/'),b'collision')])
                if duplicate:
                    # A duplicate expected directory is separate from file/dir collision.
                    with tarfile.open(path,'r:gz') as archive:members=[(x,archive.extractfile(x).read() if x.isfile() else None) for x in archive]
                    with tarfile.open(path,'w:gz') as archive:
                        for item,body in members[:-1]:archive.addfile(item,io.BytesIO(body) if body is not None else None)
                        archive.addfile(members[0][0])
                with self.assertRaises(AssertionError):POLICY.inspect(path,SOURCE,MODULE)
        with tempfile.TemporaryDirectory(prefix='continuous-archive-link-') as directory:
            path=Path(directory)/(MODULE+'-'+VERSION+'-py3-none-any.whl')
            with zipfile.ZipFile(path,'w') as archive:
                item=zipfile.ZipInfo(MODULE+'/__init__.py');item.create_system=3;item.external_attr=(stat.S_IFLNK|0o777)<<16;archive.writestr(item,b'outside')
            with self.assertRaises(AssertionError):POLICY.inspect(path,SOURCE,MODULE)

    def test_raw_zip_nul_suffix_is_refused_before_filename_truncation(self):
        # Write a same-length innocuous raw name, then replace its separator byte
        # in BOTH local and central headers. ZipInfo truncates the effective name
        # at NUL while preserving orig_filename; the payload/RECORD remain valid.
        with tempfile.TemporaryDirectory(prefix='continuous-archive-nul-') as directory:
            files=wheel_files();name=MODULE+'/__init__.py';body=files.pop(name)
            files[name+'!hidden']=body
            path=self.write(Path(directory),'wheel',files)
            raw=path.read_bytes();old=(name+'!hidden').encode();new=(name+'\x00hidden').encode()
            self.assertEqual(raw.count(old),2);path.write_bytes(raw.replace(old,new))
            with zipfile.ZipFile(path) as archive:
                item=next(x for x in archive.infolist() if '\x00' in x.orig_filename)
                self.assertEqual(item.filename,name)
            with self.assertRaises(AssertionError):POLICY.inspect(path,SOURCE,MODULE)

    def test_selected_platform_directory_mode_without_widening_file_modes(self):
        with tempfile.TemporaryDirectory(prefix='continuous-archive-directory-mode-') as directory:
            path=self.write(Path(directory),'sdist',sdist_files())
            with tarfile.open(path,'r:gz') as archive:
                members=[(item,archive.extractfile(item).read() if item.isfile() else None) for item in archive]
            with tarfile.open(path,'w:gz') as archive:
                for item,body in members:
                    if item.isdir():item.mode=0o777
                    archive.addfile(item,io.BytesIO(body) if body is not None else None)
            if os.name=='nt':POLICY.inspect(path,SOURCE,MODULE)
            else:
                with self.assertRaises(AssertionError):POLICY.inspect(path,SOURCE,MODULE)
        self.reject('sdist',sdist_files(),mode=0o777)


if __name__=='__main__':unittest.main()
