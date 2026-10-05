# Experimental foundation builds and delivery

EQ-009 channel: downloadable **GitHub Actions artifacts from successful main
Foundation package checks**, named `foundation-<commit>-<OS>`. No PyPI/public
registry publication. Public repository readers with appropriate GitHub access
can download authorized code/synthetic artifacts; no private data is included.
These are version0.0.1a0 experimental R0 distributions, not production calculators.
30-day retention is requested, subject to repository limits; record actual expiry
on each issue. After expiry, rebuild from the recorded commit with the pinned
requirements; retained artifacts are a delivery channel, not permanent archival.

```text
python -m pip install -r requirements-dev.txt
python tools/verify_imports.py
python tools/check_boundary.py
python -m mypy --strict packages/contracts/src packages/features/src
python tools/build_foundation.py
```

The build tool creates both wheels and sdists twice, compares SHA256 bytes,
inspects contents/license/py.typed, and installs each pair in separate fresh venvs
with no package-index fallback for project packages. Sdist install uses the exact
setuptools build pin. It runs installed unit tests when present. SOURCE_DATE_EPOCH
1700000000 fixes wheel timestamps; sdist tar ownership/mode/mtime and gzip headers
are canonicalized at that epoch. This timestamp is a packaging convention, not
market time or an availability claim. Repeatability is within a tested OS/toolchain;
cross-platform archive byte identity is not promised.

`manifest.json` binds source commit, Python/OS, epoch and SHA256 of exactly four
artifacts. CI logs record tool versions and tests. Download the bundle from the
recorded main run, compare all file hashes/manifest commit, then clean-install.
Only after actual download and verification is an implementation Released/Done.
Later foundation revisions retain commit identity and update the experimental
version when public APIs change. CI artifacts from PR refs are review evidence;
main artifacts are the declared delivery. See issue evidence for current run IDs.

## Pure-boundary gate

`check_boundary.py` allows only reviewed stdlib/inward/explicit columnar imports,
rejects source/provider/filesystem/process/clock modules, dynamic execution/import,
reflective access and common I/O calls, including imported function aliases and
wildcard imports.14negative fixtures prove
the gate fails on prohibited imports/accesses. Runtime tests supplement it as APIs
grow. This is a conservative project-owned Python boundary policy, not a sandbox
or proof about arbitrary third-party code/native dependencies. Each new import or
call pattern requires review; NumPy/PyArrow I/O methods remain forbidden.

Primary guidance: [build frontend](https://build.pypa.io/en/stable/) and
[GitHub artifact retention/downloads](https://docs.github.com/en/actions/tutorials/store-and-share-data).
Artifact checksums and actual installations establish delivery; merged source
alone and editable wheels alone do not.
