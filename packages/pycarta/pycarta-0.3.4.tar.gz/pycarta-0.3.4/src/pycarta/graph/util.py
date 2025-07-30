import numpy as np
from collections import namedtuple
from copy import deepcopy
from itertools import chain, product, repeat, starmap
from typing import Any, TypeAlias, Union


ArrayLike: TypeAlias = Union[list[Any], tuple[Any], np.ndarray]


def as_container(x):
    """Ensures the object is a container."""
    # if hasattr(x, "__iter__") and not isinstance(x, str):
    if hasattr(x, "__iter__") and not isinstance(x, str):
        return x
    else:
        return [x]


def as_list(x):
    """Ensures the object is a list."""
    return list(as_container(x))


def broadcast(arr: ArrayLike, *, dim: int | None=None) -> list[Any]:
    """
    Aligns data by broadcasting data into a common shape. This follows numpy's
    broadcasting rules.

    Users should be aware of the consequences of this function. This aligns
    data with compatible dimensions and establishes an implicit correlation
    between elements in vector-valued properties. Specifically::

        x = [1, 2, 3]
        y = [4, 5, 6]

    assumes three points in a two dimensional space: (1, 4), (2, 5), and
    (3, 6).

    Parameters
    ----------
    arr : array-like
        Array whose contents should be reshaped.
    
    dim : int | None
        Final dimensionality of the resulting list. Typical values are None (no
        reshaping), -1 (reduce the inner dimension by 1)

    Returns
    -------
    list
        List (of lists (of lists (...))) of aligned data.
    """
    def is_arraylike(x):
        return isinstance(x, (list, tuple, np.ndarray))
    
    if not is_arraylike(arr):
        return arr # type: ignore
    
    result = list(arr[:])
    shape_set = set()
    for i,x in enumerate(result):
        # broadcast within nested structures
        result[i] = broadcast(x, dim=None)
        shape_set.add(np.shape(result[i]))
    for x in result:
        # look for shapes into which all other values can be broadcast
        for shape in shape_set:
            try:
                _ = np.broadcast_to(x, shape)
            except ValueError:
                shape_set = shape_set - {shape}
    try:
        shape = shape_set.pop()
    except KeyError: # pragma: no cover
        raise ValueError(f"Cannot broadcast arrays into a common shape.")
    rval = np.array([np.broadcast_to(x, shape) for x in result])
    # Replace 0-dim entries with their values. (Remove ndarray wrapper.)
    rval = np.array([(x.item() if x.ndim == 0 else x) for x in rval])
    if dim is not None:
        shape = rval.shape[:dim-1] + (-1,)
        # rval = np.array([np.ravel(x) for x in rval])
        rval = rval.reshape(shape)
    return rval.tolist()


__broadcast = broadcast  # So broadcast parameter in cartesian doesn't mask function.

def cartesian(obj: dict, *, aligned: bool=True, broadcast: bool | None=None, in_place: bool=False) -> dict:
    """
    Joins data from dictionaries that key to scalar or list-like data even if
    the data (lists of data) in each vertex are ragged.
    
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
    obj : dict[Any, array-like]
        Dictionary whose possibly ragged lists are to be combined.

    aligned : bool (optional)
        Whether arrays/lists that are the same length in a node should be considered
        aligned or if they, too, should be combined in all possible permutations.
        Default: True. (Lists that are the same length are considered to be aligned.)
        *Note* Be very careful setting this to False. The resulting tables can become
        extremely large.

    broadcast : bool (optional)
        Attempt to broadcast first. This can be much faster and produce more compact
        data sets then a full cartesian join. Default: same as `aligned`. If the
        broadcast fails, fall back to cartesian.

    in_place : bool (optional)
        Whether to replace the contents of `obj` with the results of the merge.
        Default: False. This should typically be set to True if this function
        is used in `BinaryVisitor`, such as an `Aggregator` or `Propagator`.

    Returns
    -------
    dict[Any, array-like]
        Returns the dictionary containing the updated data, whether in place or not.

    Example
    -------
    The following example might be used if, for example, measurements "a" and "c"
    are correlated and repeated twice each but "b" is a repeated measurement that
    is conducted independently of "a" and "c".

        left = {"a": [1, 2], "b": [3, 4, 5], "c": [6, 7]}

        cartesian(left, aligned=True)
        # output = {
        #    "a": [1, 1, 1, 2, 2, 2],
        #    "b": [3, 4, 5, 3, 4, 5],
        #    "c": [6, 6, 6, 7, 7, 7]
        # }

        cartesian(left, aligned=False)
        # output = {
        #    "a": [1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2],
        #    "b": [3, 3, 4, 4, 5, 5, 3, 3, 4, 4, 5, 5],
        #    "c": [6, 7, 6, 7, 6, 7, 6, 7, 6, 7, 6, 7]
        # }
    """
    def try_numeric(x):
        try:
            return int(x)
        except:
            pass
        try:
            return float(x)
        except:
            pass
        return x

    def cartesian_product_maintain_alignment_of_equal_length_vecs(d: dict):
        try:
            if broadcast:
                # If values are broadcastable, broadcast.
                keys = list(d.keys())
                values = list(d.values())
                result = dict(zip(keys, __broadcast(values))) # Raises ValueError on failure.
            else:
                raise ValueError()  # Skip to cartesian product
        except ValueError:
            # Otherwise, combine as the cartesian product
            # Note: This is refactored to use generators until the very end
            # to avoid unnecessary duplication of data.
            Chunk = namedtuple("Chunk", ["label", "values"])
            # Unique list lengths (in the dict values)
            lengths = set((len(a) if isinstance(a, list) else 1) for a in d.values())
            # Each group is the collection of lists with common length
            groups_of_length = lambda length: (Chunk(k, as_list(v))
                                            for k, v in d.items()
                                            if len(as_list(v)) == length)
            groups = lambda: (groups_of_length(length) for length in lengths)
            # Each chunk has a label generator that produces the sequence of
            # labels for the N members of the group and a values generator that
            # yields the N-tuple of aligned values.
            chunks = lambda: (
                Chunk((g.label for g in labels), zip(*(g.values for g in values)))
                for labels, values in zip(groups(), groups())
            )
            # Chain all the labels together from each chunk: M x N x ... length tuple
            labels = lambda: chain(*(chunk.label for chunk in chunks()))
            # Chain all the values together from the product of each unique-length groups' values
            values = lambda: starmap(chain, product(*(chunk.values for chunk in chunks())))
            # Return these as a dictionary (in other applications, the iterator
            # itself could be returned, simulating a call to dict.items(), but
            # this use cases works directly with dicts)
            result = dict(zip(labels(), zip(*values())))
        for k, v in result.items():
            result[k] = list(map(try_numeric, v)) # type: ignore
        return result
    
    def cartesian_product_ignore_alignment_of_equal_length_vecs(d: dict):
        try:
            if broadcast:
                # If values are broadcastable, broadcast.
                keys = list(d.keys())
                values = list(d.values())
                result = dict(zip(keys, __broadcast(values)))
            else:
                raise ValueError()  # Skip to cartesian product
        except ValueError:
            # Otherwise,
            labels = d.keys
            values = lambda: product(*(as_list(d[l] for l in labels())))
            result = dict(zip(labels(), zip(*values())))
        for k, v in result.items():
            result[k] = list(map(try_numeric, v)) # type: ignore
        return result

    broadcast = aligned if broadcast is None else broadcast
    cartprod = (cartesian_product_maintain_alignment_of_equal_length_vecs
                if aligned else
                cartesian_product_ignore_alignment_of_equal_length_vecs)
    dst = cartprod(obj)
    if not in_place:
        return dst
    else:
        obj.clear()
        obj.update(dst)
        return obj


def concatenate(data: dict, *, in_place: bool=False) -> dict:
    """
    Stacks the values from each key in the input dictionary so all values are
    lists of the same length and no values are aligned. For example:

        a: 1, 2, 3
        b: 4, 5, 6
        c: 7

    becomes:

        a: 1, 2, 3, None, None, None, None
        b: None, None, None, 4, 5, 6, None
        c: None, None, None, None, None, None, 7

    This structure is relevant when the key/value pairs in are not related,
    that is, when the data are uncorrelated and should be treated as
    unconnected.

    Parameters
    ----------
    data : dict[hashable, list-like | scalar]
        Data whose possibly ragged fields are to be combined into equal-length
        lists.
    
    in_place : bool (optional)
        Whether to modify `d` in place. Default: False

    Returns
    -------
    dict[hashable, list-like]
        Data with equal-length lists.
    """
    result = {
        key: [(x if k == key else None) for k, v in data.items() for x in as_list(v)]
        for key in data.keys()
    }
    if in_place:
        data.clear()
        data.update(result)
        return data
    else:
        return result


def join(left: dict, right: dict, *, in_place: bool=False) -> dict:
    """
    Joins the records from two objects (dictionaries/mappings) to produce a single
    record with value alignment maintained from the constituent properties.

    Simply, if you were to plot A vs. B from record 1 in Matplotlib, those same
    points would appear, possibly with others, when record 1 and record 2 are joined.
    That is `plot(A, B)` before joining is a subset of `plot(A, B)` after joining.

    Parameters
    ----------
    left : dict
        Left record to join.

    right : dict
        Right record to join.

    in_place : bool
        Whether to replace the contents of lhs with the result of the join.

    Returns
    -------
    dict
        The content from left and right combined into a single, aligned record.
    """
    lhs, rhs = deepcopy(left), deepcopy(right)
    # Keys present in both object
    keys = sorted(set(lhs) | set(rhs))
    # Make sure all records have a full complement of keys
    # Pads the shorter of any two lists with None to maintain alignment,
    # e.g. [1, 2, 3] + [4, 5] -> [(1, 4), (2, 5), (3, None)]
    for dict_ in (lhs, rhs):
        for k in keys:
            dict_.setdefault(k, None)
    # Ensure all fields in lhs and rhs are aligned
    for dict_ in (lhs, rhs):
        values = list(dict_.values())
        try:
            aligned = broadcast(values, dim=2)
        except ValueError: # pragma: no cover
            raise ValueError("The data in one or more records cannot be "
                             "aligned. Joining is not possible.")
        else:
            for k, v in zip(dict_, aligned):
                dict_[k] = v
    # maximum vector length when left and right are combined
    maxlen = max([len(as_list(lhs.get(k, []))) + len(as_list(rhs.get(k, []))) for k in keys])
    # Construct the values: [(v11, v21, ..., vn1), (v12, v22, ..., vn2), ...]
    # That is, the values for each key are organized in column vectors
    values = [[(None if x == "\0" else x) for x in tuple_] # Replace null string with None.
              for tuple_ in filter(
                  lambda container: not all(x == "\0" for x in container), # drop triple-null strings from...
                  zip(*[
                      chain(as_list(lhs.get(k, [])), # left-hand list
                            repeat("\0", maxlen - len(as_list(lhs.get(k, []))) - len(as_list(rhs.get(k, [])))), # centrally padded with null strings
                            as_list(rhs.get(k, [])))  # right-hand list
                      for k in keys
                  ])
              )]
    # Convert column vectors back into row vectors
    result = {k:[v[i] for v in values] for i, k in enumerate(keys)}
    if in_place:
        left.clear()
        left.update(result)
        return left
    else:
        return result
