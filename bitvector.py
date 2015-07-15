#!/usr/bin/python

"""
This is William Brafford's 'bitvector' module.

In Programming Pearls, Second Edition, Jon Bently writes that a bitmap data
structure "represents a dense set over a finite domain when each element occurs
at most once and no other data is assocated with the element." The BitVector
class in this module is an implementation of a bitmap data structure that uses
Python's bytearray class. The bytearray class, in turn, is "a mutable sequence
of integers in the range 0 <= x < 256." A byte-sized integer is represented in
8 bits. We can show this using this module's conversion function:

>>> int_to_binary_string(249)
'11111001'

In an array of, say, 100 bytes, there are 800 bits, so we have a very compact
format for representing a set of up to 800 integers. If the integer 249 were
the first byte in our bit vector, it could represent the set [0, 1, 2, 3, 4,
7].

Creating a bitvector requires only a maximum value. Then we can set values and
test whether the bitvector contains them:
>>> bv = BitVector(maxval=10)
>>> bv.contains(4)
False
>>> bv.set(4)
>>> bv.contains(4)
True

We can output our bitvector as a list:
>>> bv.set(9)
>>> print bv.convert_to_list()
[4, 9]
"""

def int_to_binary_string(n):
    """Given an integer that fits in 8 bits, return a binary representation.

    Python is good at displaying integers, but not so great at showing off the
    specific byte units we're dealing with here. For convenience, we'll want to
    be able to show off our binary representations of any integer that can fit
    in a byte. For example:
    
    >>> print int_to_binary_string(2)
    00000010
    >>> print int_to_binary_string(255)
    11111111

    Of course, 0 <= n <= 255:
    >>> int_to_binary_string(-23)
    Traceback (most recent call last):
        ...
    ValueError: n must be between 0 and 255 inclusive
    >>> int_to_binary_string(256)
    Traceback (most recent call last):
        ...
    ValueError: n must be between 0 and 255 inclusive

    Python has a format string that does this very quickly.
    """
    
    if n < 0 or n > 255:
        raise ValueError('n must be between 0 and 255 inclusive')
    return "{:0>8b}".format(n)

def binary_string_to_int(b):
    """Given a representation of an 8-bit binary string, return an integer.

    We'll also want to be able to convert our binary strings back into integer
    format. Python's integer constructor will handle this for us.

    >>> binary_string_to_int('00000010')
    2

    This makes a nice inverse for our previous function.
    >>> binary_string_to_int(int_to_binary_string(12))
    12
    >>> int_to_binary_string(binary_string_to_int('11010011'))
    '11010011'
    """
    return int(b, 2)

class BitVector:
    def __init__(self, maxval=255, minval=0):
        """Initialize the bitvector for the given range.

        >>> bv = BitVector(300)

        There's a one in eight chance that we'll have a few more bits than we
        need, since we can only define the underlying bytearray in terms of
        bytes.

        >>> underlying_bytearray = bv.ba
        >>> len(underlying_bytearray)
        38
        >>> 38 * 8
        304

        Is there a downside to letting clients use those extra bits? In terms
        of performance, I doubt it. But it's also probably a sane bound to use
        on our set method, since we do need to catch attempts to set values
        outside of our bitvector's range. So we'll hold on to the maximum
        value.

        """
        self.maxval = maxval
        self.ba = bytearray((maxval / 8) + 1)

    def set(self, num):
        """Add an integer to the bitvector set

        We need to determine which byte in the bitvector the integer is in, and
        we need to determine the integer's position within the byte. Rather
        arbitrarily, I've chosen to index my vector "from the left", so that the
        0th byte of the underlying bytevector contains the integers 0-7.


        -------------------------------------------------
        | byte 0                | byte 1                |
        |-----------------------|-----------------------|
        | 0| 1| 2| 3| 4| 5| 6| 7| 8| 9|10|11|12|13|14|15|
        |-----------------------|-----------------------|
        | 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0| 0|
        -------------------------------------------------
        
        If the first number we add to our bit vector is 10, we need to flip the
        third bit (from left) in the second byte (from left). This being a
        computer program, we're indexing from zero, of course.

        >>> num = 10
        >>> 10 / 8   # byte position
        1
        >>> 10 % 8   # bit position
        2

        How do we actually flip a single bit? In the underlying bytearray, we
        can only set bytes. We'll have to use Python's bitwise operators on
        integers.
        
        First, the leftward bit shift. It's pretty simple: n << m
        pushes the bits in n over m places. (There are some wrinkles with
        overflow but we won't be running into those in this function.)

        >>> int_to_binary_string(23)
        '00010111'
        >>> int_to_binary_string(23 << 3)
        '10111000'

        Next, there's bitwise OR, which is n | m. Each bit in the result is
        '1' if either n or m has a corresponding bit of '1'.

        >>> binary_string_to_int('01010111')
        87
        >>> binary_string_to_int('10100100')
        164
        >>> binary_string_to_int('11110111')  # what the result of a bitwise or
        ...                                   # ought to be
        247
        >>> 87 | 164
        247

        Putting these two concepts together, if you have a byte and need to the
        fifth bit to true, a bitwise OR with '00001000' would do the trick. And
        bit shifting is a nice way of creating these operations: you can shift
        the number 1 leftwards. (The bit indexed '4' is 3 positions from the
        bit indexed '7', so we shift by 7 - 4 = 3.)

        >>> int_to_binary_string(1 << (7 - 4))
        '00001000'
        >>> binary_string_to_int('01010111') | (1 << (7 - 4))
        95
        >>> int_to_binary_string(95)
        '01011111'

        And that's how you use bitwise operators to flip bits in bytes!

        >>> bv = BitVector(20)
        >>> bv.set(15)


        Note: To avoid confusion, we'll throw an error if num is out of the
        nominal range of the bit vector, even if the bits are technically
        available.

        >>> bv = BitVector(300)
        >>> bv.set(303)
        Traceback (most recent call last):
            ...
        ValueError: Index out of range (len=300)
        """
        if num >= self.maxval:
            raise ValueError("Index out of range (len={})".format(self.maxval))
        byte_pos = num / 8
        bit_pos = num % 8
        self.ba[byte_pos] = self.ba[byte_pos] | (1 << (7 - bit_pos))

    def contains(self, num):
        """Check to see if num is contained in our set of integers

        This method needs to check whether a particular bit in the bitvector
        is set to 'true'. However, we can only retrieve bytes, so we need to
        use bitwise tricks here as well. We'll use the left shift and the OR
        that we used previously, as well as an XOR.

        So, let's say we're starting with '11010111' and want to check whether
        the first bit is set. If we use a bitwise OR with a string whose
        first bit is 0 and whose other bits are all 1, we'll have an
        interesting result. If the first bit of our original string is 1,
        the result of the OR will be a byte of 1's, which equals 255.

        >>> binary_string_to_int('11010111')
        215
        >>> binary_string_to_int('01111111')
        127
        >>> binary_string_to_int('11111111')  # what the result of a bitwise or
        ...                                   # ought to be
        255
        >>> 215 | 127
        255

        But how do we generate the '01111111' that we need? You might want to
        use the '~' bit flip operator, but Python integers use more than a
        byte and this won't give us the number we're after. Instead, we can use
        the XOR ('exclusive or') operator, which is true when one bit is true
        but not when both bits are true.

        >>> binary_string_to_int('11111111')
        255
        >>> binary_string_to_int('10000000')
        128
        >>> binary_string_to_int('01111111')
        127
        >>> 255 ^ 128
        127

        So putting these two steps together, we just have to shift a bit to
        the right position, flip our byte by an XOR with 255, and then use
        an inclusive OR on the target byte and the flipped byte. If this is
        255, then the integer is included in our set.

        >>> bv = BitVector(20)
        >>> bv.set(15)
        >>> bv.contains(15)
        True
        >>> bv.contains(16)
        False
        >>> bv.contains(21)
        Traceback (most recent call last):
            ...
        ValueError: Index out of range (len=20)
        """

        if num >= self.maxval:
            raise ValueError("Index out of range (len={})".format(self.maxval))
        byte_pos = num / 8
        bit_pos = num % 8
        raw = 1 << (7 - bit_pos)
        masked = raw ^ 255
        compared = masked | self.ba[byte_pos]
        return 255 == compared

    def printv(self):
        """Prints the values in the set
        
        >>> bv = BitVector(16)
        >>> for i in [0, 3, 6, 11, 2, 8]: bv.set(i)
        >>> bv.printv() # doctest: +NORMALIZE_WHITESPACE, +ELLIPSIS
        0 2 3 ... 11
        """

        for i in range(self.maxval):
            if self.contains(i):
                print(i)

    def convert_to_list(self):
        """Returns the set as a list

        >>> bv = BitVector(16)
        >>> for i in [0, 3, 6, 11, 2, 8]: bv.set(i)
        >>> bv.convert_to_list()
        [0, 2, 3, 6, 8, 11]
        """
        return [i for i in range(self.maxval)
                if self.contains(i)]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
