class POCacheRet(object):
    def __init__(self, key, cleared=None, reloaded=None, expired=None):
        self.key = key
        if cleared is not None:
            self.cleared = cleared
        if reloaded is not None:
            self.reloaded = reloaded
        if expired is not None:
            self.expired = expired