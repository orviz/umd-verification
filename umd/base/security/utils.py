def get_filelist_from_find(r):
    return [finfo.split()[-1] for finfo in r.split('\n')]
