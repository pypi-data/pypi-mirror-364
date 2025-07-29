r"""
center.base
===========

High-level utilities for computing a polynomial normal form of the centre
manifold around a collinear libration point of the spatial circular
restricted three body problem (CRTBP).

All heavy algebra is performed symbolically on packed coefficient arrays.
Only NumPy is used so the implementation is portable and fast.

References
----------
Jorba, À. (1999). "A Methodology for the Numerical Computation of Normal Forms, Centre
Manifolds and First Integrals of Hamiltonian Systems".

Zhang, H. Q., Li, S. (2001). "Improved semi-analytical computation of center
manifolds near collinear libration points".
"""

from dataclasses import asdict
from typing import (TYPE_CHECKING, Any, Callable, Dict, Iterable, List,
                    Optional, Tuple, Union)

import numpy as np

from hiten.algorithms.hamiltonian.center._lie import (_evaluate_transform,
                                                      _lie_expansion)
from hiten.algorithms.hamiltonian.center._lie import \
    _lie_transform as _lie_transform_partial
from hiten.algorithms.hamiltonian.hamiltonian import (
    _build_physical_hamiltonian_collinear,
    _build_physical_hamiltonian_triangular)
# Full ("complete") normal form Lie transform
from hiten.algorithms.hamiltonian.normal._lie import \
    _lie_transform as _lie_transform_full
from hiten.algorithms.hamiltonian.transforms import (_coordlocal2realmodal,
                                                     _coordrealmodal2local,
                                                     _local2synodic_collinear,
                                                     _local2synodic_triangular,
                                                     _polylocal2realmodal,
                                                     _polyrealmodal2local,
                                                     _solve_complex,
                                                     _solve_real,
                                                     _substitute_complex,
                                                     _substitute_real,
                                                     _synodic2local_collinear,
                                                     _synodic2local_triangular)
from hiten.algorithms.poincare.config import _get_section_config
from hiten.algorithms.poincare.map import _solve_missing_coord
from hiten.algorithms.polynomial.base import (_create_encode_dict_from_clmo,
                                              _decode_multiindex,
                                              _init_index_tables)
from hiten.system.libration.base import LibrationPoint
from hiten.system.libration.collinear import CollinearPoint, L3Point
from hiten.system.libration.triangular import TriangularPoint
from hiten.utils.io import _load_center_manifold, _save_center_manifold
from hiten.utils.log_config import logger
from hiten.utils.printing import _format_poly_table

if TYPE_CHECKING:
    from hiten.algorithms.poincare.base import _PoincareMap


class CenterManifold:
    r"""
    Centre manifold normal-form builder.

    Parameters
    ----------
    point : hiten.system.libration.collinear.CollinearPoint
        Collinear libration point about which the normal form is computed.
    max_degree : int
        Maximum total degree :math:`N` of the polynomial truncation.

    Attributes
    ----------
    point : hiten.system.libration.collinear.CollinearPoint
        The libration point about which the normal form is computed.
    max_degree : int
        The maximum total degree of the polynomial truncation. Can be changed,
        which will invalidate the cache.
    psi, clmo : numpy.ndarray
        Index tables used to pack and unpack multivariate monomials.
    encode_dict_list : list of dict
        Helper structures for encoding multi-indices.
    _cache : dict
        Stores intermediate polynomial objects keyed by tuples to avoid
        recomputation.
    _poincare_maps : Dict[Tuple[float, tuple], hiten.algorithms.poincare.base._PoincareMap]
        Lazy cached instances of the Poincaré return maps.

    Notes
    -----
    All heavy computations are cached. Calling :py:meth:`compute` more than once
    with the same *max_degree* is inexpensive because it reuses cached results.
    """
    def __init__(self, point: LibrationPoint, max_degree: int):
        self._point = point
        self._max_degree = max_degree

        if isinstance(self._point, CollinearPoint):
            self._local2synodic = _local2synodic_collinear
            self._synodic2local = _synodic2local_collinear
            self._build_hamiltonian = _build_physical_hamiltonian_collinear
            self._mix_pairs = (1, 2)

            if isinstance(self._point, L3Point):
                logger.warning("L3 point has not been verified for centre manifold / normal form computations!")

        elif isinstance(self._point, TriangularPoint):
            logger.warning("Triangular points have not been verified for centre manifold / normal form computations!")
            self._local2synodic = _local2synodic_triangular
            self._synodic2local = _synodic2local_triangular
            self._build_hamiltonian = _build_physical_hamiltonian_triangular
            self._mix_pairs = (0, 1, 2)

        else:
            raise ValueError(f"Unsupported libration point type: {type(self._point)}")

        self._psi, self._clmo = _init_index_tables(self._max_degree)
        self._encode_dict_list = _create_encode_dict_from_clmo(self._clmo)
        self._cache = {}
        self._poincare_maps: Dict[Tuple[float, tuple], "_PoincareMap"] = {}

    @property
    def point(self) -> LibrationPoint:
        """The libration point about which the normal form is computed."""
        return self._point

    @property
    def max_degree(self) -> int:
        """The maximum total degree of the polynomial truncation."""
        return self._max_degree

    @max_degree.setter
    def max_degree(self, value: int):
        """
        Set a new maximum degree, which invalidates all cached data.
        """
        if not isinstance(value, int) or value <= 0:
            raise ValueError("max_degree must be a positive integer.")
            
        if value != self._max_degree:
            logger.info(
                f"Maximum degree changed from {self._max_degree} to {value}. "
                "Invalidating all cached data."
            )
            self._max_degree = value
            self._psi, self._clmo = _init_index_tables(self._max_degree)
            self._encode_dict_list = _create_encode_dict_from_clmo(self._clmo)
            self.cache_clear()

    def __str__(self):
        return f"CenterManifold(point={self._point}, max_degree={self._max_degree})" 
    
    def __repr__(self):
        return f"CenterManifold(point={self._point}, max_degree={self._max_degree})"
    
    def __getstate__(self):
        return {
            "_point": self._point,
            "_max_degree": self._max_degree,
            "_cache": self._sanitize_cache(self._cache),
        }

    def __setstate__(self, state):
        self._point = state["_point"]
        self._max_degree = state["_max_degree"]

        self._psi, self._clmo = _init_index_tables(self._max_degree)
        self._encode_dict_list = _create_encode_dict_from_clmo(self._clmo)
        self._cache = self._clone_cache(state.get("_cache", {}))
        self._poincare_maps = {}

    def coefficients(
        self,
        degree: Union[int, Iterable[int], str, None] = None,
        form: str = "center_manifold_real",
    ) -> str:

        # Mapping from *form* identifiers to the corresponding accessor
        # methods.  These accessors take care of computing and caching the
        # requested polynomial list on-demand.
        _form_dispatch = self._get_form_dispatch()

        if form not in _form_dispatch:
            raise ValueError(
                f"Unsupported polynomial form '{form}'. Allowed values are: "
                f"{', '.join(_form_dispatch.keys())}."
            )

        # Obtain the requested polynomial list (computed lazily & cached)
        poly_list = _form_dispatch[form]()

        # Delegate the actual formatting to the utility function, passing the
        # *degree* filter straight through.
        table = _format_poly_table(poly_list, self._clmo, degree)
        logger.info(f'{form} coefficients:\n\n{table}\n\n')
        return table

    def cache_get(self, key: tuple) -> Any:
        r"""
        Get a value from the cache.
        """
        return self._cache.get(key)
    
    def cache_set(self, key: tuple, value: Any):
        r"""
        Set a value in the cache.
        """
        self._cache[key] = value
    
    def cache_clear(self):
        r"""
        Clear the cache of computed polynomials and Poincaré maps.
        """
        logger.debug("Clearing polynomial and Poincaré map caches.")
        self._cache.clear()
        self._poincare_maps.clear()

    def _get_form_dispatch(self) -> Dict[str, Callable[[], List[np.ndarray]]]:
        """Return a dictionary mapping *form* strings to internal accessors.

        This centralizes the mapping so it can be reused by both
        :py:meth:`coefficients` and :py:meth:`compute` without repeating the
        same dictionary definition in multiple places.
        """
        return {
            "physical": self._get_physical_hamiltonian,
            "real_modal": self._get_real_modal_form,
            "complex_modal": self._get_complex_modal_form,
            "real_partial_normal": self._get_partial_real_normal_form,
            "complex_partial_normal": self._get_complex_partial_normal_form,
            "real_full_normal": self._get_full_real_normal_form,
            "complex_full_normal": self._get_full_complex_normal_form,
            "center_manifold_real": self._get_center_manifold_real,
            "center_manifold_complex": self._get_center_manifold_complex,
        }

    def _get_or_compute(self, key: tuple, compute_func: Callable[[], Any]) -> Any:
        r"""
        Retrieve a value from the cache or compute it if not present.

        This helper centralizes the caching logic. It ensures that computed
        values (which are assumed to be lists of numpy arrays or tuples of
        such lists) are stored and retrieved as copies to prevent mutation
        of the cached objects.
        """
        if (cached_val := self.cache_get(key)) is None:
            logger.debug(f"Cache miss for key {key}, computing.")
            computed_val = compute_func()
            
            # Store a copy to prevent mutation of the cached object.
            if isinstance(computed_val, tuple):
                self.cache_set(key, tuple([item.copy() for item in sublist] if isinstance(sublist, list) else sublist for sublist in computed_val))
            elif isinstance(computed_val, list):
                self.cache_set(key, [item.copy() for item in computed_val])
            else:
                self.cache_set(key, computed_val) # Should not be mutable
            
            return computed_val

        logger.debug(f"Cache hit for key {key}.")
        # Return a copy to the caller.
        if isinstance(cached_val, tuple):
            return tuple([item.copy() for item in sublist] if isinstance(sublist, list) else sublist for sublist in cached_val)
        elif isinstance(cached_val, list):
            return [item.copy() for item in cached_val]
        else:
            return cached_val

    def _get_physical_hamiltonian(self) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'physical')
        return self._get_or_compute(key, lambda: self._build_hamiltonian(
            self._point, self._max_degree
        ))

    def _get_real_modal_form(self, tol=1e-12) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'real_modal')
        return self._get_or_compute(key, lambda: _polylocal2realmodal(
            self._point, self._get_physical_hamiltonian(), self._max_degree, self._psi, self._clmo, tol=tol
        ))

    def _get_complex_modal_form(self, tol=1e-12) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'complex_modal')
        return self._get_or_compute(key, lambda: _substitute_complex(
            self._get_real_modal_form(tol=tol), self._max_degree, self._psi, self._clmo, tol=tol, mix_pairs=self._mix_pairs
        ))

    def _get_partial_lie_results(self, tol_modal=1e-12, tol_lie=1e-30) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        key_trans = ('hamiltonian', self._max_degree, 'complex_partial_normal')
        key_G = ('generating_functions', self._max_degree)
        key_elim = ('terms_to_eliminate', self._max_degree)
        
        # We bundle the results under a single key to ensure atomicity
        bundle_key = ('lie_transform_bundle', self._max_degree)

        def compute_partial_lie_bundle():
            poly_cn = self._get_complex_modal_form(tol=tol_modal)
            poly_trans, poly_G_total, poly_elim_total = _lie_transform_partial(
                self._point, poly_cn, self._psi, self._clmo, self._max_degree, tol=tol_lie
            )
            
            # Cache individual components as well
            self.cache_set(key_trans, [item.copy() for item in poly_trans])
            self.cache_set(key_G, [item.copy() for item in poly_G_total])
            self.cache_set(key_elim, [item.copy() for item in poly_elim_total])
            
            return poly_trans, poly_G_total, poly_elim_total

        return self._get_or_compute(bundle_key, compute_partial_lie_bundle)

    def _get_complex_partial_normal_form(self, tol_modal=1e-12, tol_lie=1e-30) -> List[np.ndarray]:
        """Return the Lie-transformed (normal-form) Hamiltonian in complex variables.

        This corresponds to the Hamiltonian obtained *after* the Lie series
        normalization (so it is in normal form), but *before* restricting to
        the centre manifold.  The result is cached under the same key that is
        already populated by ``_get_partial_lie_results`` so no duplicate
        computation occurs.
        """
        key = ('hamiltonian', self._max_degree, 'complex_partial_normal')

        def compute_normal_form():
            poly_trans, _, _ = self._get_partial_lie_results(tol_modal=tol_modal, tol_lie=tol_lie)
            return poly_trans

        return self._get_or_compute(key, compute_normal_form)

    def _get_partial_real_normal_form(self, tol_modal=1e-12, tol_lie=1e-30) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'real_partial_normal')

        def compute_normal_form():
            poly_trans = self._get_complex_partial_normal_form(tol_modal=tol_modal, tol_lie=tol_lie)
            return _substitute_real(poly_trans, self._max_degree, self._psi, self._clmo, tol=tol_modal, mix_pairs=self._mix_pairs)

        return self._get_or_compute(key, compute_normal_form)

    def _get_full_lie_results(self, tol_modal=1e-12, tol_lie=1e-30, resonance_tol=1e-30) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
        key_trans = ("hamiltonian", self._max_degree, "complex_full_normal")
        key_G = ("generating_functions_full", self._max_degree)
        key_elim = ("terms_to_eliminate_full", self._max_degree)

        # Bundle to ensure atomic cache writes
        bundle_key = ("lie_transform_bundle_full", self._max_degree)

        def compute_full_lie_bundle():
            logger.info("Performing full Lie transformation...")
            poly_cn = self._get_complex_modal_form(tol=tol_modal)
            poly_trans, poly_G_total, poly_elim_total = _lie_transform_full(
                self._point,
                poly_cn,
                self._psi,
                self._clmo,
                self._max_degree,
                tol=tol_lie,
                resonance_tol=resonance_tol
            )

            # cache copies to avoid accidental mutation
            self.cache_set(key_trans, [item.copy() for item in poly_trans])
            self.cache_set(key_G, [item.copy() for item in poly_G_total])
            self.cache_set(key_elim, [item.copy() for item in poly_elim_total])

            return poly_trans, poly_G_total, poly_elim_total

        return self._get_or_compute(bundle_key, compute_full_lie_bundle)

    def _get_full_complex_normal_form(self, tol_modal=1e-12, tol_lie=1e-30, resonance_tol=1e-30) -> List[np.ndarray]:
        """Return the *full* normal-form Hamiltonian in **complex** variables."""
        key = ("hamiltonian", self._max_degree, "complex_full_normal")

        def compute_full_complex_normal():
            poly_trans, _, _ = self._get_full_lie_results(tol_modal=tol_modal, tol_lie=tol_lie, resonance_tol=resonance_tol)
            return poly_trans

        return self._get_or_compute(key, compute_full_complex_normal)

    def _get_full_real_normal_form(self, tol_modal=1e-12, tol_lie=1e-30, resonance_tol=1e-30) -> List[np.ndarray]:
        """Return the *full* normal-form Hamiltonian in **real** variables."""
        key = ("hamiltonian", self._max_degree, "real_full_normal")

        def compute_full_real_normal():
            poly_trans = self._get_full_complex_normal_form(tol_modal=tol_modal, tol_lie=tol_lie, resonance_tol=resonance_tol)
            return _substitute_real(poly_trans, self._max_degree, self._psi, self._clmo, tol=tol_modal, mix_pairs=self._mix_pairs)

        return self._get_or_compute(key, compute_full_real_normal)
    
    def _restrict_poly_to_center_manifold(self, poly_H, tol=1e-14):
        r"""
        Restrict a Hamiltonian to the center manifold by eliminating hyperbolic variables.
        """
        # For triangular points, all directions are centre-type, so we do NOT
        # eliminate any terms involving (q1, p1).  The original behaviour of
        # zeroing these terms is only appropriate for collinear points where
        # (q1, p1) span the hyperbolic sub-space.

        if isinstance(self._point, TriangularPoint):
            # Simply return a *copy* of the input to avoid accidental mutation
            return [h.copy() for h in poly_H]

        # Collinear case - remove all terms containing q1 or p1 exponents.
        poly_cm = [h.copy() for h in poly_H]
        for deg, coeff_vec in enumerate(poly_cm):
            if coeff_vec.size == 0:
                continue
            for pos, c in enumerate(coeff_vec):
                if abs(c) <= tol:
                    coeff_vec[pos] = 0.0
                    continue
                k = _decode_multiindex(pos, deg, self._clmo)
                if k[0] != 0 or k[3] != 0:       # q1 or p1 exponent non-zero
                    coeff_vec[pos] = 0.0
        return poly_cm
    
    def _restrict_coord_to_center_manifold(self, coord_6d):
        """Project a 6-D Phase-space coordinate onto the centre manifold.

        For collinear points the hyperbolic pair (q1, p1) is removed.  For
        triangular points all six variables belong to the centre manifold so
        the original coordinates are returned unchanged (apart from casting to
        real dtype and ensuring contiguity).
        """

        # Always work with real numbers once we reach this stage.
        if np.iscomplexobj(coord_6d):
            coord_6d = np.real(coord_6d)

        if isinstance(self._point, TriangularPoint):
            # Nothing to eliminate, return full 6-vector.
            return np.ascontiguousarray(coord_6d, dtype=np.float64)

        # Collinear case: zero out the hyperbolic coordinates.
        return np.array([0.0, coord_6d[1], coord_6d[2], 0.0, coord_6d[4], coord_6d[5]], dtype=np.float64)
    
    def _get_center_manifold_complex(self) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'center_manifold_complex')

        if isinstance(self._point, TriangularPoint):
            logger.warning("Called center manifold method on triangular point, returning normal form.")
            return self._get_full_complex_normal_form()
        
        def compute_cm_complex():
            poly_trans = self._get_complex_partial_normal_form()
            return self._restrict_poly_to_center_manifold(poly_trans)

        return self._get_or_compute(key, compute_cm_complex)

    def _get_center_manifold_real(self, tol=1e-12) -> List[np.ndarray]:
        key = ('hamiltonian', self._max_degree, 'center_manifold_real')

        if isinstance(self._point, TriangularPoint):
            logger.warning("Called center manifold method on triangular point, returning normal form.")
            return self._get_full_real_normal_form(tol=tol)

        def compute_cm_real():
            poly_cm_complex = self._get_center_manifold_complex()
            return _substitute_real(poly_cm_complex, self._max_degree, self._psi, self._clmo, tol=tol, mix_pairs=self._mix_pairs)

        return self._get_or_compute(key, compute_cm_real)

    def compute(self, form: str = "center_manifold_real") -> List[np.ndarray]:
        r"""
        Compute and return a specific polynomial representation of the
        Hamiltonian.

        By default (``form='center_manifold_real'``) this reproduces the
        historical behaviour of returning the Hamiltonian restricted to the
        centre manifold expressed in real variables
        :math:`(q_2, p_2, q_3, p_3)`.  However, any of the internally
        supported representations can be requested by passing the appropriate
        *form* key, enabling callers (e.g.
        bifurcation/continuation routines) to obtain the *full* complex normal
        form without performing extraneous computations.

        Parameters
        ----------
        form : str, optional
            Identifier of the desired polynomial representation.  Allowed
            values are the same as those accepted by
            :py:meth:`CenterManifold.coefficients`.  Defaults to
            ``'center_manifold_real'`` for backward compatibility.

        Returns
        -------
        list of numpy.ndarray
            Sequence :math:`[H_0, H_2, \dots, H_N]` where each entry contains
            the packed coefficients of the homogeneous polynomial of that
            degree.

        Raises
        ------
        RuntimeError
            If any underlying computation step fails.
        
        Notes
        -----
        The computation is performed lazily and all intermediate results are
        cached.  Subsequent calls with the same *form* are therefore
        inexpensive.
        """

        # Mapping reused from ``coefficients`` but returning *raw* coefficient
        # lists instead of pretty-printed tables.
        _form_dispatch = self._get_form_dispatch()

        if form not in _form_dispatch:
            raise ValueError(
                f"Unsupported form '{form}'. Allowed values are: "
                f"{', '.join(_form_dispatch.keys())}."
            )

        # Compute (or retrieve from cache) the requested representation.
        result = _form_dispatch[form]()
        logger.info(f"Computed {form} coefficients.")
        return result

    def poincare_map(self, energy: float, **kwargs) -> "_PoincareMap":
        r"""
        Create a Poincaré map at the specified energy level.

        Parameters
        ----------
        energy : float
            Hamiltonian energy :math:`h_0`.
        **kwargs
            Configuration parameters for the Poincaré map:
            
            - dt : float, default 1e-2
                Integration step size.
            - method : {'rk', 'symplectic'}, default 'rk'
                Integration method.
            - integrator_order : int, default 4
                Order of the integration scheme.
            - c_omega_heuristic : float, default 20.0
                Heuristic parameter for symplectic integrators.
            - n_seeds : int, default 20
                Number of initial seed points.
            - n_iter : int, default 40
                Number of map iterations per seed.
            - seed_strategy : {'single', 'axis_aligned', 'level_sets', 'radial', 'random'}, default 'single'
                Strategy for generating initial seed points.
            - seed_axis : {'q2', 'p2', 'q3', 'p3'}, optional
                Axis for seeding when using 'single' strategy.
            - section_coord : {'q2', 'p2', 'q3', 'p3'}, default 'q3'
                Coordinate defining the Poincaré section.
            - compute_on_init : bool, default False
                Whether to compute the map immediately upon creation.
            - use_gpu : bool, default False
                Whether to use GPU acceleration.

        Returns
        -------
        _PoincareMap
            A Poincaré map object for the given energy and configuration.

        Notes
        -----
        A map is constructed for each unique combination of energy and
        configuration, and stored internally. Subsequent calls with the same
        parameters return the cached object.
        
        Parallel processing is enabled automatically for CPU computations.
        """
        from hiten.algorithms.poincare.base import (_PoincareMap,
                                                    _PoincareMapConfig)

        # Separate config kwargs from runtime kwargs (currently none)
        config_fields = set(_PoincareMapConfig.__dataclass_fields__.keys())
        
        config_kwargs = {}
        
        for key, value in kwargs.items():
            if key in config_fields:
                config_kwargs[key] = value
            else:
                raise TypeError(f"'{key}' is not a valid keyword argument for PoincareMap configuration.")
        
        cfg = _PoincareMapConfig(**config_kwargs)

        # Create a hashable key from the configuration only (not runtime params)
        config_tuple = tuple(sorted(asdict(cfg).items()))
        cache_key = (energy, config_tuple)

        if cache_key not in self._poincare_maps:
            self._poincare_maps[cache_key] = _PoincareMap(self, energy, cfg)
        
        return self._poincare_maps[cache_key]

    def _4d_cm_to_ic(self, cm_coords_4d: np.ndarray, tol: float = 1e-16) -> np.ndarray:
        """Convert 4-D centre-manifold coordinates to 6-D synodic initial conditions.

        This helper assumes *cm_coords_4d* is an array-like object of shape ``(4,)``
        containing the real centre-manifold variables ``[q2, p2, q3, p3]``.  No
        root-finding or Hamiltonian energy information is required - the
        supplied coordinates are taken to lie on the centre manifold already.

        The transformation follows exactly the *second* half of the original
        :py:meth:`ic` pipeline::

            CM (real) -> CM (complex) -> Lie transform -> real modal -> local -> synodic
        """

        # Ensure we have the required Lie generators (computed lazily)
        _, poly_G_total, _ = self._get_partial_lie_results()

        # Construct a 6-D centre-manifold phase-space vector.  By definition the
        # hyperbolic coordinates (q1, p1) are zero on the CM for collinear
        # points.  For triangular points *all* variables belong to the centre
        # manifold so we still embed the 4-D vector into the full 6-D space in
        # the same fashion - the values of q1, p1 are simply disregarded later
        # in the forward transform.
        real_4d_cm = np.asarray(cm_coords_4d, dtype=np.float64).reshape(4)

        real_6d_cm = np.zeros(6, dtype=np.complex128)
        real_6d_cm[1] = real_4d_cm[0]  # q2
        real_6d_cm[4] = real_4d_cm[1]  # p2
        real_6d_cm[2] = real_4d_cm[2]  # q3
        real_6d_cm[5] = real_4d_cm[3]  # p3

        # Modal (real -> complex) representation
        complex_6d_cm = _solve_complex(real_6d_cm, tol=tol, mix_pairs=self._mix_pairs)

        # Apply the forward Lie transform (centre-manifold -> physical variables)
        expansions = _lie_expansion(
            poly_G_total,
            self._max_degree,
            self._psi,
            self._clmo,
            tol,
            inverse=False,
            sign=1,
            restrict=False,
        )
        complex_6d = _evaluate_transform(expansions, complex_6d_cm, self._clmo)

        # Back to real modal variables
        real_6d = _solve_real(complex_6d, tol=tol, mix_pairs=self._mix_pairs)

        # Modal (real) -> local -> synodic coordinate chain
        local_6d = _coordrealmodal2local(self._point, real_6d, tol)
        synodic_6d = self._local2synodic(self._point, local_6d, tol)

        logger.info("CM->synodic transformation (4-D input) complete")
        return synodic_6d

    def _2d_cm_to_ic(
        self,
        poincare_point: np.ndarray,
        energy: float,
        section_coord: str = "q3",
        tol: float = 1e-16,
    ) -> np.ndarray:
        """Original *ic* behaviour - convert a 2-D Poincaré-section point.

        This routine reproduces verbatim the legacy implementation that:

        1. Uses the Hamiltonian energy constraint to solve for the missing
           coordinate on the chosen section;
        2. Embeds the resulting 4-D CM coordinates into 6-D phase-space;
        3. Applies the Lie transform and coordinate conversions to obtain the
           synodic initial conditions.
        """

        # Ensure we have the centre-manifold Hamiltonian and Lie generators
        poly_cm_real = self.compute(form="center_manifold_real")

        # Section configuration specifies which coordinate is fixed to zero and
        # which one must be solved for
        config = _get_section_config(section_coord)

        # Known variables on the section
        known_vars: Dict[str, float] = {config.section_coord: 0.0}
        known_vars[config.plane_coords[0]] = float(poincare_point[0])
        known_vars[config.plane_coords[1]] = float(poincare_point[1])

        var_to_solve = config.missing_coord

        # Solve for the missing CM coordinate that satisfies the energy level
        solved_val = _solve_missing_coord(
            var_to_solve,
            known_vars,
            float(energy),
            poly_cm_real,
            self._clmo,
        )

        # Combine into a full CM coordinate dictionary
        full_cm_coords = known_vars.copy()
        full_cm_coords[var_to_solve] = solved_val

        # Sanity check
        if any(v is None for v in full_cm_coords.values()):
            err = (
                "Failed to reconstruct full CM coordinates - root finding "
                "did not converge."
            )
            logger.error(err)
            raise RuntimeError(err)

        real_4d_cm = np.array(
            [
                full_cm_coords["q2"],
                full_cm_coords["p2"],
                full_cm_coords["q3"],
                full_cm_coords["p3"],
            ],
            dtype=np.float64,
        )

        # Delegate the second half of the pipeline to the 4-D helper
        return self._4d_cm_to_ic(real_4d_cm, tol)

    def ic(
        self,
        cm_point: np.ndarray,
        energy: Optional[float] = None,
        section_coord: str = "q3",
        tol: float = 1e-16,
    ) -> np.ndarray:
        """Convert centre-manifold coordinates to full synodic ICs.

        The method now supports **two** input formats:

        1. *2-D Poincaré-section* coordinates (legacy behaviour).  In this case
           *energy* **must** be provided and *section_coord* specifies which CM
           coordinate is fixed to zero on the section.
        2. *4-D centre-manifold* coordinates ``[q2, p2, q3, p3]``.  Here the
           coordinates are assumed to satisfy the Hamiltonian energy
           constraint already, so *energy* and *section_coord* are ignored.

        Parameters
        ----------
        cm_point : numpy.ndarray, shape (2,) or (4,)
            Point on the Poincaré section (length-2) **or** full centre-manifold
            coordinates (length-4).
        energy : float | None, optional
            Hamiltonian energy level *h0*.  Required only when *cm_point* is a
            2-vector.
        section_coord : {'q3', 'p3', 'q2', 'p2'}, default 'q3'
            Coordinate fixed to zero on the Poincaré section.  Ignored for
            4-D inputs.
        tol : float, optional
            Numerical tolerance used by the various helper routines.

        Returns
        -------
        numpy.ndarray, shape (6,)
            Synodic-frame initial conditions ``(q1, q2, q3, p1, p2, p3)``.
        """

        cm_point = np.asarray(cm_point)

        if cm_point.size == 2:
            if energy is None:
                raise ValueError(
                    "energy must be specified when converting a 2-D Poincaré "
                    "point to initial conditions."
                )
            logger.info(
                "Converting 2-D Poincaré point %s (section=%s) to synodic ICs",
                cm_point,
                section_coord,
            )
            return self._2d_cm_to_ic(cm_point, float(energy), section_coord, tol)

        elif cm_point.size == 4:
            logger.info("Converting 4-D CM point %s to synodic ICs", cm_point)
            return self._4d_cm_to_ic(cm_point, tol)

        else:
            raise ValueError(
                "cm_point must be either a 2- or 4-element vector representing "
                "a Poincaré-section point or full CM coordinates, respectively."
            )
    
    def cm(self, synodic_6d: np.ndarray, tol=1e-16) -> np.ndarray:
        """Return 4-D centre-manifold coordinates (q2, p2, q3, p3) from 6-D synodic ICs.

        This is the exact inverse of :py:meth:`ic` and therefore performs the
        following steps in *reverse* order::

            synodic -> local -> real modal -> complex modal -> Lie-inverse -> CM.

        Parameters
        ----------
        synodic_6d : numpy.ndarray, shape (6,)
            Synodic coordinates (X, Y, Z, Vx, Vy, Vz).

        Returns
        -------
        numpy.ndarray, shape (4,)
            Centre-manifold real coordinates ``[q2, p2, q3, p3]``.
        """

        local_6d = self._synodic2local(self._point, synodic_6d, tol)

        real_modal_6d = _coordlocal2realmodal(self._point, local_6d, tol)

        complex_modal_6d = _solve_complex(real_modal_6d, tol=tol, mix_pairs=self._mix_pairs)

        _, poly_G_total, _ = self._get_partial_lie_results()
        expansions = _lie_expansion(poly_G_total, self._max_degree, self._psi, self._clmo,
                                    tol, inverse=True, sign=-1, restrict=False)

        complex_pnf_6d = _evaluate_transform(expansions, complex_modal_6d, self._clmo)
        real_pnf_6d = _solve_real(complex_pnf_6d, tol=tol, mix_pairs=self._mix_pairs)
        real_cm_6d = self._restrict_coord_to_center_manifold(real_pnf_6d)

        real_cm_4d = np.array([
            real_cm_6d[1], # q2
            real_cm_6d[4], # p2
            real_cm_6d[2], # q3
            real_cm_6d[5], # p3
        ], dtype=np.float64)

        return real_cm_4d

    def save(self, dir_path: str):
        r"""
        Save the CenterManifold instance to a directory.

        This method serializes the main object to 'manifold.pkl' and saves
        each associated Poincare map to a separate file within a 'poincare_maps'
        subdirectory.

        Parameters
        ----------
        dir_path : str or path-like object
            The path to the directory where the data will be saved.
        """
        _save_center_manifold(self, dir_path)

    @classmethod
    def load(cls, dir_path: str) -> "CenterManifold":
        r"""
        Load a CenterManifold instance from a directory.

        This class method deserializes a CenterManifold object and its
        associated Poincare maps that were saved with the `save` method.

        Parameters
        ----------
        dir_path : str or path-like object
            The path to the directory from which to load the data.

        Returns
        -------
        CenterManifold
            The loaded CenterManifold instance with its Poincare maps.
        """
        return _load_center_manifold(dir_path)

    @staticmethod
    def _sanitize_cache(cache_in):
        """Recursively clone arrays so they are backed by NumPy memory only."""
        import numpy as np

        def _clone(obj):
            if isinstance(obj, np.ndarray):
                return np.ascontiguousarray(obj)
            if isinstance(obj, (list, tuple)):
                cloned = [_clone(item) for item in obj]
                return type(obj)(cloned)  # preserve list / tuple
            if isinstance(obj, dict):
                return {k: _clone(v) for k, v in obj.items()}
            try:
                # Handle numba.typed.List / Dict by casting to list / dict
                from numba.typed import Dict as NumbaDict
                from numba.typed import List as NumbaList
                if isinstance(obj, NumbaList):
                    return [_clone(x) for x in list(obj)]
                if isinstance(obj, NumbaDict):
                    return {k: _clone(v) for k, v in obj.items()}
            except Exception:
                pass
            return obj

        return {k: _clone(v) for k, v in cache_in.items()}

    @staticmethod
    def _clone_cache(cache_in):
        """Deep-copy the cached structures so the unpickled object owns its data."""
        import numpy as np
        def _clone(obj):
            if isinstance(obj, np.ndarray):
                return np.ascontiguousarray(obj)
            if isinstance(obj, (list, tuple)):
                return type(obj)([_clone(x) for x in obj])
            if isinstance(obj, dict):
                return {k: _clone(v) for k, v in obj.items()}
            return obj
        return {k: _clone(v) for k, v in cache_in.items()}
