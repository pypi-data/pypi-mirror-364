"""
Profiling of doctests.
"""
import ast
import dataclasses
import doctest
import functools
import inspect
import linecache
import os
import pathlib
import re
import textwrap
import types

import pytest
from line_profiler.autoprofile.autoprofile import AstTreeModuleProfiler
from line_profiler.profiler_mixin import ByCountProfilerMixin
from line_profiler.autoprofile.util_static import modpath_to_modname

from . import importers, profiler
from ._typing import (
    TYPE_CHECKING,
    Dict, FrozenSet, List, Set, Tuple,
    Callable, Collection,
    NamedTuple,
    Type, TypeVar, ClassVar,
    Annotated, Any, Self,
    Literal, Union, Optional,
    ChainedIdentifier, Identifier, ImportPath,
    is_chained_identifier,
)
from .option_hooks import resolve_hooked_option
from .utils import NodeContextLabeller


if TYPE_CHECKING:
    from .importers import AutoProfStash


__all__ = (
    'DocstringLocator',
    'DoctestProfilingWarning',
    'get_runner_class',
)

# `line_profiler.LineProfiler.get_stats()` labels code objects by their
# `.co_qualname`s where available, so set it where appropriate
_SET_CODE_QUALNAME = hasattr(types.CodeType, 'co_qualname')

THIS_PACKAGE = (lambda: None).__module__.rpartition('.')[0]
DOCTEST_FILENAME_PATTERN = re.compile(r'^<doctest .*\[[0-9]+\]>$')
DefNode = TypeVar('DefNode', ast.FunctionDef, ast.AsyncFunctionDef)
NodeWithDocstring = Union[
    ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef,
]


# We have a forward reference to `~.importers.AutoProfStash`;
# lazy-import it


def __dir__() -> List[Annotated[str, Identifier]]:
    return sorted({*globals(), 'AutoProfStash'})


def __getattr__(attr: Annotated[str, Identifier]) -> Any:
    if attr != 'AutoProfStash':
        raise AttributeError(attr)
    ipath = ImportPath(THIS_PACKAGE + '.importers', 'AutoProfStash')
    Stash: Type['AutoProfStash'] = ipath.import_target()
    return globals().setdefault('AutoProfStash', Stash)


def get_member(
    cls: type, member: Annotated[str, Identifier],
) -> Tuple[Annotated[str, Identifier], Any]:
    xc: Union[AttributeError, None] = None
    try:
        return member, getattr(cls, member)
    except AttributeError as e:
        xc = e
    if member.startswith('__') and not member.endswith('__'):
        # Unmangle private names
        for cls in cls.mro():
            name = '_{}{}'.format(cls.__name__.lstrip('_'), member)
            try:
                return name, getattr(cls, name)
            except AttributeError:
                pass
    raise xc


run_name, base_run = get_member(doctest.DocTestRunner, '__run')


@functools.wraps(base_run)
def inner_run(self, *args, **kwargs):
    call = functools.partial(base_run, self, *args, **kwargs)
    if self.profiler is None:
        return call()
    with pytest.MonkeyPatch.context() as mp:
        set_attr = functools.partial(mp.setattr, doctest, raising=False)
        set_attr('exec', self.exec_doctest_example)
        set_attr('compile', self.compile_doctest_example)
        return call()


def no_op(*_, **__) -> None:
    pass


def is_python_file(path: Union[pathlib.Path, str]) -> bool:
    r"""
    Example
    -------
    >>> import os
    >>> import tempfile

    Use on a normal Python file:

    >>> is_python_file(__file__)
    True

    Use on a Python file without the `.py` suffix:

    >>> module = 'print("if this is printed, you\'re in trouble")'
    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     assert not os.listdir(tmpdir)
    ...     fname = os.path.join(tmpdir, 'some.random.file')
    ...     with open(fname, mode='w') as fobj:
    ...         print(module, file=fobj)
    ...     assert os.path.isfile(fname)
    ...     assert os.stat(fname).st_size
    ...     assert is_python_file(fname)

    Use on a non-file, and then a file that isn't valid Python:

    >>> with tempfile.TemporaryDirectory() as tmpdir:
    ...     assert not os.listdir(tmpdir)
    ...     fname = os.path.join(tmpdir, 'foo.py')
    ...     assert not is_python_file(fname)
    ...     with open(fname, mode='w') as fobj:
    ...         print('foo bar baz', file=fobj)
    ...     assert os.path.isfile(fname)
    ...     assert not is_python_file(fname)
    """
    try:
        path = pathlib.Path(path).resolve(strict=True)
    except OSError:
        return False
    return _is_python_file(str(path))


@functools.lru_cache()
def _is_python_file(real_path: str) -> bool:
    try:
        content = textwrap.dedent(''.join(linecache.getlines(real_path)))
    except (TypeError, ValueError, OSError):
        return False
    if not content:
        return True
    # Compiling should be safe, but wrap it in a block just in case
    wrapped_source = 'if False:\n' + textwrap.indent(content, '    ')
    try:
        compile(wrapped_source, '<...>', 'exec')
    except SyntaxError:
        return False
    else:
        return True


def _get_runner_base(config: pytest.Config) -> Tuple[
    Type[doctest.DocTestRunner],
    Union[
        Annotated[str, ChainedIdentifier],
        Collection[Annotated[str, ChainedIdentifier]],
    ],
]:
    """
    Get the correct `doctest.DocTestRunner` subclass to inherit from,
    and the name(s) to which the resultant class should be installed to.

    Notes
    -----
    If `pytest-doctestplus` is active, it would have `.unregister()`-ed
    `_pytest.doctest` from the list of plugins and replaced it (see
    `pytest_doctestplus.plugin.pytest_configure()`);
    meanwhile, just because `pytest_doctestplus` is on the plugin list
    doesn't mean its facilities are used.
    """
    load = config.pluginmanager.getplugin
    dt_plus: Union[types.ModuleType, None] = load('pytest_doctestplus')
    dt_vanilla: Union[types.ModuleType, None] = load('doctest')

    if dt_plus is None:
        use_dtp = False
    elif dt_vanilla:
        use_dtp = False
    else:
        use_dtp = True

    if use_dtp:
        assert dt_plus is not None
        BaseRunner = dt_plus.DebugRunnerPlus
        dest = '{0.__module__}.{0.__qualname__}'.format(BaseRunner)
    else:
        assert dt_vanilla is not None
        BaseRunner = dt_vanilla._init_runner_class()
        dest = f'{dt_vanilla.__name__}.RUNNER_CLASS'
    if TYPE_CHECKING:
        assert issubclass(BaseRunner, doctest.DocTestRunner)
    return BaseRunner, dest


def get_runner_class(
    config: pytest.Config, stash: Optional['AutoProfStash'] = None,
) -> Type[doctest.DocTestRunner]:
    """
    Factory function for building the appropriate
    `doctest.DocTestRunner` subclass.

    Notes
    -----
    - This function is supposed to be called after `pytest_configure()`.
    - Currently it checks whether the constructed class should inherit
      from either:
      - `_pytest.doctest.RUNNER_CLASS`, or
      - `pytest_doctestplus.plugin.DebugRunnerPlus`
    """
    if stash is None:
        try:
            stash = config.stash[importers.AUTOPROF_STASH_KEY]
        except KeyError:
            stash = importers.AutoProfStash.from_config(config)
    BaseRunner, dest = _get_runner_base(config)
    namespace = {
        'config': config,
        'stash': stash,
        '_installer': pytest.MonkeyPatch(),
        'installation_destinations': dest,
    }
    name = 'Profiling' + BaseRunner.__name__
    return type(name, (_RunnerMixin, BaseRunner), namespace)


class DoctestProfilingWarning(UserWarning):
    """
    Warnings for when doctests cannot be profiled.
    """


class _RunnerMixin:
    """
    Mixin class to work with a `doctest.DocTestRunner` subclass (e.g.
    `_pytest.doctest.RUNNER_CLASS`,
    `pytest_doctestplus.plugin.DebugRunnerPlus`) which handles doctest
    profiling.
    """
    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__(*args, **kwargs)
        # Set up the registry of cached properties, so that we can
        # invalidate them at once if needs be
        cached_property = functools.cached_property
        cls._cached_properties = frozenset(
            name for name, member in inspect.getmembers(cls)
            if isinstance(member, cached_property)
        )
        # Normalize `.installation_destinations`
        if 'installation_destinations' in vars(cls):
            dests: Collection = cls.installation_destinations or []
            if isinstance(dests, str):
                dests = dests,
            dests_ = frozenset(dests)
            if not all(is_chained_identifier(d) for d in dests_):
                raise TypeError(
                    '{0.__module__}.{0.__qualname__}'
                    '.installation_destinations = {1!r}: '
                    'expected collection of period-joined identifiers'
                    .format(cls, dests_)
                )
            cls.installation_destinations = dests_

    # Overrides

    @functools.wraps(exec)
    def exec_doctest_example(
        self, code: types.CodeType, /, globals: Optional[dict] = None,
        *args, **kwargs
    ) -> Any:
        """
        Override for `exec()`:
        - Insert the profiler into the test globals, if the test has
          been rewritten to incorporate import or function-/
          method-definition profiling
        - Feed the code object to be executed to the profiler, if the
          test should be profiled and if `--autoprof-doctests` is
          true
        """
        prof = self.profiler
        if globals is None:
            globals = {}
        if prof is None:  # No profiling
            return exec(code, globals, *args, **kwargs)
        profiler_wrapper: Union[_ProfilerWrapper, None] = getattr(
            self._current_example, self.profiler_wrapper_attr, None,
        )
        if profiler_wrapper is not None:
            globals['profile'] = profiler_wrapper
        dummy = types.SimpleNamespace(__code__=code)
        # Note: this may change `dummy.__code__` (see
        # `line_profiler._line_profiler.LineProfiler.add_function()`)
        prof.add_function(dummy)  # type: ignore[arg-type]
        with prof:
            return exec(dummy.__code__, globals, *args, **kwargs)

    @functools.wraps(compile)
    def compile_doctest_example(
        self, source: str, filename: str, *args, **kwargs
    ) -> types.CodeType:
        """
        Override for `compile()`:
        - Set `.co_name`, `.co_qualname` (if appropriate), and
          `.co_firstlineno` so that so that the profiler can retrieve
          the correct line numbers and filename
        - Do AST rewrite if the test should be profiled and if
          `--autoprof-rewrite-doctests` is true
        """
        if not (
            DOCTEST_FILENAME_PATTERN.match(filename) and
            self.autoprof_this_doctest
        ):
            return compile(source, filename, *args, **kwargs)
        # Note: `test.lineno` is just the location of the docstring, we
        # also need the offset of the example lines from that
        test = self.test
        example = self._current_example
        if test.lineno is None or test.filename is None:
            filename, lineno = '???', 0
        else:
            filename, lineno = test.filename, test.lineno + 1
        offset = example.lineno
        # Rename the code object so that it has all these info:
        # - File name
        # - Test name
        # - First line of the string from which the test is parsed
        info = _CodeObjectNameInfo(
            filename=filename, lineno=lineno, test=test.name,
        )
        # Rewrite the snippet to take care of import/definition
        # profiling
        if self.should_rewrite:
            rewriter = _ChunkRewriter(
                source, test.filename, self.autoprof_mod, self.autoprof_imports,
            )
            interactive = rewriter.profile()
            if rewriter.delta:
                prof = self.profiler
                assert prof is not None
                source = interactive
                profiler_wrapper = _ProfilerWrapper(prof, info, offset)
                setattr(example, self.profiler_wrapper_attr, profiler_wrapper)
        replaced = {
            'co_firstlineno': lineno + offset, 'co_name': info.to_co_name(),
        }
        if _SET_CODE_QUALNAME:
            replaced['co_qualname'] = replaced['co_name']
        return compile(source, filename, *args, **kwargs).replace(**replaced)

    # Override for `DocTestRunner._DocTestRunner__run()`
    locals()[run_name] = inner_run

    # (Un-)installation

    @classmethod
    def install(cls) -> None:
        """
        Override the base class, e.g. `_pytest.doctest.RUNNER_CLASS` or
        `pytest_doctestplus.plugin.DebugRunnerPlus`, so that doctest
        execution can be profiled.
        """
        if TYPE_CHECKING:
            assert issubclass(cls, doctest.DocTestRunner)
        cls.stash.DoctestRunner = cls
        for loc in cls.installation_destinations:
            cls._installer.setattr(loc, cls)

    @classmethod
    def uninstall(cls) -> None:
        """
        Undo the overriding of e.g. `_pytest.doctest.RUNNER_CLASS` or
        `pytest_doctestplus.plugin.DebugRunnerPlus`.
        """
        cls.stash.DoctestRunner = None
        cls._installer.undo()

    # Helper methods

    @staticmethod
    def _seek_module_frame(
        module: Annotated[str, ChainedIdentifier],
    ) -> types.FrameType:
        """
        Get the previous frame in the stack belonging to `module`.
        """
        frame = inspect.currentframe()
        if frame is None:
            raise RuntimeError('cannot get current frame')
        while True:
            frame = frame.f_back
            if frame is None:
                raise RuntimeError(
                    f'module = {module!r}: '
                    'reached call stack bottom without finding '
                    'the required frame'
                )
            spec = frame.f_globals.get('__spec__')
            if spec is None:
                raise RuntimeError('Cannot get `.__spec__` from frame globals')
            if spec.name == module:
                return frame

    def _invalidate_caches(self) -> None:
        remove_cache = self.__dict__.pop
        for name in self._cached_properties:
            remove_cache(name, None)

    @staticmethod
    def parse_code_object_name(name: str) -> '_CodeObjectNameInfo':
        """
        Return
        ------
        Named 3-tuple:
        - Path to the filename where the test is parsed (`.filename`)
        - Line number of the string the test is parsed (`.lineno`)
        - Name of the test (`.test`)
        """
        return _CodeObjectNameInfo.from_co_name(name)

    # Descriptors

    @property
    def _profiler(self) -> profiler.LineProfiler:
        return self.stash.profiler

    @property
    def profiler(self) -> Union[profiler.LineProfiler, None]:
        if self.autoprof_this_doctest:
            return self._profiler
        return None

    @property
    def _current_example(self) -> doctest.Example:
        """
        Hack to access the current example in methods where we can't
        explicitly pass it to.

        Notes
        -----
        Should not be accessed outside of
        `.{exec,compile}_doctest_example()`, as it is not guaranteed
        that the we land in the intended stack frame
        (`doctest.DocTestRunner.__run()`) and retrieve the correct
        `example`.
        """
        return self._seek_module_frame('doctest').f_locals['example']

    @property
    def test(self) -> doctest.DocTest:
        try:
            return vars(self)['test']
        except KeyError:
            raise AttributeError(f'{self!r} has no attribute `.test`') from None

    @test.setter
    def test(self, test: doctest.DocTest) -> None:
        vars(self)['test'] = test
        self._invalidate_caches()

    @test.deleter
    def test(self) -> None:
        try:
            del vars(self)['test']
        except KeyError:
            raise AttributeError(f'{self!r} has no attribute `.test`') from None
        self._invalidate_caches()

    # Config-parsing methods and properties

    get_autoprof_mod = staticmethod(
        importers.AutoProfImporter.get_autoprof_mod,
    )
    get_autoprof_imports = staticmethod(
        importers.AutoProfImporter.get_autoprof_imports,
    )
    get_autoprof_doctests = staticmethod(functools.partial(
        resolve_hooked_option, opt_or_dest='autoprof_doctests',
    ))
    get_autoprof_rewrite_doctests = staticmethod(functools.partial(
        resolve_hooked_option, opt_or_dest='autoprof_rewrite_doctests',
    ))

    @functools.cached_property
    def autoprof_imports(self) -> bool:
        return self.get_autoprof_imports(self.config)

    @functools.cached_property
    def autoprof_mod(self) -> List[str]:
        """
        Return
        ------
        List of strings that can be directly passed to
        `AstTreeProfiler(prof_mod=...)`
        """
        targets = [
            module if object is None else f'{module}.{object}'
            for module, object in self.get_autoprof_mod(self.config)
        ]
        filename = self.test.filename
        if self.autoprof_this_doctest:
            assert filename is not None
            targets += [filename]
        return targets

    @functools.cached_property
    def autoprof_this_doctest(self) -> bool:
        """
        Return
        ------
        Whether `.test` should be profiled (as resolved from
        `--autoprof-doctests` and `--autoprof-mod`)
        """
        test = self.test
        fname = test.filename
        test_name = test.name
        if fname is None:  # Can't trace nothing, give up
            return False
        autoprof_doctests = self.get_autoprof_doctests(self.config)
        if autoprof_doctests == 'all':
            # `--autoprof-doctests=all` -> all doctests profiled
            should_try_to_prof = True
        elif not autoprof_doctests:
            # `--autoprof-doctests=no` -> not profiled
            should_try_to_prof = False
        else:
            # Else, check `--autoprof-mod` to see if the test matches
            module_names: Set[
                Union[Annotated[str, ChainedIdentifier], None]
            ] = {
                modpath_to_modname(fname, hide_init=hide_init)
                for hide_init in (True, False)
            }
            targets: Set[Annotated[str, ChainedIdentifier]] = {
                module if object is None else f'{module}.{object}'
                for module, object in self.get_autoprof_mod(self.config)
                if module in module_names
            }
            should_try_to_prof = any(
                test_name == target or test_name.startswith(target + '.')
                for target in targets
            )
        # If the test should be profiled but isn't due to being
        # untractable (non-Python file, no line number, ...), take note
        # of that to later issue a warning
        if not should_try_to_prof:
            return False
        if test.lineno is None or not is_python_file(fname):
            self._profiler.non_profiled_doctests[fname].add(test_name)
            return False
        return True

    @functools.cached_property
    def should_rewrite(self) -> bool:
        return (
            self.autoprof_this_doctest and
            self.get_autoprof_rewrite_doctests(self.config)
        )

    # Class attributes (to be supplied by the factory function
    # `get_runner_class()`)

    profiler_wrapper_attr: ClassVar[Annotated[str, Identifier]] = (
        'profiler_wrapper'
    )

    # These should be supplied by `get_runner_class()`
    config: ClassVar[pytest.Config]
    stash: ClassVar[importers.AutoProfStash]
    installation_destinations: ClassVar[
        FrozenSet[Annotated[str, ChainedIdentifier]]
    ]
    _installer: ClassVar[pytest.MonkeyPatch]

    # This is calculated by `__init_subclass__()`
    _cached_properties: ClassVar[FrozenSet[Annotated[str, Identifier]]]


class _ChunkRewriter(AstTreeModuleProfiler):
    """
    Handle import and function-definition rewriting in doctests.

    Attributes
    ----------
    chunk
        Doctest snippet to be rewritten
    delta
        Number of added nodes
    """
    def __init__(self, chunk: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.chunk = chunk
        self.delta = 0

    def _get_script_ast_tree(self, _) -> ast.Interactive:
        """
        Override the base-class static method so that we build the
        AST tree based on the provided chunk instead of the content
        of the `script_file`.

        Notes
        -----
        Returns an `ast.Interactive` instead of `.Module`.
        """
        return ast.parse(self.chunk, mode='single')

    def _profile_ast_tree(
        self, tree: ast.Interactive, *args, **kwargs
    ) -> ast.Interactive:
        """
        Store the number of changed nodes.
        """
        count = self.count_nodes(tree)
        new_tree = super()._profile_ast_tree(tree, *args, **kwargs)
        self.delta = self.count_nodes(new_tree) - count
        return new_tree

    @classmethod
    def count_nodes(cls, node: ast.AST) -> int:
        counter = cls._NodeCounter()
        counter.visit(node)
        return counter.count

    chunk: str
    delta: int

    class _NodeCounter(ast.NodeVisitor):
        def __init__(self) -> None:
            self.count = 0

        def generic_visit(self, node: ast.AST) -> None:
            self.count += 1
            return super().generic_visit(node)


@dataclasses.dataclass
class _CodeObjectNameInfo:
    """
    Information placed into the `.co_name` of a doctest's compiled
    examples.

    Example
    -------
    >>> info = _CodeObjectNameInfo('foo.py', 42, '')
    >>> assert info.from_co_name(info.to_co_name()) == info
    """
    filename: str
    lineno: int
    test: str

    def to_co_name(self) -> str:
        return self.template.format(self)

    @classmethod
    def from_co_name(cls, co_name: str) -> Self:
        re_match = cls.regex.match(co_name)
        literal_eval = ast.literal_eval
        if not re_match:
            raise ValueError(
                f'co_name = {co_name!r}: '
                f'doesn\'t match the pattern {cls.template!r}'
            )
        return cls(*(
            literal_eval(group)
            for group in re_match.group('filename', 'lineno', 'test')
        ))

    regex: ClassVar[re.Pattern] = re.compile(
        r'^<auto-profiled doctest '
        r'''file=(?P<filename>(?P<fq>['"]).*(?P=fq)) '''
        r'ln=(?P<lineno>[0-9]+) '
        r'''test=(?P<test>(?P<tq>['"]).*(?P=tq))>$'''
    )
    template: ClassVar[str] = (
        '<auto-profiled doctest '
        'file={0.filename!r} ln={0.lineno!r} test={0.test!r}>'
    )


@dataclasses.dataclass
class _ProfilerWrapper(ByCountProfilerMixin):
    """
    Helper object which makes sure that the correct filename, test name,
    and line numbers get passed to `@profile` for auto-profiled
    function/method/etc. definitions.
    """
    profiler: profiler.LineProfiler
    info: _CodeObjectNameInfo
    offset: int

    @functools.wraps(profiler.LineProfiler.__call__)
    def __call__(self, func, *args, **kwargs):
        return self.profiler(self.wrap_callable(func), *args, **kwargs)

    @functools.wraps(profiler.LineProfiler.add_imported_function_or_module)
    def add_imported_function_or_module(self, *args, **kwargs):
        return self.profiler.add_imported_function_or_module(*args, **kwargs)

    def wrap_function(self, func: types.FunctionType) -> types.FunctionType:
        """
        Relabel the code object so that `LineProfiler` knows (how) to
        retrieve line location of definitions in doctests.
        """
        code = func.__code__
        info = self.info
        lineno = info.lineno + self.offset + code.co_firstlineno - 1
        replaced = {'co_firstlineno': lineno, 'co_name': info.to_co_name()}
        if _SET_CODE_QUALNAME:
            replaced['co_qualname'] = replaced['co_name']
        func.__code__ = code.replace(
            **replaced,  # type: ignore[arg-type]
        )
        return func

    wrap_async_generator = wrap_generator = wrap_coroutine = wrap_function


class DocstringLocInfo(NamedTuple):
    """
    Location info of a docstring.
    """
    docstring: str
    docstring_lineno: int
    host: Union[Literal[''], Annotated[str, ChainedIdentifier]]
    host_lineno: int


class DocstringLocator:
    """
    Helper object for locating the host object for a docstring.

    Notes
    -----
    Only handles statically-defined docstrings.
    """
    @classmethod
    def locate_docstring(
        cls,
        filename: str,
        lineno: Optional[int] = None,
        host_lineno: Optional[int] = None,
        test_name: Optional[Annotated[str, ChainedIdentifier]] = None,
        *,
        lineno_tolerance: int = 2,
        refresh_cache: bool = True,
    ) -> DocstringLocInfo:
        r"""
        Parameters
        ----------
        filename
            String path to the Python source file (should be
            import-able under the current `sys.path`)
        lineno, host_lineno, test_name
            Requirements for the docstring search

        Return
        ------
        Named 4-tuple of:
        - The docstring (`.docstring`)
        - The line number of the docstring (`.docstring_lineno`)
        - The qualified name of the host node (`.host`)
        - The line number of the host node (`.host_lineno`)

        Example
        -------
        >>> import functools
        >>> import textwrap
        >>>
        >>>
        >>> locate = functools.partial(
        ...     DocstringLocator.locate_docstring, __file__,
        ...     refresh_cache=False,
        ... )
        >>> func = locate.func.__func__
        >>> func_lineno = func.__code__.co_firstlineno
        >>> offset = 11  # XXX: update if this func is refactored
        >>> try:
        ...     loc1 = locate(host_lineno=func_lineno)
        ...     loc2 = locate(lineno=func_lineno + offset)
        ...     loc3 = locate(
        ...         test_name=f'{func.__module__}.{func.__qualname__}',
        ...     )
        ...     assert loc1 == loc2 == loc3
        ...     assert loc1.host == (
        ...         'DocstringLocator.locate_docstring'
        ...     )
        ...     assert (
        ...         textwrap.dedent(loc1.docstring).strip('\n')
        ...         .endswith('DocstringLocator.cache_clear()')
        ...     )
        ... finally:
        ...     DocstringLocator.cache_clear()
        """
        def check_name(loc: DocstringLocInfo) -> bool:
            host = loc.host
            if host:
                host_names = {f'{name}.{host}' for name in module_names}
            else:
                host_names = module_names
            return test_name in host_names

        def check_lineno(
            checked: Literal['docstring_lineno', 'host_lineno'],
            expected_lineno: int,
            loc: DocstringLocInfo,
        ) -> bool:
            lineno = getattr(loc, checked)
            return abs(lineno - expected_lineno) <= lineno_tolerance

        checks: List[Callable[[DocstringLocInfo], bool]] = []
        query: Dict[Annotated[str, Identifier], Any] = {'filename': filename}
        if lineno is not None:
            checks.append(
                functools.partial(check_lineno, 'docstring_lineno', lineno),
            )
            query['lineno'] = lineno
        if host_lineno is not None:
            checks.append(
                functools.partial(check_lineno, 'host_lineno', host_lineno),
            )
            query['host_lineno'] = host_lineno
        if test_name is not None:
            checks.append(check_name)
            query['test_name'] = test_name
        if not checks:
            raise TypeError(
                'lineno = host_lineno = test_name = None: cannot all be `None`'
            )
        locs = cls.locate_all_docstrings(filename, refresh_cache)
        name, = module_names = {modpath_to_modname(filename)}
        if os.path.basename(filename) == '__init__.py':
            module_names.add(name + '.__init__')
        if lineno_tolerance is not None and lineno_tolerance < 0:
            lineno_tolerance = 0
        matches = {s for s in locs if all(check(s) for check in checks)}
        try:
            result, = matches
        except ValueError:
            raise ValueError(
                '{}: found {} match(es): {!r}'.format(
                    ', '.join(f'{k} = {v!r}' for k, v in query.items()),
                    len(matches),
                    matches,
                ),
            ) from None
        return result

    @classmethod
    def locate_all_docstrings(
        cls, filename: str, refresh_cache: bool = True,
    ) -> List[DocstringLocInfo]:
        r"""
        Parse `filename` into an `ast.Module`, and find the
        locations of all the class, function, and method docstring nodes
        that are publicly accessible.

        Return
        ------
        List of named 4-tuples of:
        - The docstring (`.docstring`)
        - The line number of the docstring (`.docstring_lineno`)
        - The qualified name of the host node (`.host`)
        - The line number of the host node (`.host_lineno`)

        Examples
        --------
        >>> import textwrap
        >>>
        >>>
        >>> def strip(s: str) -> str:
        ...     return textwrap.dedent(s).strip('\n')

        Finding the docstring of a method:

        >>> cls = DocstringLocator
        >>> locs = cls.locate_all_docstrings(__file__)
        >>> hosts = {loc.host for loc in locs}
        >>> this_method = f'{cls.__name__}.locate_all_docstrings'
        >>> assert {
        ...     f'{cls.__name__}.DocstringFinder',
        ...     this_method,
        ... } < hosts
        >>> this_docstring, = (
        ...     loc.docstring for loc in locs if loc.host == this_method
        ... )
        >>> assert (
        ...     strip(this_docstring)
        ...     .startswith('Parse `filename` into an `ast.Module`')
        ... )

        Finding the docstring of a class:

        >>> class_docstring_loc, = (
        ...     loc for loc in locs if loc.host == cls.__name__
        ... )
        >>> assert (  # Docstrings are dedented since Python 3.13
        ...     strip(class_docstring_loc.docstring)
        ...     == strip(cls.__doc__)
        ... )

        Finding the docstring of a module:

        >>> module_docstring_loc, = (
        ...     loc for loc in locs if loc.docstring_lineno == 1
        ... )
        >>> assert module_docstring_loc == (__doc__, 1, '', 1)
        """
        if not is_python_file(filename):
            raise ValueError(
                'filename = {filename!r}: expected a Python source file',
            )
        if refresh_cache:
            cls.cache_clear()
        filename = os.path.realpath(filename)
        try:
            cached = cls._cache[filename]
        except KeyError:
            # Label all the publically-accessible classes, functions,
            # and methods
            module = NodeContextLabeller().visit(
                ast.parse(''.join(linecache.getlines(filename))),
            )
            # Locate the docstrings
            finder = cls.DocstringFinder()
            finder.visit(module)
            cached = cls._cache.setdefault(filename, (module, finder.locs))
        return list(cached[1])

    @classmethod
    def cache_clear(cls) -> None:
        """
        Clear the cache.
        """
        linecache.clearcache()
        cls._cache.clear()

    class DocstringFinder(ast.NodeVisitor):
        """
        Helper object which crawls through the AST and finds docstrings.
        """
        def __init__(self) -> None:
            self.locs: List[DocstringLocInfo] = []

        def _visit_class_with_body(self, node: NodeWithDocstring) -> None:
            try:
                self.locs.append(self.get_docstring_loc_info(node))
            except (ValueError, TypeError, AttributeError):
                pass
            super().generic_visit(node)

        visit_Module = visit_ClassDef = _visit_class_with_body
        visit_FunctionDef = visit_AsyncFunctionDef = _visit_class_with_body

        @classmethod
        def get_docstring_loc_info(
            cls, node: NodeWithDocstring,
        ) -> DocstringLocInfo:
            host = getattr(node, cls.qualname_attr, '')
            if isinstance(node, ast.Module):
                # `ast.Module` nodes don't have a line number as of now
                lineno = getattr(node, 'lineno', 1)
            elif not host:
                raise ValueError(f'node = {node!r}: cannot find qualified name')
            elif node.decorator_list:
                lineno = min(nd.lineno for nd in (node, *node.decorator_list))
            else:
                lineno = node.lineno
            first_expr, *_ = getattr(node, 'body', [])
            docstring = first_expr.value.value
            if not (
                isinstance(first_expr, ast.Expr) and
                isinstance(first_expr.value, ast.Constant) and
                isinstance(docstring, str)
            ):
                raise TypeError(
                    f'node.body[0] = {first_expr!r}: '
                    'not an `ast.Expr` containing a constant-string node',
                )
            return DocstringLocInfo(docstring, first_expr.lineno, host, lineno)

        locs: List[DocstringLocInfo]
        qualname_attr: ClassVar[Annotated[str, Identifier]] = (
            NodeContextLabeller.qualname_attr
        )

    _cache: ClassVar[Dict[str, Tuple[ast.Module, List[DocstringLocInfo]]]] = {}
