"""Guarda la evidencia de unittest sin exigir pytest."""
import io
import unittest
import argparse
from .common import ROOT, json_write

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--final', action='store_true', help='Incluye evidencia final PostgreSQL/QGIS; ejecutar tras autenticar.')
    args=parser.parse_args()
    suite = unittest.defaultTestLoader.discover(str(ROOT/'tests'), pattern='test*.py' if args.final else 'test_geospatial.py')
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    output = stream.getvalue()
    prefix='final_tests' if args.final else 'tests'
    (ROOT/f'reports/geospatial/{prefix}.txt').write_text(output, encoding='utf-8')
    json_write(ROOT/f'reports/geospatial/{prefix}.json', dict(tests=result.testsRun,
        failures=len(result.failures), errors=len(result.errors), successful=result.wasSuccessful()))
    print(output)
    if not result.wasSuccessful():
        raise SystemExit(1)

if __name__ == '__main__':
    main()
