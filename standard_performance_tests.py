from __future__ import print_function

import contextlib
import datetime
import os
import os.path
import shutil
import sys

import numpy as np

import iris
from iris.fileformats.um import structured_um_loading


class TimedOp(object):
    def __init__(self, print_result=False):
        self.print_result = print_result

    def __enter__(self):
        self.start_datetime = datetime.datetime.now()
        return self

    def __exit__(self, e1, e2, e3):
        self.end_datetime = datetime.datetime.now()
        elapsed_deltatime = self.end_datetime - self.start_datetime
        self.seconds = elapsed_deltatime.total_seconds()
        if self.print_result:
            action = 'Time taken : {:12.6f} seconds'
            print(action.format(self.seconds))


def do_load(filespec):
    with TimedOp() as timer:
        data = iris.load(filespec)
    return timer.seconds, data


def do_structured_load(filespec):
    with structured_um_loading():
        result = do_load(filespec)
    return result


def _cube_data(cube):
    # Note: don't realise the original cube !
    return cube.copy().data


def do_data_load(cubes_list):
    with TimedOp() as timer:
        data = map(_cube_data, cubes_list)
    return timer.seconds, data


def do_save(cubes, filename):
    tmp_dir = os.path.join(os.environ['TMPDIR'], os.environ['USER'])
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)
    tmp_filepath = os.path.join(tmp_dir, filename)
    with TimedOp() as timer:
        iris.save(cubes, tmp_filepath)
    return timer.seconds, None


_DEBUG = True

_DEFAULT_REPS = 3
#if _DEBUG:
#    _DEFAULT_REPS = 1

REPORT_LINES = []

def exercise(description, method, args, repeats=None, abstol=0.001, reltol=0.05):
    if repeats is None:
        repeats = _DEFAULT_REPS

    times = []
    n_rep = 1

    if _DEBUG:
        print('\n')
        print('  Running {!r} :'.format(description))
        sys.stdout.flush()

    while n_rep <= repeats:
        if _DEBUG:
            print('    repeat #{} .. '.format(n_rep), end='')
            sys.stdout.flush()
        time, result = method(*args)
        if _DEBUG:
            print('took {:12.6f} ...'.format(time))
            sys.stdout.flush()
        times.append(time)
        n_rep += 1

    if repeats > 2:
        np.testing.assert_allclose(times[-2], times[-1],
                                   atol=abstol, rtol=reltol)

    description = '"{}"'.format(description).rjust(40)
    summary = 'Test {} : {:12.6f} seconds'.format(description, times[-1])
    print('\n\n{}\n'.format(summary))
    sys.stdout.flush()
    global REPORT_LINES
    REPORT_LINES.append(summary)
    return result


def set_futures():
    names = ('cell_datetime_objects',
             'netcdf_promote',
             'strict_grib_load',
             'netcdf_no_unlimited')
    for name in names:
        if hasattr(iris.FUTURE, name):
            setattr(iris.FUTURE, name, True)


def run_tests():
    set_futures()

    pp_filespec = \
        '/data/local/dataZoo/PP/mogrepsR/2011032906.qtey06.oper00.000*.pp'

    pp_cubes = exercise('PP load (plain)',
                        do_load, [pp_filespec])

    exercise('PP load (structured)',
             do_structured_load, [pp_filespec])

    exercise('PP data load',
             do_data_load, [pp_cubes])

    ff_filespec = '/data/local/dataZoo/FF/ff_variants/ff_64.ff'

    ff_cubes = exercise('Fieldsfile load (plain)',
                        do_load, [ff_filespec])

    exercise('Fieldsfile load (structured)',
             do_structured_load, [ff_filespec])

    exercise('Fieldsfile data load',
             do_data_load, [ff_cubes[29:30]])

    nc_filespec = (
        '/data/local/dataZoo/netCDF/largeFile/'
        'tas_day_HadGEM2-ES_historical_r1i1p1_18591201-20051130.nc')

    nc_cubes = exercise('NetCDF load (plain)',
                        do_load, [nc_filespec])

    nc_dataload_cubes_list = [nc_cubes[0][:5000]]
    exercise('NetCDF data load',
             do_data_load, [nc_dataload_cubes_list])

    nc_save_cube = nc_cubes[0][:5000]
    exercise('PP save to PP',
             do_save, [pp_cubes, 'tmp.pp'])
    exercise('PP save to NetCDF',
             do_save, [pp_cubes, 'tmp.nc'])
    exercise('NetCDF save to NetCDF',
             do_save, [nc_save_cube, 'tmp.nc'])
    exercise('NetCDF save to PP',
             do_save, [nc_save_cube, 'tmp.pp'])

    print('\n\nResults summary:')
    for summary in REPORT_LINES:
        print(summary)


if __name__ == '__main__':
    run_tests()
