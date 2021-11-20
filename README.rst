Unitoad
-------

Pack binary data into Unicode UTF-8 strings.


## Entoad

Given a string of bits::

    abcd efgh  ijkl mnop  qrst uvwx  yzAB CD

We entoad it into the range U+0000 to U+007F.
In this general case, we entoad the first 8 bits as::

    P(a=0) = 1/2
    0bcd egfh

Except, if a = 1, then UTF-8 would see this as a continuation or multi-byte start byte.
So instead, we entoad these cases into the range from U+0080 through U+07FF.
In this case, the first 12 bits are entoaded as::

    P(a=1) = 1/2
    P(bcde!=0000) = 15/16
    110b cdef  10gh ijkl

Except, if bcde = 0000, then UTF-8 would see this as an overlong encoding.
Instead, we entoad this into the range from U+0800 through U+FFFF.
In this case, we entoad the first 21 bits as::

    P(a=1) = 1/2
    P(bcde=0000) = 1/16
    P(fghij!=00000) = 31/32
    1110 fghi  10jk lmno  10pq rstu

Except, if fghij = 00000, it's an overlong encoding again.
Instead, we entoad this into the range from U+01FFFF through U+0FFFFF.
In this case, we entoad the first 30 bits as::

    P(a=1) = 1/2
    P(bcde=0000) = 1/16
    P(fghij=00000) = 1/32
    P(klmn!=0000) = 15/16
    1111 00kl  10mn opqr  10st uvwx  10yz ABCD

Except, if klmn = 0000, it's an overlong encoding again.
We can't do 5 byte encodings in UTF-8, so instead, we entoad this into Private Use Area B, U+100000 through U+10FFFF.
In this case, we entoad the first 30 bits as:: 

    P(a=1) = 1/2
    P(bcde=0000) = 15/16
    P(fghij=00000) = 31/32
    P(klmn=0000) = 1/16
    1111 0100  1000 opqr  10st uvwx  10yz ABCD


TODO: How do we encode the end of a stream?
Special semantics about the last character?
