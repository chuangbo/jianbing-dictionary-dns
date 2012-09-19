import sys
import os
import struct


DICT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'stardict-lazyworm-ec-2.4.2/lazyworm-ec'))


word_idx = dict()

def prepare():
    idx_data = open(DICT+'.idx', 'r').read()
    dict_data = open(DICT+'.dict', 'r').read()

    idx_data_length = len(idx_data)
    offset = 0

    while offset < idx_data_length:
        word_length = idx_data.find('\0', offset) - offset
        (word, eof, word_offset, word_data_length) = struct.unpack_from('!%dssLL' % word_length, idx_data, offset)
        offset += len(word)+1+4+4

        # print word
        # print word_offset
        # print word_data_length
        # print word_desc
        word_desc = dict_data[word_offset:word_offset+word_data_length]
        word_idx[word] = word_desc

prepare()

def check(word):
    return word_idx.get(word)