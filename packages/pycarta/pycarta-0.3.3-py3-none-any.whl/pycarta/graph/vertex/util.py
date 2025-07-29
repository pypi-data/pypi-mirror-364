from collections import namedtuple
from itertools import product, chain, starmap

from pycarta.graph.util import join as join_dicts
from pycarta.graph.util import cartesian, as_list
from pycarta.graph.vertex.types import DictVertex


__all__ = [
    "join",
    "cartesian_join",
]


def join(left: DictVertex, right: DictVertex, *, in_place: bool=False) -> DictVertex:
    """
    Joins the records from two dictionary-like vertices to produce a single
    record with value alignment maintained from the constituent properties.

    Simply, if you were to plot A vs. B from record 1 in Matplotlib, those same
    points would appear, possibly with others, when record 1 and record 2 are
    joined. That is `plot(A, B)` before joining is a subset of `plot(A, B)`
    after joining.

    Parameters
    ----------
    left : JsonVertex
        Left record to join.

    right : JsonVertex
        Right record to join.

    in_place : bool
        Whehter to replace the values in the left index with the results of
        the join.

    Returns
    -------
    DictVertex
        The content from left and right combined into a single, aligned
        DictVertex.
    """
    joined = join_dicts(left.to_json(), right.to_json()) # type: ignore
    if in_place:
        left.content_ = joined
        return left
    else:
        return DictVertex.from_json(joined) # type: ignore


def cartesian_join(dst: DictVertex, src: DictVertex, *, aligned: bool=True, broadcast: bool | None=None, in_place: bool=False) -> DictVertex:
    """
    Joins data from vertex even if the data (lists of data) in each vertex are ragged.
    
    Where might a cartesian join be used? Consider the situation where one sample
    is cut into two subsamples: A and B. A is subdivided into m test coupons, each
    measuring a scalar value for "foo". Similarly, B is subdivided into n test
    coupons, each measuring a scalar value for "bar". Because these measurements 
    are independent, there is no correlation between the i^th foo measurement and
    the i^th bar measurement. Were both measurments possible on the same sample,
    then each measurement of bar is equally probable for a measured value of foo.

    More concretely, a steel plate is cut in half. One half is cut into 3 fatigue
    samples, the other half is cut into 5 tensile samples. Each of the 3 fatigue
    measurements, F1-F3, is paired to each of the 5 tensile measurements, T1-T5:

        tensile: T1, T1, T1, T2, T2, T2, ..., T5, T5, T5
        fatigue: F1, F2, F3, F1, F2, F3, ..., F1, F2, F3
    
    This ensures the lists remain aligned as data are aggregated through the graph.

    **Note**: Values that look like numbers, i.e. they are convertable to numbers,
    will be treated as numbers. This is not guaranteed and may be changed in the
    future without warning.
    
    Parameters
    ----------
    dst : pycarta.graph.vertex.DictVertex
        Destination vertex -- the vertex that will be updated with the joined data.
    
    src : pycarta.graph.vertex.DictVertex
        Source vertex -- the other vertex.

    aligned : bool (optional)
        Whether arrays/lists that are the same list in a node should be considered
        aligned or if they, too, should be combined in all possible permutations.
        Default: True. (Lists that are the same length are considered to be aligned.)
        *Note* Be very careful setting this to False. The resulting tables can become
        extremely large.

    broadcast : bool (optional)
        Attempt to broadcast first. This can be much faster and produce more compact
        data sets then a full cartesian join. Default: same as `aligned`. If the
        broadcast fails, fall back to cartesian.

    in_place : bool (optional)
        Whether to replace the contents of the first vertex with the results of the
        merge. Default: False. This should typically be set to True if this function
        is used in `BinaryVisitor`, such as an `Aggregator` or `Propagator`.

    Returns
    -------
    DictVertex
        Returns the vertex containing the updated data, whether in place or not.

    Example
    -------
    The following example might be used if, for example, measurements "a" and "c"
    are correlated and repeated twice each but "b" is a repeated measurement that
    is conducted independently of "a" and "c".

        left = {"a": [1, 2], "b": [3, 4, 5], "c": [6, 7]}
        right = {"b": 8, "c": [9, 0]}

        cartesian_join(left, right, aligned=True)
        # output = {
        #    "a": [1, 1, 1, 2, 2, 2, None, None],
        #    "b": [3, 4, 5, 3, 4, 5, 8, 8],
        #    "c": [6, 6, 6, 7, 7, 7, 9, 0]
        # }
    """    
    lhs = cartesian(dst.to_json(), aligned=aligned, broadcast=broadcast, in_place=False) # type: ignore
    rhs = cartesian(src.to_json(), aligned=aligned, broadcast=broadcast, in_place=False) # type: ignore

    if not in_place:
        dst = dst.copy() # type: ignore # copy is a DictVertex method, not a dict method
    result = join_dicts(lhs, rhs)
    dst.clear()
    dst.update(result)
    return dst
