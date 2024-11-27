'''def twos_complement(hex_value):
# converts hex number to decimal, including negative hex numbers

    decimal_value = int(hex_value, 16)
    bit_length = len(hex_value) * 4
    if decimal_value & (1 << (bit_length - 1)):
        decimal_value -= 1 << bit_length
    return decimal_value'''

'''def twos_complement(hex_value):
    # Convert hex number to binary string
    binary_value = bin(int(hex_value, 16))[2:]

    # Calculate bit length
    bit_length = len(binary_value)

    # Convert binary string to decimal
    decimal_value = int(binary_value, 2)

    # Check if the number is negative and apply two's complement if necessary
    if binary_value[0] == '1':
        decimal_value -= 1 << bit_length

    return decimal_value'''

'''def twos_complement(hex_value, bit_length=256):
    # Convert hex number to binary string padded up to bit_length
    binary_value = bin(int(hex_value, 16))[2:].zfill(bit_length)

    # Convert binary string to decimal
    decimal_value = int(binary_value, 2)

    # Check if the number is negative and apply two's complement if necessary
    if binary_value[0] == '1':  # Checking the most significant bit (MSB)
        decimal_value -= 1 << bit_length

    return decimal_value'''

def twos_complement(hex_value, bit_length=256):

    if hex_value[2] == 'f':
        # Convert hex number to binary string padded up to bit_length
        binary_value = bin(int(hex_value, 16))[2:].zfill(bit_length)

        # Convert binary string to decimal
        decimal_value = int(binary_value, 2)

        # Check if the number is negative and apply two's complement if necessary
        if binary_value[0] == '1':  # Checking the most significant bit (MSB)
            decimal_value -= 1 << bit_length

        return decimal_value

    else:
        return int(hex_value,16)


#test= '0x00000000000000000000000000000000000000000000000001efd74e1027f881'

#test = '0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffe564d2704'
#print(twos_complement(test))