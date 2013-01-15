#!/usr/bin/env python
# -*- coding:utf8 -*-

import struct

import dnslib

from gevent.server import StreamServer, DatagramServer

import stardict


def notfound(word):
    yield "No word '%s' found, did you mean:" % word
    for i, w in enumerate(stardict.get_close_matches(word)):
        yield " %d. %s %s" % (i+1, w, stardict.check(w).replace('\n', ' '))


def split_len(seq, length):
    for i in xrange(0, len(seq), length):
        yield seq[i:i+length]


def make_jianbing(query):
    response = query.reply()
    response.header.ra = 0
    word = query.q.qname.label[0]
    desc = stardict.check(word)
    desc = [desc] if desc else notfound(word)
    # force change rtype to TXT
    response.rr = []

    for txt in desc:
        # if len(txt) > 255
        for part in split_len(txt, 255):
            response.add_answer(
                dnslib.RR(query.q.qname, dnslib.QTYPE.TXT,
                          rdata=dnslib.TXT(part), ttl=5))

    # no Recursion Available
    return response


class UdpJianbingServer(DatagramServer):

    def handle(self, data, address):
        # print '%s: got %r' % (address[0], data)

        query = dnslib.DNSRecord.parse(data)

        # print query
        response = make_jianbing(query)
        wire = response.pack()
        if len(wire) >= 512:
            response.rr = []
            response.header.a = 0
            response.header.tc = 1
            wire = response.pack()
        self.socket.sendto(wire, address)


class TcpJianbingServer(StreamServer):

    def handle(self, socket, address):
        # print ('New connection from %s:%s' % address)
        # using a makefile because we want to use readline()
        fileobj = socket.makefile()
        ldata = fileobj.read(2)
        (l,) = struct.unpack("!H", ldata)

        data = fileobj.read(l)
        # print '%r' % data
        query = dnslib.DNSRecord.parse(data)

        # print query
        response = make_jianbing(query)
        wire = response.pack()
        wire = struct.pack('!H', len(wire)) + wire
        fileobj.write(wire)
        fileobj.flush()


if __name__ == '__main__':
    print 'Already here'
    udpserver = UdpJianbingServer(':53')
    udpserver.start()

    tcpserver = TcpJianbingServer(':53')
    tcpserver.serve_forever()
