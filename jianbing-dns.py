#!/usr/bin/env python
# -*- coding:utf8 -*-

import struct

import dns.message
import dns.renderer
import dns.flags
import dns.rdtypes.txtbase

from gevent.server import StreamServer, DatagramServer

import stardict

def make_jianbing(query):
    response = dns.message.make_response(query)
    response.flags |= dns.flags.AA
    word = query.question[0].name.labels[0]
    desc = stardict.check(word) or 'No such word %s' % word
    # desc.replace(';', '\;')
    # desc = ' '.join(desc.splitlines())
    response.answer.append(dns.rrset.from_rdata(query.question[0].name, 5, dns.rdtypes.txtbase.TXTBase(dns.rdataclass.IN, dns.rdatatype.TXT, desc)))
    return response

class UdpJianbingServer(DatagramServer):

    def handle(self, data, address):
        # print '%s: got %r' % (address[0], data)

        query = dns.message.from_wire(data)

        # print query
        response = make_jianbing(query)
        wire = response.to_wire()
        if len(wire) >= 512:
            response.answer = []
            response.flags |= dns.flags.TC
            wire = response.to_wire()
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
        query = dns.message.from_wire(data)

        # print query
        response = make_jianbing(query)
        wire = response.to_wire()
        wire = struct.pack('!H', len(wire)) + wire
        fileobj.write(wire)
        fileobj.flush()


if __name__ == '__main__':
    print ('Already here')
    udpserver = UdpJianbingServer(':53')
    udpserver.start()

    tcpserver = TcpJianbingServer(':53')
    tcpserver.serve_forever()

