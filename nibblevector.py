#!/usr/bin/python

"""
Nibblevector - 20 July 2015

This is the nibblevector module, a kind of companion to the bitvector module.
The idea in the bit vector is that we access individual bits of a byte array;
here, we access the bits in groups of four. The bitvector has the semantics of
a set, at least the way I implemented it, but here we're back in the realm of
traditional arrays: the nth position in the nibble vector can take values from
zero to fifteen.

We have to initialize with length, and from there we've hijacked the Python
interface for lists.

# example of usage

I've also put in the iterator.

# example of usage.

We can return a normal Python list too:

# example of usage
"""

class NibbleVector:
    """A vector of integers between 0 and 15.

    Emulating as many sequence features as I can. See:
    https://docs.python.org/2.7/reference/datamodel.html#emulating-container-types
    """
    def __init__(self, size=255):
        """Initialize the nibble vector for the given range.

        >>> nv = NibbleVector(5)
        >>> underlying_bytearray = nv.ba
        >>> len(underlying_bytearray)
        3
        """
        self.size = size
        self.ba = bytearray((size + 1) / 2)
        # for the iterator
        self.index = 0

    def __len__(self):
        """Return the length of the nibble vector.

        Note: there may be an "unused" nibble at the end of the underlying
        vector, since the byte array can only hold an even number of nibbles.
        >>> nv = NibbleVector(5)
        >>> len(nv)
        5
        """
        return self.size

    def __getitem__(self, key):
        """Get an item from the vector.

        >>> nv = NibbleVector(5)
        >>> nv[3]
        0

        Negative indexing will work.
        >>> nv[4] = 12
        >>> nv[-1]
        12

        We raise a value error if the index is out of range.
        >>> nv[5]
        Traceback (most recent call last):
            ...
        ValueError: Index out of range (len=5)

        We need to support slice objects, too.
        """
        if key >= self.size or key < -self.size:
            raise ValueError("Index out of range (len={})".format(self.size))
        if key < 0:
            return self.__getitem__(self.size + key)
        byte_pos = key / 2
        nib_pos = key % 2
        mask = 15 << (4 * (1 - nib_pos))
        masked_result = self.ba[byte_pos] & mask
        result = masked_result >> (4 * (1 - nib_pos))
        return result

    def __setitem__(self, key, value):
        """Set an item in the vector

        >>> nv = NibbleVector(5)
        >>> nv[2] = 10
        >>> nv[3] = 14
        >>> nv[2]
        10
        >>> nv[3]
        14

        Our values must be proper four-bit integers...
        >>> nv[3] = 17
        Traceback (most recent call last):
            ...
        ValueError: nibble must be in range(0, 16)

        And our keys must be in range.
        >>> nv[6] = 4
        Traceback (most recent call last):
            ...
        ValueError: Index out of range (len=5)
        """
        if key >= self.size or key < -self.size:
            raise ValueError("Index out of range (len={})".format(self.size))
        if value < 0 or value >= 16:
            raise ValueError("nibble must be in range(0, 16)")
        if key < 0:
            return self.__setitem__(self.size + key, value)

        byte_pos = key / 2
        nib_pos = key % 2
        mask = 15 << (4 * nib_pos)
        masked_result = self.ba[byte_pos] & mask
        result = masked_result + (value << (4 * (1 - nib_pos)))
        self.ba[byte_pos] = result

    def __iter__(self):
        """The nibble vector can be an iterator.

        >>> nv = NibbleVector(5)
        >>> for i in range(5): nv[i] = i + 1
        >>> for n in nv: print n   # doctest: +NORMALIZE_WHITESPACE
        1 2 3 4 5

        We should be able to iterate twice.
        >>> for r in nv: print r   # doctest: +NORMALIZE_WHITESPACE
        1 2 3 4 5
        """
        return self

    def next(self):
        if self.index == self.size:
            raise StopIteration
        value = self.__getitem__(self.index)
        self.index = self.index + 1
        return value

if __name__ == "__main__":
    import doctest
    doctest.testmod()
