#! /usr/bin/python -t


import os
import sys


# Decent (UK/US English only) number formatting.
import locale
locale.setlocale(locale.LC_ALL, '') 

def loc_num(x):
    """ Return a string of a number in the readable "locale" format. """
    return locale.format("%d", int(x), True)
def kmgtp_num(x):
    """ Return a string of a number in the MEM size format, Ie. "30 MB". """
    ends = [" ", "K", "M", "G", "T", "P"]
    while len(ends) and x > 1024:
        ends.pop(0)
        x /= 1024
    return "%u %s" % (x, ends[0])

def cmdline_from_pid(pid):
    """ Fetch command line from a process id. """
    try:
        cmdline= open("/proc/%i/cmdline" %pid).readlines()[0]
        return " ".join(cmdline.split("\x00")).rstrip()
    except:
        return ""

pids = {}
for d in os.listdir("/proc/"):
    try:
        pid = int(d)
        pids[pid] = lambda x: x
        pids[pid].files = set()
        pids[pid].vsz   = 0
        pids[pid].s_size          = 0
        pids[pid].s_rss           = 0
        pids[pid].s_shared_clean  = 0
        pids[pid].s_shared_dirty  = 0
        pids[pid].s_private_clean = 0
        pids[pid].s_private_dirty = 0
        pids[pid].referenced      = 0
        pids[pid].name            = cmdline_from_pid(pid)
    except:
        pass

def map_sz(x):
    """ Work out vsz from mapping range. """
    (beg, end) = x.split('-')
    return (int(end, 16) - int(beg, 16))

files = {}
for pid in pids.keys():
    try:
        try:
            lines = open("/proc/%d/smaps" % pid).readlines()
            smaps = True
        except:
            lines = open("/proc/%d/maps" % pid).readlines()
            smaps = False

        off = 0
        while off < len(lines):
            line = lines[off]
            off += 1
            try:
                int(line[0])
            except:
                continue

            data = line.split(None, 5)
            try:
                ino = int(data[4])
                dev = int(data[3].split(":", 2)[0], 16)
            except:
                print "DBG: Bad line:", lines[off - 1]
                print "DBG:     data=", data
                continue
                
            if dev == 0:
                continue
            if ino == 0:
                continue
            if '(deleted)' not in data[5]:
                continue

            key = "%s:%d" % (data[3], ino)
            if key not in files:
                files[key] = lambda x: x # Hack
                
                files[key].s_size          = 0
                files[key].s_rss           = 0
                files[key].s_shared_clean  = 0
                files[key].s_shared_dirty  = 0
                files[key].s_private_clean = 0
                files[key].s_private_dirty = 0
                files[key].referenced      = 0
                
                files[key].vsz  = 0
                files[key].pids = set()
                files[key].name = data[5]
                
            num = map_sz(data[0])
            pids[pid].vsz  += num
            pids[pid].files.update([key])
            files[key].vsz += num
            files[key].pids.update([pid])
            try:
                if smaps:
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_size += num
                    files[key].s_size          += num
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_rss            += num
                    files[key].s_rss           += num
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_shared_clean   += num
                    files[key].s_shared_clean  += num
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_shared_dirty   += num
                    files[key].s_shared_dirty  += num
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_private_clean  += num
                    files[key].s_private_clean += num
                    off += 1
                    num = int(lines[off].split(None, 3)[1])
                    pids[pid].s_private_dirty  += num
                    files[key].s_private_dirty += num
                    off += 1
                    try:
                        num = int(lines[off].split(None, 3)[1])
                        pids[pid].referenced   += num
                        files[key].referenced  += num
                        off += 1
                    except:
                        pass
            except:
                print "DBG: Bad data:", lines[off - 1]
                
    except:
        pass

vsz             = 0
s_size          = 0
s_rss           = 0
s_shared_clean  = 0
s_shared_dirty  = 0
s_private_clean = 0
s_private_dirty = 0
referenced      = 0

out_type = "files"
if len(sys.argv) > 1 and sys.argv[1] == "pids":
    out_type = "pids"
if len(sys.argv) > 1 and sys.argv[1] == "summary":
    out_type = "summary"

for x in files.values():
    vsz             += x.vsz
    s_size          += x.s_size
    s_rss           += x.s_rss
    s_shared_clean  += x.s_shared_clean
    s_shared_dirty  += x.s_shared_dirty
    s_private_clean += x.s_private_clean
    s_private_dirty += x.s_private_dirty
    referenced      += x.referenced

    if out_type == "files":
        print "%5sB:" % kmgtp_num(x.vsz), x.name,
        print "\ts_size          = %5sB" % kmgtp_num(x.s_size * 1024)
        print "\ts_rss           = %5sB" % kmgtp_num(x.s_rss * 1024)
        print "\ts_shared_clean  = %5sB" % kmgtp_num(x.s_shared_clean * 1024)
        print "\ts_shared_dirty  = %5sB" % kmgtp_num(x.s_shared_dirty * 1024)
        print "\ts_private_clean = %5sB" % kmgtp_num(x.s_private_clean * 1024)
        print "\ts_private_dirty = %5sB" % kmgtp_num(x.s_private_dirty * 1024)
        print "\treferenced      = %5sB" % kmgtp_num(x.referenced * 1024)
        for pid in frozenset(x.pids):
            print "\t\t", pid, pids[pid].name


for pid in pids.keys():
    if not pids[pid].vsz:
         del pids[pid]

if out_type == "pids":
    for pid in pids.keys():
        print "%5sB:" % kmgtp_num(pids[pid].vsz), pid, pids[pid].name
        print "\ts_size          = %5sB" % kmgtp_num(pids[pid].s_size * 1024)
        print "\ts_rss           = %5sB" % kmgtp_num(pids[pid].s_rss * 1024)
        print "\ts_shared_clean  = %5sB" % kmgtp_num(pids[pid].s_shared_clean * 1024)
        print "\ts_shared_dirty  = %5sB" % kmgtp_num(pids[pid].s_shared_dirty * 1024)
        print "\ts_private_clean = %5sB" % kmgtp_num(pids[pid].s_private_clean * 1024)
        print "\ts_private_dirty = %5sB" % kmgtp_num(pids[pid].s_private_dirty * 1024)
        print "\treferenced      = %5sB" % kmgtp_num(pids[pid].referenced * 1024)
        for key in pids[pid].files:
            print "\t\t", files[key].name,

print "\
=============================================================================="
print "files           = %8s" % loc_num(len(files))
print "pids            = %8s" % loc_num(len(pids.keys()))
print "vsz             = %5sB" % kmgtp_num(vsz)
print "\
------------------------------------------------------------------------------"
print "s_size          = %5sB" % kmgtp_num(s_size * 1024)
print "s_rss           = %5sB" % kmgtp_num(s_rss * 1024)
print "s_shared_clean  = %5sB" % kmgtp_num(s_shared_clean * 1024)
print "s_shared_dirty  = %5sB" % kmgtp_num(s_shared_dirty * 1024)
print "s_private_clean = %5sB" % kmgtp_num(s_private_clean * 1024)
print "s_private_dirty = %5sB" % kmgtp_num(s_private_dirty * 1024)
print "referenced      = %5sB" % kmgtp_num(referenced * 1024)
print "\
=============================================================================="