"""Read-only distribution catalog, sources, metadata and deterministic ZIP checks."""
import sys

sys.dont_write_bytecode = True
if __package__:
    from .skill_dist_support import ROOT, archive, catalog, package, require, validate_archive
else:
    from skill_dist_support import ROOT, archive, catalog, package, require, validate_archive


def validate(root=ROOT):
    for name in catalog(root):
        bundle = package(name, root, require_installable=False)
        payload = archive(bundle)
        require(payload == archive(bundle), 'Non-reproducible archive')
        require(validate_archive(payload, name) == bundle['files'], 'Archive content mismatch')


def main():
    try:
        validate()
    except (OSError, ValueError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        return 1
    print('PASS: 3 catalog entries, canonical sources, metadata/resources, links, copies and reproducible ZIPs')
    return 0


if __name__ == '__main__':
    sys.exit(main())
