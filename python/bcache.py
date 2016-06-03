# -*- coding:utf-8 -*-
#    author    :   丁雪峰
#    time      :   2016-06-02 02:32:00
#    email     :   fengidri@yeah.net
#    version   :   1.0.1


import os
import re

def fun_get_backings():
    bcaches = []
    fs = os.listdir('/sys/block')
    for f in fs:
        if f.startswith('bcache'):
            bcaches.append(f)
    return bcaches

def fun_get_cache_set():
    caches = []
    fs = os.listdir('/sys/fs/bcache')
    for f in fs:
        if f.startswith('register'):
            continue
        caches.append(f)
    return caches


def fun_backing_set_cache_set(b, s):
    open('/sys/block/%s/bcache/attach' % b, 'w').write(s)


def get_cache_priority_stats(cache):
    '''Retrieve priority stats from a cache.'''
    attrs = {}

    for line in file_to_lines('%s/priority_stats' % cache):
        x = line.split()
        key = x[0]
        value = x[1]
        attrs[key[:-1]] = value
    return attrs

def dump_cachedev(cachedev_path):
    '''Dump a cachding device stats.'''
    def fmt_cachesize(val):
        return '%s\t(%d%%)' % (format_sectors(val), float(val) / cache_size * 100)

#    global MAX_KEY_LENGTH, devnum_map
    attrs = [
#        ('../dev',                   'Device',             lambda x: '%s (%s)' % (devnum_map.get(x, '?'), x)),
        ('../size',                  'Size',               format_sectors),
        ('block_size',               'Block Size',         pretty_size),
        ('bucket_size',              'Bucket Size',        pretty_size),
        ('cache_replacement_policy', 'Replacement Policy', None),
        ('discard',                  'Discard?',           str_to_bool),
        ('io_errors',                'I/O Errors',         None),
        ('metadata_written',         'Metadata Written',   pretty_size),
        ('written',                  'Data Written',       pretty_size),
        ('nbuckets',                 'Buckets',            None),
        (None,                       'Cache Used',         lambda x: fmt_cachesize(used_sectors)),
        (None,                       'Cache Unused',       lambda x: fmt_cachesize(unused_sectors)),
    ]

    stats = get_cache_priority_stats(cachedev_path)
    cache_size = int(file_to_line('%s/../size' % cachedev_path))
    unused_sectors = float(stats['Unused'][:-1]) * cache_size / 100
    used_sectors = cache_size - unused_sectors

    print('--- Cache Device ---')
    for (sysfs_name, display_name, conversion_func) in attrs:
        if sysfs_name is not None:
            val = file_to_line('%s/%s' % (cachedev_path, sysfs_name))
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('  %-*s%s' % (MAX_KEY_LENGTH - 2, display_name, val))




def bcache_info(bcache):
    ral_block = os.path.realpath('/sys/block/%s/bcache' % bcache).split('/')[-2]

    cache_path = '/sys/block/%s/bcache/cache' % bcache
    if os.path.exists(cache_path):
        cache = os.path.realpath(cache_path).split('/')[-1]
    else:
        cache = ''
    print bcache, ral_block, cache




def cmd_list(args):
    print "========================= cache set ============================"
    for c in fun_get_cache_set():
        ral_block = os.path.realpath('/sys/fs/bcache/%s/cache0' % c).split('/')[-2]
        print  c, ral_block

    print ''
    print "========================= backing device ============================"

    for b in fun_get_backings():
        bcache_info(b)




def cmd_set_cache(args):
    if len(args.set) < 2:
        print "args.set too less"
        return
    set_uuid = args.set[0]

    if args.set[1] == 'all':
        for b in fun_get_backings():
            fun_backing_set_cache_set(b, set_uuid)
    else:
        for b in args.set[1:]:
            fun_backing_set_cache_set(b, set_uuid)




#import argparse
#
#parser = argparse.ArgumentParser(description='Bcache')
#subparser = parser.add_subparsers()
#arg = subparser.add_parser('list', help= 'list all backing device and cache set')
#arg.set_defaults(func = cmd_list)
#arg = subparser.add_parser('set', help= 'set the cache set for backing drive')
#arg.add_argument('set', nargs='+')
#arg.set_defaults(func = cmd_set_cache)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#args = parser.parse_args()
#args.func(args)




import os
import sys
import argparse

MAX_KEY_LENGTH    = 28
DEV_BLOCK_PATH    = '/dev/block/'
SYSFS_BCACHE_PATH = '/sys/fs/bcache/'

def file_to_lines(fname):
    try:
        with open(fname, "r") as fd:
            return fd.readlines()
    except:
        return []

def file_to_line(fname):
    ret = file_to_lines(fname)
    if ret:
        return ret[0].strip()
    return ''

def str_to_bool(x):
    return x == '1'


def pretty_size(x):
    return format_sectors(interpret_sectors(x))

def dump_bdev(bdev_path):
    '''Dump a backing device stats.'''
#    global MAX_KEY_LENGTH, devnum_map
    attrs = [
#        ('../dev',              'Device',               lambda x: '%s (%s)' % (devnum_map.get(x, '?'), x)),
        ('../size',             'Size',                 format_sectors),
        ('cache_mode',          'Cache Mode',           None),
        ('readahead',           'Readahead',            None),
        ('sequential_cutoff',   'Sequential Cutoff',    pretty_size),
        ('sequential_merge',    'Merge sequential?',    str_to_bool),
        ('state',               'State',                None),
        ('writeback_running',   'Writeback?',           str_to_bool),
        ('dirty_data',          'Dirty Data',           pretty_size),
    ]

    print('--- Backing Device ---')
    for (sysfs_name, display_name, conversion_func) in attrs:
        val = file_to_line('%s/%s' % (bdev_path, sysfs_name))
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('  %-*s%s' % (MAX_KEY_LENGTH - 2, display_name, val))


def hits_to_str(hits_str, misses_str):
    '''Render a hits/misses ratio as a string.'''
    hits = int(hits_str)
    misses = int(misses_str)

    ret = '%d' % hits
    if hits + misses != 0:
        ret = '%s\t(%.d%%)' % (ret, 100 * hits / (hits + misses))
    return ret

def dump_stats(sysfs_path, indent_str, stats):
    '''Dump stats on a bcache device.'''
    stat_types = [
        ('five_minute', 'Last 5min'),
        ('hour',        'Last Hour'),
        ('day',         'Last Day'),
        ('total',       'Total'),
    ]
    attrs = ['bypassed', 'cache_bypass_hits', 'cache_bypass_misses', 'cache_hits', 'cache_misses']
    display = [
        ('Hits',          lambda: hits_to_str(stat_data['cache_hits'], stat_data['cache_misses'])),
        ('Misses',        lambda: stat_data['cache_misses']),
        ('Bypass Hits',   lambda: hits_to_str(stat_data['cache_bypass_hits'], stat_data['cache_bypass_misses'])),
        ('Bypass Misses', lambda: stat_data['cache_bypass_misses']),
        ('Bypassed',      lambda: pretty_size(stat_data['bypassed'])),
    ]

    for (sysfs_name, stat_display_name) in stat_types:
        if len(stats) > 0 and sysfs_name not in stats:
            continue
        stat_data = {}
        for attr in attrs:
            val = file_to_line('%s/stats_%s/%s' % (sysfs_path, sysfs_name, attr))
            stat_data[attr] = val
        for (display_name, str_func) in display:
            d = '%s%s %s' % (indent_str, stat_display_name, display_name)
            print('%-*s%s' % (MAX_KEY_LENGTH, d, str_func()))


def dump_bcache(bcache_sysfs_path, stats, print_subdevices, device):
    '''Dump bcache stats'''
#    global devnum_map
    def fmt_cachesize(val):
        return '%s\t(%d%%)' % (format_sectors(val), 100.0 * val / cache_sectors)

    attrs = [
#        (None,                           'Device',             lambda x: '%s (%s)' % (devnum_map.get(device, '?'), device)),
        (None,                           'UUID',               lambda x: os.path.basename(bcache_sysfs_path)),
        ('block_size',                   'Block Size',         pretty_size),
        ('bucket_size',                  'Bucket Size',        pretty_size),
        ('congested',                    'Congested?',         str_to_bool),
        ('congested_read_threshold_us',  'Read Congestion',    lambda x: '%.1fms' % (int(x) / 1000)),
        ('congested_write_threshold_us', 'Write Congestion',   lambda x: '%.1fms' % (int(x) / 1000)),
        (None,                           'Total Cache Size',   lambda x: format_sectors(cache_sectors)),
        (None,                           'Total Cache Used',   lambda x: fmt_cachesize(cache_used_sectors)),
        (None,                           'Total Cache Unused', lambda x: fmt_cachesize(cache_unused_sectors)),
        ('dirty_data',                   'Dirty Data',         lambda x: fmt_cachesize(interpret_sectors(x))),
        ('cache_available_percent',      'Evictable Cache',    lambda x: '%s\t(%s%%)' % (format_sectors(float(x) * cache_sectors / 100), x)),
        (None,                           'Replacement Policy', lambda x: replacement_policies.pop() if len(replacement_policies) == 1 else '(Unknown)'),
        (None,                           'Cache Mode',         lambda x: cache_modes.pop() if len(cache_modes) == 1 else '(Unknown)'),
    ]

    # Calculate aggregate data
    cache_sectors = 0
    cache_unused_sectors = 0
    cache_modes = set()
    replacement_policies = set()
    for obj in os.listdir(bcache_sysfs_path):
        if not os.path.isdir('%s/%s' % (bcache_sysfs_path, obj)):
            continue
        if obj.startswith('cache'):
            cache_size = int(file_to_line('%s/%s/../size' % (bcache_sysfs_path, obj)))
            cache_sectors += cache_size
            cstats = get_cache_priority_stats('%s/%s' % (bcache_sysfs_path, obj))
            unused_size = float(cstats['Unused'][:-1]) * cache_size / 100
            cache_unused_sectors += unused_size
            replacement_policies.add(file_to_line('%s/%s/cache_replacement_policy' % (bcache_sysfs_path, obj)))
        elif obj.startswith('bdev'):
            cache_modes.add(file_to_line('%s/%s/cache_mode' % (bcache_sysfs_path, obj)))
    cache_used_sectors = cache_sectors - cache_unused_sectors

    # Dump basic stats
    print("--- bcache ---")
    for (sysfs_name, display_name, conversion_func) in attrs:
        if sysfs_name is not None:
            val = file_to_line('%s/%s' % (bcache_sysfs_path, sysfs_name))
        else:
            val = None
        if conversion_func is not None:
            val = conversion_func(val)
        if display_name is None:
            display_name = sysfs_name
        print('%-*s%s' % (MAX_KEY_LENGTH, display_name, val))
    dump_stats(bcache_sysfs_path, '', stats)

    # Dump sub-device stats
    if not print_subdevices:
        return
    for obj in os.listdir(bcache_sysfs_path):
        if not os.path.isdir('%s/%s' % (bcache_sysfs_path, obj)):
            continue
        if obj.startswith('bdev'):
            dump_bdev('%s/%s' % (bcache_sysfs_path, obj))
            dump_stats('%s/%s' % (bcache_sysfs_path, obj), '  ', stats)
        elif obj.startswith('cache'):
            dump_cachedev('%s/%s' % (bcache_sysfs_path, obj))

def map_uuid_to_device():
    '''Map bcache UUIDs to device files.'''
    ret = {}

    SYSFS_BLOCK_PATH = '/sys/block/'

    for bdev in os.listdir(SYSFS_BLOCK_PATH):
        link = os.path.join(SYSFS_BLOCK_PATH, bdev)
        link = os.path.join(link, 'bcache/cache')

        if not os.path.islink(link):
            continue

        basename = os.path.basename(os.readlink(link))
        ret[basename] = bdev #file_to_line('%s%s/dev' % (SYSFS_BLOCK_PATH, bdev))
    return ret

def map_devnum_to_device():
    '''Map device numbers to device files.'''
    global DEV_BLOCK_PATH
    ret = {}

    for bdev in os.listdir(DEV_BLOCK_PATH):
        ret[bdev] = os.path.realpath('%s%s' % (DEV_BLOCK_PATH, bdev))

    return ret

def main():
    '''Main function'''
    stats = set()
    reset_stats = False
    print_subdevices = False
    run_gc = False

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--help',              help='show this help message and exit',       action='store_true')
    parser.add_argument('-f', '--five-minute', help='Print the last five minutes of stats.', action='store_true')
    parser.add_argument('-h', '--hour',        help='Print the last hour of stats.',         action='store_true')
    parser.add_argument('-d', '--day',         help='Print the last day of stats.',          action='store_true')
    parser.add_argument('-t', '--total',       help='Print total stats.',                    action='store_true')
    parser.add_argument('-a', '--all',         help='Print all stats.',                      action='store_true')
    parser.add_argument('-r', '--reset-stats', help='Reset stats after printing them.',      action='store_true')
    parser.add_argument('-s', '--sub-status',  help='Print subdevice status.',               action='store_true')
    parser.add_argument('-g', '--gc',          help='Invoke GC before printing status.',     action='store_true')
    args = parser.parse_args()

    if args.help:
        parser.print_help()
        return 0

    if args.five_minute:
        stats.add('five_minute')
    if args.hour:
        stats.add('hour')
    if args.day:
        stats.add('day')
    if args.total:
        stats.add('total')
    if args.all:
        stats.add('five_minute')
        stats.add('hour')
        stats.add('day')
        stats.add('total')
    if args.reset_stats:
        reset_stats = True
    if args.sub_status:
        print_subdevices = True
    if args.gc:
        run_gc = True

    if not stats:
        stats.add('total')

    uuid_map = map_uuid_to_device()
    #devnum_map = map_devnum_to_device()

    for cache in os.listdir(SYSFS_BCACHE_PATH):
        cache_dir = os.path.join(SYSFS_BCACHE_PATH, cache)
        if not os.path.isdir(cache_dir):
            continue

        if run_gc:
            with open('%s%s/internal/trigger_gc' % (SYSFS_BCACHE_PATH, cache), 'w') as fd:
                fd.write('1\n')

        dump_bcache(cache_dir, stats, print_subdevices, uuid_map.get(cache, '?'))

        if reset_stats:
            with open('%s%s/clear_stats' % (SYSFS_BCACHE_PATH, cache), 'w') as fd:
                fd.write('1\n')

VALUE_SELECT = 1
VALUE_SIZE = 2
VALUE_INFO = 3

def format_sectors(x):
    '''Pretty print a sector count.'''
    sectors = int(x)
    asectors = abs(sectors)

    if asectors == 0:
        return '0B'
    elif asectors < 2048:
        return '%.2fKiB' % (sectors / 2)
    elif asectors < 2097152:
        return '%.2fMiB' % (sectors / 2048)
    elif asectors < 2147483648:
        return '%.2fGiB' % (sectors / 2097152)
    else:
        return '%.2fTiB' % (sectors / 2147483648)

def interpret_sectors(x):
    '''Interpret a pretty-printed disk size.'''
    factors = {
        'k': 1 << 10,
        'M': 1 << 20,
        'G': 1 << 30,
        'T': 1 << 40,
        'P': 1 << 50,
        'E': 1 << 60,
        'Z': 1 << 70,
        'Y': 1 << 80,
    }

    if len(x)>0:
        factor = 1
        if x[-1] in factors:
            factor = factors[x[-1]]
            x = x[:-1]
        return int(float(x) * factor / 512)
    else:
        return 1


class Base(object):
    def read_value(self):
        i = -1
        for filename, showname, tp in self.attrs:
            i += 1
            if tp == VALUE_SIZE:
                v = open(os.path.join(self.path, filename)).read()
                v = float(v)

            if tp == VALUE_SELECT:
                v = open(os.path.join(self.path, filename)).read()
                t = v.split()
                for tt in t:
                    if tt[0] == '[':
                        v = tt[1:-1]
                        break

            if tp == VALUE_INFO:
                filename, key = filename.split('|')
                for line in open(os.path.join(self.path, filename)).readlines():
                    k, v = line.split(':')
                    if k.strip() == key:
                        v = v.strip()
                        break

            self.attrs[i].append(v)

    def print_value(self, filter = None):
        print self.name

        for item in self.attrs:
            v = item[-1]
            if item[2] == VALUE_SIZE:
                v =  format_sectors(v)

            print '    ', item[1].ljust(15), ':', v


class CacheSet(Base):
    def __init__(self, path):
        self.attrs = []

        self.bdev = []
        self.cdev = []
        self.uuid = os.path.basename(path)
        self.path = path
        self.name = "BCache: %s" % self.uuid

        fs = os.listdir(path)
        for f in fs:
            p = os.path.join(path, f)

            if re.search('^bdev\d+$', f):
                p = os.readlink(p)
                p = os.path.join(path, p)
                self.bdev.append(CacheBdev(p))
                continue

            if re.search('^cache\d+$', f):
                p = os.readlink(p)
                p = os.path.join(path, p)
                self.cdev.append(CacheCdev(p))
                continue
        self.read_value()



class CacheBdev(Base):

    def __init__(self, path):
        self.attrs = []
        self.attrs.append(['../size',   'Size',       VALUE_SIZE])
        self.attrs.append(['cache_mode', 'Cache Mode', VALUE_SELECT])
        self.attrs.append(['dirty_data', 'Dirty Data', VALUE_SIZE])

        self.real_dev = path.split('/')[-2]
        self.path = path
        self.read_value()
        self.name = '--- Backing Device: %s ---' % self.real_dev

    def stats(self):
        path = 'stats_total'
        path = os.path.join(self.path, path)

        t1 = ['cache_hits', 'cache_misses', 'cache_hit_ratio' ]
        t2 = ['HITS',       'MISSES',       'RATIO'           ]
        t3 = [0,            0,              0                 ]

        for i, f in enumerate(t1):
            p = os.path.join(path, f)
            t3[i] = open(p).read().strip()

        w = max(map(len, t2))

        print '  ', ' '.join([x.rjust(w) for x in t2])
        print '  ', ' '.join([x.rjust(w) for x in t3])

    def print_value(self):
        Base.print_value(self)
        self.stats()


class CacheCdev(Base):

    def __init__(self, path):
        self.attrs = []
        self.attrs.append(['../size',   'Size',       VALUE_SIZE])
        self.attrs.append(['cache_replacement_policy', 'Replace Policy', VALUE_SELECT])
        self.attrs.append(['priority_stats|Unused', 'Unused', VALUE_INFO])

        self.real_dev = path.split('/')[-2]
        self.path = path
        self.read_value()
        self.name = '--- Cache Device: %s ---' % self.real_dev





def main():
    sets = []
    for cache in os.listdir(SYSFS_BCACHE_PATH):
        cache_dir = os.path.join(SYSFS_BCACHE_PATH, cache)
        if not os.path.isdir(cache_dir):
            continue
        sets.append(CacheSet(cache_dir))


    for s in sets:
        s.print_value()

        for c in s.cdev:
            c.print_value()

        for b in s.bdev:
            b.print_value()



























if __name__ == '__main__':
    main()

