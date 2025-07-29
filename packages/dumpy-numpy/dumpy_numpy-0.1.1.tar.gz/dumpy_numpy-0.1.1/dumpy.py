# DumPy: Like NumPy except it's OK if you're dum
# Copyright (C) 2025 dynomight
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# This code may only be used for good, not evil.

__version__ = "0.0.1"

from __future__ import annotations

import numpy as np
import jax
import jax.numpy as jnp
from typing import Union, Sequence, Tuple, Any, Dict, List, Iterable, Optional
from jax.typing import ArrayLike
import warnings


def process_axes(axes: Sequence[str | MappedRange | None])->List[str|None]:
    "Given some axes that might include a range, convert ranges to str"
    out_axes = []
    for ax in axes:
        if isinstance(ax, MappedRange):
            name, = ax.axes
            out_axes.append(name)
        else:
            out_axes.append(ax)
    return out_axes

class MappedArray:
    def __init__(self, data, axes: Sequence[str | None]):
        data = jnp.asarray(data)
        if data.ndim != len(axes):
            raise ValueError(f"Data ndim {data.ndim} != length of axes {len(axes)}")
        self.data = data
        self.axes = tuple(axes)

    @property
    def shape(self):
        return tuple(s for s, ax in zip(self.data.shape, self.axes, strict=True) if ax is None)

    @property
    def ndim(self):
        return len(self.shape)

    def __len__(self):
        return self.shape[0]

    @property
    def mapped_axes(self):
        return tuple(ax for ax in self.axes if ax is not None)

    def in_axis(self, ax:str, ignore:Sequence[str]):
        if ax in ignore:
            raise ValueError("given axis in ignore list")

        remaining_axes = [ax for ax in self.axes if ax not in ignore]

        if ax in remaining_axes:
            return remaining_axes.index(ax)
        else:
            return None

    def map_axis(self, num, name):
        if not (0 <= num < self.ndim):
            raise ValueError(f"given axis number {num} does not satisfy 0 <= {num} < {self.ndim}")
        if name in self.mapped_axes:
            raise ValueError(f"axis {name} already mapped")

        new_axes = []
        num_processed = 0
        for ax in self.axes:
            if ax is not None:
                new_axes.append(ax)
            elif num_processed == num:
                new_axes.append(name)
                num_processed += 1
            else:
                new_axes.append(None)
                num_processed += 1
        return MappedArray(self.data, new_axes)

    def map_axes(self, nums, names):
        if len(nums) != len(names):
            raise ValueError("Number of axis indices must match number of names")
        if len(set(nums)) != len(nums):
            raise ValueError("Duplicate axis indices provided")
        if len(set(names)) != len(names):
            raise ValueError("Duplicate axis names provided")

        if len(nums) == 0:
            return self

        # sorted_indices = jnp.argsort(jnp.asarray(nums))
        # A = self
        # for i in sorted_indices[::-1]:
        #     A = A.map_axis(nums[i], names[i])
        # return A

        def argsort(seq):
            # Return the indices that would sort the sequence
            return sorted(range(len(seq)), key=seq.__getitem__)

        sorted_indices = argsort(nums)
        print("sorted_indices", sorted_indices)
        A = self
        for i in reversed(sorted_indices):
            A = A.map_axis(nums[i], names[i])
        return A

    # def unmap_axis_in_place(self, name):
    #     if name not in self.mapped_axes:
    #         raise ValueError(f"axis {name} not mapped")
    #     old_loc = self.axes.index(name)
    #
    #     new_axes = []
    #     for ax in self.axes:
    #         if ax is None or ax != name:
    #             new_axes.append(ax)
    #         else:
    #             new_axes.append(None)
    #     return MappedArray(self.data, new_axes), old_loc
    #
    # def mapped_dim(self, num):
    #     if not (0 <= num < self.ndim):
    #         raise ValueError(f"given axis number {num} does not satisfy 0 <= {num} < {self.ndim}")
    #     count = 0
    #     for n, ax in enumerate(self.axes):
    #         if ax is None:
    #             if count == num:
    #                 return n
    #             count += 1
    #     # Should not be reached if input is valid
    #     raise IndexError("Could not find the specified unmapped dimension index.")
    #
    # def swap_mapped_axes(self, dim1, dim2):
    #     new_axes = []
    #     for n, ax in enumerate(self.axes):
    #         if n == dim1:
    #             new = self.axes[dim2]
    #         elif n == dim2:
    #             new = self.axes[dim1]
    #         else:
    #             new = self.axes[n]
    #         new_axes.append(new)
    #     return MappedArray(jnp.swapaxes(self.data, dim1, dim2), new_axes)
    #
    # def unmap_axis(self, num, name):
    #     if not (0 <= num <= self.ndim):
    #         raise ValueError(f"given axis number {num} does not satisfy 0 <= {num} <= {self.ndim}")
    #
    #     tmp_array, old_loc = self.unmap_axis_in_place(name)
    #     new_loc = tmp_array.mapped_dim(num)
    #     return tmp_array.swap_mapped_axes(old_loc, new_loc)
    #
    # def unmap_axes(self, nums, names):
    #     order = jnp.argsort(jnp.asarray(nums))
    #     A = self
    #     for n in order:
    #         A = A.unmap_axis(nums[n], names[n])
    #     return A

    def unmap(self, *idx:str|slice):
        if len(idx) != len(self.axes):
            raise IndexError(f"given idx does not satisfy len(idx) == {self.ndim}")

        unnamed_indices = (n for n,ax in enumerate(self.axes) if ax is None or ax not in idx)

        source_indices = []
        new_axes = []
        for i in idx:
            if isinstance(i, str):
                source_indices.append(self.axes.index(i))
                new_axes.append(None)
            else:
                assert i == slice(None) or i not in idx
                source_indices.append(next(unnamed_indices))
                new_axes.append(self.axes[source_indices[-1]])
        new_data = self.data.transpose(source_indices)
        if all(i is None for i in new_axes):
            return Array(new_data)
        return MappedArray(new_data, new_axes)

    def unmap_with_missing(self, *idx:str|slice):
        new_idx = []
        def cur():
            if len(new_idx) < len(self.axes):
                return self.axes[len(new_idx)]
            else:
                return None

        # needed?
        # while cur() is not None and cur() not in idx:
        #     #new_idx.append(cur())
        #     new_idx.append(slice(None))

        for i in idx:
            while cur() is not None and cur() not in idx:
                #new_idx.append(cur())
                new_idx.append(slice(None))
            new_idx.append(i)

        while cur() is not None and cur() not in idx:
            #new_idx.append(cur())
            new_idx.append(slice(None))

        if len(new_idx) != len(self.axes):
            raise ValueError(f"new_idx does not satisfy len(new_idx) == len(self.axes) ({len(new_idx)} != {len(self.axes)})")

        return self.unmap(*new_idx)

    def index_no_strings(self, *idx):
        assert len(idx) == self.ndim
        arrays, weave = weave_arrays(*idx)

        @MappedFunction
        def index(data, *arrays):
            idx = weave(*arrays)

            return data[*idx]
        return index(self, *arrays)

    def index(self, *idx):
        if len(idx) != self.ndim:
            raise IndexError(f"Got {len(idx)} with {self.ndim} dimensions")
        if not any(isinstance(s,str) for s in idx):
            nums = []
            names = []
        else:
            nums, names = zip(*[(n,s) for (n,s) in enumerate(idx) if isinstance(s,str)])
        A = self.map_axes(nums, names)
        remaining_idx = [s for s in idx if not isinstance(s,str)]
        return A.index_no_strings(*remaining_idx)

    # def check_indices(self, *idx):
    #     # restrict valid inputs
    #     index_shape = None
    #     for i in idx:
    #         if isinstance(i, slice):
    #             continue
    #         elif isinstance(i, str):
    #             continue
    #         elif isinstance(i, (MappedArray, jnp.ndarray)):
    #             my_shape = i.shape
    #         else:
    #             my_shape = jnp.asarray(i).shape
    #         if my_shape == ():
    #             continue
    #         elif index_shape is None:
    #             index_shape = my_shape
    #         else:
    #             if index_shape != my_shape:
    #                 raise IndexError(f"Only only index can be non-scalar array (got {array_shape} and {i})")

    def check_indices(self, *idx):
        # restrict valid inputs
        index_shape = None
        for i in idx:
            if isinstance(i, slice):
                continue
            elif isinstance(i, str):
                continue
            elif isinstance(i, (MappedArray, jnp.ndarray)):
                my_shape = i.shape
            else:
                my_shape = jnp.asarray(i).shape
            if my_shape == ():
                continue
            elif index_shape is None:
                index_shape = my_shape
            else:
                raise IndexError(f"Only one index can be non-scalar array (got {index_shape} and {my_shape})")


    def __getitem__(self, idx):
        """Index an array. All inputs must be slice or string or scalar except one"""

        if not isinstance(idx,tuple):
            idx = (idx,)

        self.check_indices(*idx)

        return self.index(*idx)

    def __repr__(self):
        cls_name = self.__class__.__name__

        data_str = f"{self.data}".replace("\n","\n "+" "*len(cls_name))

        if self.mapped_axes:
            return f"{cls_name}({data_str}, shape={self.shape}, mapped_axes={self.mapped_axes}, axes={self.axes}, data.shape={self.data.shape})"
        else:
            return f"{cls_name}({data_str}, shape={self.shape})"

    def __add__(self, other):
        return add(self, other)

    def __radd__(self, other):
        return add(other, self)

    def __sub__(self, other):
        return subtract(self, other)

    def __rsub__(self, other):
        return subtract(other, self)

    def __mul__(self, other):
        return multiply(self, other)

    def __rmul__(self, other):
        return multiply(other, self)

    def __truediv__(self, other):
        return divide(self, other)

    def __rtruediv__(self, other):
        return divide(other, self)

    def __pow__(self, other):
        return power(self, other)

    def __rpow__(self, other):
         return power(other, self) # JAX handles scalar exponentiation correctly

    def __mod__(self, other):
        return mod(self, other)

    def __rmod__(self, other):
        return mod(other, self)

    # Matrix Multiplication
    def __matmul__(self, other):
        return matmul(self, other)

    def __rmatmul__(self, other):
        return matmul(other, self)

    # Unary Operators
    def __neg__(self):
        # Define negative if not already done
        global negative
        try:
            negative
        except NameError:
            negative = MappedFunction(jnp.negative)
        return negative(self)

    def __pos__(self):
        # Define positive if not already done
        global positive
        try:
            positive
        except NameError:
            positive = MappedFunction(jnp.positive)
        return positive(self) # Or simply return self if jnp.positive isn't needed

    def __abs__(self):
        # Assumes 'absolute' wrapper exists for jnp.absolute
        return absolute(self)

    # Comparisons
    def __eq__(self, other):
        return equal(self, other)

    def __ne__(self, other):
        return not_equal(self, other)

    def __lt__(self, other):
        return less(self, other)

    def __le__(self, other):
        return less_equal(self, other)

    def __gt__(self, other):
        return greater(self, other)

    def __ge__(self, other):
        return greater_equal(self, other)

    @property
    def T(self):
        return MappedArray(self.data.T, tuple(reversed(self.axes)))

    # def __jax_array__(self):
    #     """Allows JAX functions to treat this object as a JAX array.
    #
    #     Returns:
    #         jax.Array: The underlying data array.
    #     """
    #     # Return the raw JAX array data
    #     if self.mapped_axes != ():
    #         raise ValueError("Cannot use MappedArray with mapped dims as jax array")
    #
    #     return self.data

    @property
    def dtype(self):
        return self.data.dtype

def weave_arrays(*args):
    "given a list of args, pick out the Array args"
    def weave(*arrays):
        out = []
        n = 0
        for a in args:
            if isinstance(a,MappedArray):
                out.append(arrays[n])
                n += 1
            else:
                out.append(a)
        return tuple(out)

    initial_arrays = tuple(a for a in args if isinstance(a, MappedArray))
    return initial_arrays, weave

class Array(MappedArray):
    def __init__(self, data):
        data = jnp.asarray(data)
        super().__init__(data, [None]*data.ndim)

    def __str__(self):
        "Array has a simple str that only prints the data. (MappedArray doesn't have this.)"
        return f"{self.data}"

    # def __float__(self):
    #     if self.shape != ():
    #         raise ValueError(f"Only scalar array can be converted to int (got shape {self.shape})")
    #     return float(self.data)

    def __jax_array__(self):
        """Allows JAX functions to treat this object as a JAX array.

        Returns:
            jax.Array: The underlying data array.
        """
        # Return the raw JAX array data
        return self.data

    def __array__(self):
        """Allows numpy functions to treat this object as a numpy array.

        Returns:
            numpy.ndarray: The underlying data array.
        """
        # Return the raw JAX array data
        return np.array(self.data)


def all_mapped_axes(args:Iterable[MappedArray]):
    axes = []
    for arg in args:
        for ax in arg.mapped_axes:
            if ax not in axes:
                axes.append(ax)
    return axes


class MappedFunction:
    def __init__(self, function):
        self._function = function

    def __call__(self, *args:MappedArray|ArrayLike, **kwargs):
        # don't vmap keyword arguments
        fun = lambda *args: self._function(*args, **kwargs)
        
        #args = tuple(arg if isinstance(arg,MappedArray) else Array(arg) for arg in args)
        new_args = []
        for arg in args:
            if isinstance(arg, MappedArray):
                new_args.append(arg)
            else:
                new_args.append(Array(arg))
        args = tuple(new_args)
        
        mapped_axes = all_mapped_axes(args)

        for n in range(len(mapped_axes)-1,-1,-1):
            ax = mapped_axes[n]
            ignore = mapped_axes[:n]
            in_axes = [arg.in_axis(ax, ignore) for arg in args]
            fun = jax.vmap(fun, in_axes=in_axes)

        fun = jax.jit(fun)

        data = [arg.data for arg in args]

        #print(f"calling {self._function} on {[d.shape for d in data]}")

        new_data = fun(*data)

        # jax.block_until_ready(data)
        #
        # import time
        # t0 = time.time()
        # new_data = fun(*data)
        # jax.block_until_ready(new_data)
        # t1 = time.time()
        # print("fun", self._function, "time:", t1-t0)

        def process_output(new):
            if not isinstance(new, jnp.ndarray):
                raise ValueError(f"function must return a jnp.ndarray (got {new})")

            new_mapped_axes = mapped_axes + [None] * (new.ndim - len(mapped_axes))

            if all(ax is None for ax in new_mapped_axes):
                return Array(new)
            else:
                return MappedArray(new, new_mapped_axes)

        if isinstance(new_data, jnp.ndarray):
            out = process_output(new_data)
        elif isinstance(new_data, tuple):
            out = tuple(process_output(new) for new in new_data)
        else:
            raise ValueError(f"function must return a jnp.ndarray or tuple of jnp.ndarray (got {new_data})")

        return out

        # if isinstance(new_data, jnp.ndarray):
        #     return process_output(new_data)
        # elif isinstance(new_data, tuple):
        #     return tuple(process_output(new) for new in new_data)
        # else:
        #     raise ValueError(f"function must return a jnp.ndarray or tuple of jnp.ndarray (got {new_data})")


class MappedSingleArgFunction:
    def __init__(self, function):
        self.mapped_fun = MappedFunction(function)

    def __call__(self, arg: MappedArray|ArrayLike):
        return self.mapped_fun(arg)

class MappedElementwise:
    def __init__(self, function):
        self.mapped_fun = MappedFunction(function)

    def __call__(self, arg1: MappedArray|ArrayLike, arg2: MappedArray|ArrayLike):
        arg1 = arg1 if isinstance(arg1, MappedArray) else Array(arg1)
        arg2 = arg2 if isinstance(arg2, MappedArray) else Array(arg2)

        same_shape = arg1.shape == arg2.shape
        arg1_scalar = arg1.shape == ()
        arg2_scalar = arg2.shape == ()

        if same_shape or arg1_scalar or arg2_scalar:
            return self.mapped_fun(arg1, arg2)
        else:
            raise ValueError(f"MappedPairwiseFunction only accepts args that are same shape or scalar (got {arg1.shape} and {arg2.shape})")

def wrap(fun):
    def call(*args:MappedArray|Array):
        #jax_args = [jnp.array(arg.shape) for arg in args]

        def jax_fun(*jax_args):
            import time
            t0 = time.time()
            my_args = [Array(jax_arg) for jax_arg in jax_args]
            t1 = time.time()
            print("args time", t1-t0)

            active_ranges = Range._active_ranges
            Range._active_ranges = {}
            out = fun(*my_args)
            Range._active_ranges = active_ranges
            return out.data

        return MappedFunction(jax_fun)(*args)
    return call

class Slot(Array):
    def __init__(self):
        self.data = None
        self.axes = None
        self._assigned = False

    def __setitem__(self, idx, value):
        if self._assigned:
            raise ValueError("Slot can only be assigned once")

        if not isinstance(value, MappedArray):
            raise ValueError("Can only assign MappedArray to Slot")

        # Convert idx to tuple if it's not already
        if not isinstance(idx, tuple):
            idx = (idx,)

        idx = process_axes(idx)

        origin_str = "["
        for n, i in enumerate(value.axes):
            if i is None:
                origin_str += ':'
            else:
                origin_str += i
            if n < len(value.axes)-1:
                origin_str += ','
        origin_str += "]"

        dest_str = "["
        for n, i in enumerate(idx):
            if i == slice(None):
                dest_str += ':'
            else:
                dest_str += i
            if n < len(idx) - 1:
                dest_str += ','
        dest_str += "]"

        for ax in Range._active_ranges:
            if ax not in idx:
                #warnings.warn(f"Active range {ax} not in indices being assigned",UserWarning)
                print(Range._active_ranges)
                raise SyntaxError(f"Active range {ax} not in indices being assigned in {dest_str} <- {origin_str}")

        num_empty = len([i for i in idx if i == slice(None)])
        if num_empty != value.ndim:
            raise IndexError(f"number of empty slots does not match in {dest_str} <- {origin_str}")
            #raise ValueError(f"Number of empty slots {num_empty} not equal to array dims {value.ndim}")

        for i in idx:
            if isinstance(i,str):
                if i not in value.mapped_axes:
                    raise IndexError(f"Slot assigned axis {i} doesn't exist in {dest_str} <- {origin_str}")

        #reordered = value.unmap_with_missing(*idx)
        reordered = value.unmap(*idx)

        self.data = reordered.data
        self.axes = reordered.axes
        self._assigned = True

    @property
    def shape(self):
        if self.data is None:
            return ()
        return super().shape

    @property
    def ndim(self):
        if self.data is None:
            raise ValueError("Slot does not have ndim until assigned")
        return super().ndim

    def __repr__(self):
        if self.data is None:
            return "Slot(unassigned)"
        mapped_repr = super().__repr__()
        # Replace "MappedArray" with "Array" (only the first occurrence)
        return mapped_repr.replace("MappedArray", "Slot", 1)

from jax.numpy import linalg as jlinalg # Import jax.linalg

# --- JAX NumPy Wrappers ---

# Element-wise mathematical functions
cos = MappedFunction(jnp.cos)
sin = MappedFunction(jnp.sin)
tan = MappedFunction(jnp.tan)
arccos = MappedFunction(jnp.arccos)
arcsin = MappedFunction(jnp.arcsin)
arctan = MappedFunction(jnp.arctan)
exp = MappedFunction(jnp.exp)
log = MappedFunction(jnp.log)
log10 = MappedFunction(jnp.log10)
sqrt = MappedFunction(jnp.sqrt)
square = MappedFunction(jnp.square)
abs = MappedFunction(jnp.abs) # Note: abs is built-in, jnp.abs preferred
absolute = MappedFunction(jnp.absolute)
sign = MappedFunction(jnp.sign)
ceil = MappedFunction(jnp.ceil)
floor = MappedFunction(jnp.floor)
round = MappedFunction(jnp.round)

# Element-wise comparison functions
equal = MappedElementwise(jnp.equal)
not_equal = MappedElementwise(jnp.not_equal)
less = MappedElementwise(jnp.less)
less_equal = MappedElementwise(jnp.less_equal)
greater = MappedElementwise(jnp.greater)
greater_equal = MappedElementwise(jnp.greater_equal)

# Element-wise logical functions
logical_and = MappedElementwise(jnp.logical_and)
logical_or = MappedElementwise(jnp.logical_or)
logical_not = MappedElementwise(jnp.logical_not)
logical_xor = MappedElementwise(jnp.logical_xor)

# Element-wise bitwise functions
bitwise_and = MappedElementwise(jnp.bitwise_and)
bitwise_or = MappedElementwise(jnp.bitwise_or)
bitwise_not = MappedElementwise(jnp.bitwise_not)
bitwise_xor = MappedElementwise(jnp.bitwise_xor)

# Basic array operations (element-wise)
add = MappedElementwise(jnp.add)
subtract = MappedElementwise(jnp.subtract)
multiply = MappedElementwise(jnp.multiply)
divide = MappedElementwise(jnp.divide)
power = MappedElementwise(jnp.power)
mod = MappedElementwise(jnp.mod)
maximum = MappedElementwise(jnp.maximum) # Element-wise maximum
minimum = MappedElementwise(jnp.minimum) # Element-wise minimum

def get_ndim(a):
    if hasattr(a, 'ndim'):
        return a.ndim
    else:
        return jnp.asarray(a).ndim

def map_1d(jax_fun):
    mapped_fun = MappedFunction(jax_fun)
    def safe_fun(*args, **kwargs):
        for a in args:
            if not get_ndim(a) == 1:
                raise ValueError(f"all arguments must be 1D (got {a})")
        return mapped_fun(*args, **kwargs)
    return safe_fun

def map_1d_or_2d(jax_fun):
    mapped_fun = MappedFunction(jax_fun)
    def safe_fun(*args, **kwargs):
        for a in args:
            if not 1 <= get_ndim(a) <= 2:
                raise ValueError(f"all arguments must be 1D (got {a})")
        return mapped_fun(*args, **kwargs)
    return safe_fun

def map_2d(jax_fun):
    mapped_fun = MappedFunction(jax_fun)
    def safe_fun(*args, **kwargs):
        for a in args:
            if not get_ndim(a) == 2:
                raise ValueError(f"all arguments must be 1D (got {a})")
        return mapped_fun(*args, **kwargs)
    return safe_fun

# More complex operations
matmul = map_1d_or_2d(jnp.matmul)
dot = map_1d_or_2d(jnp.dot)
tensordot = MappedFunction(jnp.tensordot)
outer = map_1d(jnp.outer)
inner = map_1d(jnp.inner)

# reductions
sum = MappedFunction(jnp.sum)
prod = MappedFunction(jnp.prod)
mean = MappedFunction(jnp.mean)
std = MappedFunction(jnp.std)
cov = MappedFunction(jnp.cov)
var = MappedFunction(jnp.var)
min = MappedFunction(jnp.min) # jnp.min for element-wise min
max = MappedFunction(jnp.max) # jnp.max for element-wise max

convolve = MappedFunction(jnp.convolve)
argmax = MappedFunction(jnp.argmax)

ravel = MappedFunction(jnp.ravel)

# --- JAX Linear Algebra Wrappers Namespace ---

class _LinalgNamespace:
    cholesky = staticmethod(map_2d(jlinalg.cholesky))
    det = staticmethod(map_2d(jlinalg.det))
    eig = staticmethod(map_2d(jlinalg.eig))
    eigh = staticmethod(map_2d(jlinalg.eigh))
    eigvals = staticmethod(map_2d(jlinalg.eigvals))
    eigvalsh = staticmethod(map_2d(jlinalg.eigvalsh))
    inv = staticmethod(map_2d(jlinalg.inv))
    norm = MappedFunction(jlinalg.norm)
    qr = staticmethod(map_2d(jlinalg.qr))
    slogdet = staticmethod(map_2d(jlinalg.slogdet))
    svd = staticmethod(map_2d(jlinalg.svd))
    solve = staticmethod(map_1d_or_2d(jlinalg.solve))
    #solve = MappedFunction(jlinalg.solve)

# Create an instance of the namespace
linalg = _LinalgNamespace()

Shape = Union[int, Sequence[int]]

def eye(N: int, M: Optional[int] = None, k: int = 0, dtype: Optional[Any] = None) -> Array:
    """Creates an identity Array (wrapper for jnp.eye).

    Args:
        N: Number of rows.
        M: Number of columns (defaults to N).
        k: Index of the diagonal.
        dtype: Data type of the returned array.

    Returns:
        An Array containing the identity matrix.
    """
    return Array(jnp.eye(N, M=M, k=k, dtype=dtype))

def zeros(shape: Shape, dtype: Optional[Any] = None) -> Array:
    """Creates an Array filled with zeros (wrapper for jnp.zeros).

    Args:
        shape: Shape of the new array, e.g., (2, 3) or 5.
        dtype: Data type of the returned array.

    Returns:
        An Array of the given shape and type, filled with zeros.
    """
    return Array(jnp.zeros(shape, dtype=dtype))

def ones(shape: Shape, dtype: Optional[Any] = None) -> Array:
    """Creates an Array filled with ones (wrapper for jnp.ones).

    Args:
        shape: Shape of the new array, e.g., (2, 3) or 5.
        dtype: Data type of the returned array.

    Returns:
        An Array of the given shape and type, filled with ones.
    """
    return Array(jnp.ones(shape, dtype=dtype))

class MappedRange(MappedArray):
    pass

# class MappedRange(MappedArray):
#     # act like a MappedArray
#
#     def __init__(self, value, var_name):
#         self.value = value
#         self.var_name = var_name
#
#     @property
#     def data(self):
#         # only compute data on demand
#         return jnp.arange(self.value)
#
#     @property
#     def axes(self):
#         return (self.var_name,)
#
#     @property
#     def shape(self):
#         return ()
#
#     @property
#     def mapped_axes(self):
#         return (self.var_name,)

class Range:
    _active_ranges = {}

    def __init__(self, value):
        self.value = value
        self.var_name = None
        self.registered_name = None

    def new_random_name(self):
        import random, string
        characters = string.ascii_letters
        while True:
            var_name = 'range_' + ''.join(random.choice(characters) for i in range(4))
            if var_name not in self._active_ranges:
                return var_name

    def __enter__(self):
        var_name = self.new_random_name()
        assert var_name not in self._active_ranges
        self._active_ranges[var_name] = True
        self.registered_name = var_name
        return MappedRange(jnp.arange(self.value), [var_name])
        #return MappedRange(self.value, var_name)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.registered_name is not None:
            del Range._active_ranges[self.registered_name]
            self.registered_name = None
        return False

# flat and grad

def array_flatten(x: MappedArray):
    #print(f"flattening {x=}")
    children = (x.data,)
    aux_data = (x.axes,type(x))
    return children, aux_data


def array_unflatten(aux_data, children):
    # Do unflattening without calling ntensor.__init__ to avoid issues discussed here:
    # https://docs.jax.dev/en/latest/working-with-pytrees.html
    # in "Custom pytrees and initialization with unexpected values" section
    #print("unflattening", aux_data, children)
    data, = children
    axes, ArrayClass = aux_data
    obj = object.__new__(ArrayClass)
    obj.data = data
    obj.axes = axes
    return obj

# def array_flatten(x: Array):
#     # print(f"flattening {x=}")
#     children = ()
#     aux_data = (x.data, x.axes)
#     return children, aux_data
#
#
# def array_unflatten(aux_data, children):
#     # Do unflattening without calling ntensor.__init__ to avoid issues discussed here:
#     # https://docs.jax.dev/en/latest/working-with-pytrees.html
#     # in "Custom pytrees and initialization with unexpected values" section
#     data, axes = aux_data
#     assert children == ()
#     obj = object.__new__(Array)
#     obj.data = data
#     obj.axes = axes
#     return obj


# Global registration
jax.tree_util.register_pytree_node(MappedArray, array_flatten, array_unflatten)
jax.tree_util.register_pytree_node(Array, array_flatten, array_unflatten)
jax.tree_util.register_pytree_node(Slot, array_flatten, array_unflatten)
#jax.tree_util.register_pytree_node(Range, array_flatten, array_unflatten)

def grad(fun, argnums=0):
    def myfun(*args, **vargs):
        return jnp.array(fun(*args, **vargs))
    return jax.grad(myfun, argnums)

def value_and_grad(fun, argnums=0):
    def myfun(*args, **vargs):
        return jnp.array(fun(*args, **vargs))
    return jax.value_and_grad(myfun, argnums)