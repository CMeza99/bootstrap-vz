from abc import ABCMeta


class _Release(object):
    __metaclass__ = ABCMeta

    def __init__(self, codename, version):
        self.codename = codename
        self.version = version

    def __cmp__(self, other):
        return self.version - other.version

    def __str__(self):
        return self.codename

    def __getstate__(self):
        state = self.__dict__.copy()
        state['__class__'] = self.__module__ + '.' + self.__class__.__name__
        return state

    def __setstate__(self, state):
        for key in state:
            self.__dict__[key] = state[key]

    # TODO: add metaproperty isDebian


class ReleaseDebian(_Release):
    pass


class ReleaseUbuntu(_Release):
    def __init__(self, codename, version, debian):
        self.debian = debian
        super(ReleaseUbuntu, self).__init__(codename, version)

    def __cmp__(self, other):
        if isinstance(other, ReleaseDebian):
            return self.debian.version - other.version
        elif not isinstance(other, ReleaseUbuntu):
            raise UnknownReleaseException('Unable to compare release with {}'.format(type(other)))
        return self.version - other.version


class _ReleaseAlias(_Release):
    def __init__(self, alias, release):
        self.alias = alias
        self.release = release
        super(_ReleaseAlias, self).__init__(self.release.codename, self.release.version)

    def __str__(self):
        return self.alias


sid = ReleaseDebian('sid', 11)
buster = ReleaseDebian('buster', 10)
stretch = ReleaseDebian('stretch', 9)
jessie = ReleaseDebian('jessie', 8)
wheezy = ReleaseDebian('wheezy', 7)
squeeze = ReleaseDebian('squeeze', 6.0)
lenny = ReleaseDebian('lenny', 5.0)
etch = ReleaseDebian('etch', 4.0)
sarge = ReleaseDebian('sarge', 3.1)
woody = ReleaseDebian('woody', 3.0)
potato = ReleaseDebian('potato', 2.2)
slink = ReleaseDebian('slink', 2.1)
hamm = ReleaseDebian('hamm', 2.0)
bo = ReleaseDebian('bo', 1.3)
rex = ReleaseDebian('rex', 1.2)
buzz = ReleaseDebian('buzz', 1.1)

unstable = _ReleaseAlias('unstable', sid)
testing = _ReleaseAlias('testing', buster)
stable = _ReleaseAlias('stable', stretch)
oldstable = _ReleaseAlias('oldstable', jessie)


def get_release(release_name):
    """Normalizes the release codenames
    This allows tasks to query for release codenames rather than 'stable', 'unstable' etc.
    """
    from . import releases  # pylint: disable=import-self
    release = getattr(releases, release_name, None)
    if release is None or not isinstance(release, _Release):
        raise UnknownReleaseException('The release `{name}\' is unknown'.format(name=release))
    return release


class UnknownReleaseException(Exception):
    pass
