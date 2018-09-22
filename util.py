"""
Mehrab Mehdi Islam
Student Id: 1545664

Alexandar Chan
Student Id: 1544806
"""
import bitio
import huffman


def read_tree(bitreader):
    '''
    Read a description of a Huffman tree from the given bit reader,
    and construct and return the tree. When this function returns, the
    bit reader should be ready to read the next bit immediately
    following the tree description.

    Huffman trees are stored in the following format:
      * TreeLeaf is represented by the two bits 01, followed by 8 bits
          for the symbol at that leaf.
      * TreeLeaf that is None (the special "end of message" character)
          is represented by the two bits 00.
      * TreeBranch is represented by the single bit 1, followed by a
          description of the left subtree and then the right subtree.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.

    Returns:
      A Huffman tree constructed according to the given description.
    '''

    # bit == 1, TreeBranch
    if bitreader.readbit() == 1:
        return huffman.TreeBranch(read_tree(bitreader), read_tree(bitreader))

    # bit == 0, could be either TreeLeaf(value) or TreeLeafEndMessage()
    else:
        if bitreader.readbit() == 0:
            return huffman.TreeLeaf(None)
        else:
            value = bitreader.readbits(8)
            return huffman.TreeLeaf(value)


def decode_byte(tree, bitreader):
    """
    Reads bits from the bit reader and traverses the tree from
    the root to a leaf. Once a leaf is reached, bits are no longer read
    and the value of that leave is returned.

    Args:
      bitreader: An instance of bitio.BitReader to read the tree from.
      tree: A Huffman tree.

    Returns:
      Next byte of the compressed bit stream.
    """
    while True:
        # if its tree leaf, return the value
        if isinstance(tree, huffman.TreeLeaf):
            return tree.value
        elif isinstance(tree, huffman.TreeBranch):
            # if its branch, go left if bit==0 or right if btt== 1
            if bitreader.readbit() == 1:
                tree = tree.right
            else:
                tree = tree.left
        else:
            # else raise error
            raise TypeError('{} is not a tree type'.format(type(tree)))


def decompress(compressed, uncompressed):
    '''First, read a Huffman tree from the 'compressed' stream using your
    read_tree function. Then use that tree to decode the rest of the
    stream and write the resulting symbols to the 'uncompressed'
    stream.

    Args:
      compressed: A file stream from which compressed input is read.
      uncompressed: A writable file stream to which the uncompressed
          output is written.

    '''
    # call the class
    bitreader = bitio.BitReader(compressed)
    bitwriter = bitio.BitWriter(uncompressed)
    tree = read_tree(bitreader)
    # read bits from the file, decode them using tree continiously
    # until end-of-message is reached
    while True:
        decodedByte = decode_byte(tree, bitreader)
        # if end-of-message is seen, stop reading
        if decodedByte is None:
            break
        # write the decodedByte to the output
        bitwriter.writebits(decodedByte, 8)


def write_tree(tree, bitwriter):
    '''Write the specified Huffman tree to the given bit writer.  The
    tree is written in the format described above for the read_tree
    function.

    DO NOT flush the bit writer after writing the tree.

    Args:
      tree: A Huffman tree.
      bitwriter: An instance of bitio.BitWriter to write the tree to.
    '''
    if isinstance(tree, huffman.TreeBranch):
        bitwriter.writebit(1)
        # recurse over left and right of the tree
        write_tree(tree.left, bitwriter)
        write_tree(tree.right, bitwriter)
    elif isinstance(tree, huffman.TreeLeaf):
        # this is leaf
        bitwriter.writebit(0)
        bitwriter.writebit(1)
        value = tree.value
        x = int(0 if value is None else value)
        bitwriter.writebits(x, 8)

    elif isinstance(tree, huffman.TreeLeaf(None)):
        # this is end message
        bitwriter.writebit(0)
        bitwriter.writebit(0)


def compress(tree, uncompressed, compressed):
    '''First write the given tree to the stream 'compressed' using the
    write_tree function. Then use the same tree to encode the data
    from the input stream 'uncompressed' and write it to 'compressed'.
    If there are any partially-written bytes remaining at the end,
    write 0 bits to form a complete byte.

    Flush the bitwriter after writing the entire compressed file.

    Args:
      tree: A Huffman tree.
      uncompressed: A file stream from which you can read the input.
      compressed: A file stream that will receive the tree description
          and the coded input data.
    '''
    # call Bitwrite class
    bitwriter = bitio.BitWriter(compressed)
    # write tree to the uncomressed file
    write_tree(tree, bitwriter)

    # for reading bytes from the uncompressed input file
    bitreader = bitio.BitReader(uncompressed)

    # make the encoding table
    encodingTable = huffman.make_encoding_table(tree)

    # Read each byte from the uncompressed input file
    while True:
        try:
            # read 8 bits
            inputByte = bitreader.readbits(8)
            # encode it using the table
            encodedByte = encodingTable[inputByte]
            # write the encodedByte to compressed output
            for i in encodedByte:
                bitwriter.writebit(i)

        except EOFError:
            # the end should be none
            # encode using encoding table
            encodedByte = encodingTable[None]
            # write encodedByte to output
            for i in encodedByte:
                bitwriter.writebit(i)
            break
    bitwriter.flush()
