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

    # TODO: add metaproperty disto_name


class ReleaseDebian(_Release):
    pass


class ReleaseDerivate(_Release):
    def __init__(self, codename, version, debian):
        self.debian = debian
        super(ReleaseDerivate, self).__init__(codename, version)

    def __cmp__(self, other):
        if isinstance(other, ReleaseDebian):
            return self.debian.version - other.version
        elif not isinstance(other, ReleaseDerivate):
            raise UnknownReleaseException('Unable to compare release with {}'.format(type(other)))
        return self.version - other.version


class _ReleaseAlias(_Release):
    def __init__(self, alias, release):
        self.alias = alias
        self.release = release
        super(_ReleaseAlias, self).__init__(self.release.codename, self.release.version)

    def __str__(self):
        return self.alias


def get_release(release_name, distro_name=None):
    from .tools import config_get, rel_path
    release_map = config_get(rel_path(__file__, 'release-map.yml'), distro_name)
    distros = distro_name if distro_name else release_map.keys()

    release_info = dict()
    for distro in distros:
        release_info_tmp = release_map[distro].get(release_name, None)
        if not release_info_tmp:
            continue
        elif isinstance(release_info_tmp, dict):
            release_info = release_info_tmp
        else:
            release_info['version'] = release_info_tmp
        break

    if release_info is None or not distro:  # pylint: disable=undefined-loop-variable
        raise UnknownReleaseException(
            'The release `{name}\' is unknown'.format(name=release_name))
    elif 'alias' in release_info:
        return _ReleaseAlias(release_name, get_release(release_info['alias']))
    elif distro.lower() != 'debian':  # pylint: disable=undefined-loop-variable
        return ReleaseDerivate(release_name, release_info['version'], get_release(release_info['debian']))

    return ReleaseDebian(release_name, release_info['version'])


class UnknownReleaseException(Exception):
    pass


sid = get_release('sid')
buster = get_release('buster')
stretch = get_release('stretch')
jessie = get_release('jessie')
wheezy = get_release('wheezy')

unstable = get_release('unstable')
testing = get_release('testing')
stable = get_release('stable')
oldstable = get_release('oldstable')
