def parse_parsing_callbacks(cbs):
    if cbs is None:
        cbs = dict()
    if 'after_filtering' not in cbs:
        cbs['after_filtering'] = lambda *args: args
    return cbs
