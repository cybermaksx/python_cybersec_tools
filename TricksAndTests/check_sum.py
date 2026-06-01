def calculate_checksum(data):
    """
    Calculates the Internet Checksum (RFC 1071) for the given byte data.
    This algorithm is used in IP, TCP, UDP, and ICMP headers.
    """

    # Step 1: Padding to ensure even length.
    # The algorithm processes data in 16-bit (2-byte) words.
    # If the data length is odd, we append a zero byte to make it even.
    # This prevents index errors and ensures the last byte is processed correctly.
    if len(data) % 2 != 0:
        data += b'\x00'

    # Initialize the checksum accumulator to zero.
    # This variable will hold the running sum of all 16-bit words.
    s = 0

    # Step 2: Iterate through the data in steps of 2 bytes (16 bits).
    # range(start, stop, step) generates indices: 0, 2, 4, ...
    for i in range(0, len(data), 2):

        # Step 3: Combine two consecutive bytes into a single 16-bit word.
        # data[i] is the high-order byte (most significant).
        # data[i+1] is the low-order byte (least significant).
        # Shifting left by 8 bits (<< 8) is equivalent to multiplying by 256.
        # This effectively moves the first byte to the upper 8 bits of the word.
        word = (data[i] << 8) + data[i + 1]

        # Add the 16-bit word to the running sum.
        # Note: 's' can grow larger than 16 bits during this accumulation.
        s += word

    # Step 4: Handle carries (overflow beyond 16 bits).
    # The Internet Checksum uses "ones' complement" arithmetic.
    # Any carry bits that overflow beyond the 16th bit must be added back to the least significant bits.
    
    # (s >> 16) extracts the upper 16 bits (the carry).
    # (s & 0xFFFF) extracts the lower 16 bits (the current sum).
    # We add them together.
    s = (s >> 16) + (s & 0xFFFF)

    # Step 5: Handle any potential carry from the previous addition.
    # Adding the carry might itself generate a new carry (though rare, it's possible).
    # We repeat the process to ensure the result fits within 16 bits.
    s += (s >> 16)

    # Step 6: Finalize the checksum.
    # ~s performs a bitwise NOT (one's complement inversion).
    # & 0xFFFF masks the result to keep only the lower 16 bits.
    # This ensures the return value is a valid 16-bit unsigned integer.
    return ~s & 0xFFFF
