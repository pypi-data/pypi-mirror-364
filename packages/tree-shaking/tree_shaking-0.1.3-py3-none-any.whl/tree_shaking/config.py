import atexit
import hashlib
import typing as t
from functools import partial
from os.path import isabs

from lk_utils import fs

from .path_scope import path_scope


class T:
    AnyPath = str
    #   - absolute path, or relative path based on the config file itself.
    #   - separated by '/', no '\\'.
    #   - for relative path, must start with './' or '../'.
    #   - for directory, path must end with '/'.
    #   - use '<root>' to indicate the root directory.
    #       for example: '<root>/venv'
    #   - use '<module>' to indicate the module directory.
    #       (it locates at `<python-tree-shaking-project>/data/module_graphs`)
    AnyDirPath = str
    AnyScriptPath = str
    #   must be a '.py' script file.
    #   other rules same as `AnyPath`.
    GraphId = str
    #   just the md5 value of its abspath. see `_hash_path_to_uid()`.
    IgnoredName = str
    #   - must be lower case.
    #   - use underscore, not hyphen.
    #   - use correct name.
    #   for example:
    #       wrong       right
    #       -----       -------
    #       IPython     ipython
    #       lk-utils    lk_utils
    #       pillow      pil
    NormPath = str
    #   normalized path, must be absolute path.
    
    # noinspection PyTypedDict
    Config0 = t.TypedDict('Config0', {
        'root'        : AnyDirPath,
        'search_paths': t.List[AnyDirPath],
        'entries'     : t.List[AnyScriptPath],
        'ignores'     : t.List[IgnoredName],
    }, total=False)
    """
        {
            'root': dirpath,
            'search_paths': (dirpath, ...),
            'entries': (script_path, ...),
            'ignores': (module_name, ...),
            #   module_name is case sensitive.
        }
    """
    
    # noinspection PyTypedDict
    Config1 = t.TypedDict('Config1', {
        'root'        : NormPath,
        'search_paths': t.List[NormPath],
        'entries'     : t.Dict[NormPath, GraphId],
        'ignores'     : t.Union[t.FrozenSet[str], t.Tuple[str, ...]],
        # 'exports'     : t.Sequence[str],
    })
    
    Config = Config1


graphs_root = fs.xpath('_cache/module_graphs')


def parse_config(file: str, _save: bool = False) -> T.Config:
    """
    file: see example at `examples/depsland_modules.yaml`.
        - the file ext must be '.yaml' or '.yml'.
        - we suggest using 'xxx-modules.yaml', 'xxx_modules.yaml' or just
        'modules.yaml' as the file name.
    """
    cfg_file: str = fs.abspath(file)
    cfg_dir: str = fs.parent(cfg_file)
    cfg0: T.Config0 = fs.load(cfg_file)
    cfg1: T.Config1 = {
        'root'        : '',
        'search_paths': [],
        'entries'     : {},
        'ignores'     : (),
    }
    
    # 1
    if isabs(cfg0['root']):
        cfg1['root'] = fs.normpath(cfg0['root'])
    else:
        cfg1['root'] = fs.normpath('{}/{}'.format(cfg_dir, cfg0['root']))
    
    # 2
    pathfmt = partial(_format_path, root=cfg1['root'], base=cfg_dir)
    
    temp = cfg1['search_paths']
    for p in map(pathfmt, cfg0['search_paths']):
        temp.append(p)
        path_scope.add_scope(p)
    
    # 3
    temp = cfg1['entries']
    for p in cfg0['entries']:
        p = pathfmt(p)
        temp[p] = hash_path_to_uid(p)
    
    # 4
    cfg1['ignores'] = frozenset(cfg0.get('ignores', ()))
    
    if _save:
        atexit.register(partial(_save_graph_alias, cfg1))
    
    # print(cfg1, ':l')
    return cfg1


def hash_path_to_uid(abspath: str) -> str:
    return hashlib.md5(abspath.encode()).hexdigest()


def _format_path(path: str, root: str, base: str) -> str:
    # note: return an absolute path.
    if path.startswith(('./', '../')):
        path = fs.normpath('{}/{}'.format(base, path))
    elif path.startswith('<root>'):
        path = fs.normpath(path.replace('<root>', root))
    elif path.startswith('<module>'):
        path = fs.normpath(path.replace('<module>', graphs_root))
    else:
        path = fs.normpath(path)
    assert isabs(path) and fs.exist(path), path
    return path


def _save_graph_alias(config: T.Config1) -> None:
    map_ = fs.load(fs.xpath('_cache/module_graphs_alias.yaml'), default={})
    if config['root'] in map_:
        if (
            set(config['entries'].values()) ==
            set(map_[config['root']].values())
        ):
            return
    map_[config['root']] = {
        # k.replace(config['root'], '<root>'): v
        fs.relpath(k, config['root']): v
        for k, v in config['entries'].items()
    }
    fs.dump(map_, fs.xpath('_cache/module_graphs_alias.yaml'), sort_keys=True)
