# -*- coding: utf-8 -*-
"""
-----------------------------------------------------------------------------
This source file is part of OSTIS (Open Semantic Technology for Intelligent Systems)
For the latest info, see http://www.ostis.net

Copyright (c) 2012 OSTIS

OSTIS is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OSTIS is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with OSTIS. If not, see <http://www.gnu.org/licenses/>.
-----------------------------------------------------------------------------
"""

import socket
import struct
import time
import thread, threading
import struct




__all__ = (
    'SctpCommandType',
    'SctpResultCode',
    'SctpIteratorType',
    'ScElementType',
    'ScAddr',
    'ScStatItem',
    'SctpClient',
)


class SctpCommandType:
    SCTP_CMD_UNKNOWN            = 0x00 # unkown command
    SCTP_CMD_CHECK_ELEMENT      = 0x01 # check if specified sc-element exist
    SCTP_CMD_GET_ELEMENT_TYPE   = 0x02 # return sc-element type
    SCTP_CMD_ERASE_ELEMENT      = 0x03 # erase specified sc-element
    SCTP_CMD_CREATE_NODE        = 0x04 # create new sc-node
    SCTP_CMD_CREATE_LINK        = 0x05 # create new sc-link
    SCTP_CMD_CREATE_ARC         = 0x06 # create new sc-arc
    SCTP_CMD_GET_ARC            = 0x07 # return begin and end element of sc-arc

    SCTP_CMD_GET_LINK_CONTENT   = 0x09 # return content of sc-link
    SCTP_CMD_FIND_LINKS         = 0x0a # return sc-links with specified content
    SCTP_CMD_SET_LINK_CONTENT   = 0x0b # setup new content for the link

    SCTP_CMD_ITERATE_ELEMENTS   = 0x0c # return base template iteration result
    SCTP_CMD_ITERATE_CONSTRUCTION = 0x0d # return advanced template iteration results

    SCTP_CMD_EVENT_CREATE       = 0x0e # create subscription to specified event
    SCTP_CMD_EVENT_DESTROY      = 0x0f # destroys specified event subscription
    SCTP_CMD_EVENT_EMIT         = 0x10 # emits specified event to client


    SCTP_CMD_FIND_ELEMENT_BY_SYSITDF = 0xa0 # return sc-element by it system identifier
    SCTP_CMD_SET_SYSIDTF        = 0xa1   # setup new system identifier for sc-element
    SCTP_CMD_STATISTICS         = 0xa2 # return usage statistics from server


class SctpResultCode:
    SCTP_RESULT_OK              = 0x00 #
    SCTP_RESULT_FAIL            = 0x01 #
    SCTP_RESULT_ERROR_NO_ELEMENT= 0x02 # sc-element wasn't founded
    SCTP_RESULT_NORIGHTS        = 0x03


class SctpIteratorType:
    SCTP_ITERATOR_3F_A_A = 0
    SCTP_ITERATOR_3A_A_F = 1
    SCTP_ITERATOR_3F_A_F = 2
    SCTP_ITERATOR_5F_A_A_A_F = 3
    SCTP_ITERATOR_5_A_A_F_A_F = 4
    SCTP_ITERATOR_5_F_A_F_A_F = 5
    SCTP_ITERATOR_5_F_A_F_A_A = 6
    SCTP_ITERATOR_5_F_A_A_A_A = 7
    SCTP_ITERATOR_5_A_A_F_A_A = 8


class ScElementType:
    # sc-element types
    sc_type_node        =   0x1
    sc_type_link        =   0x2
    sc_type_edge_common =   0x4
    sc_type_arc_common  =   0x8
    sc_type_arc_access  =   0x10

    # sc-element constant
    sc_type_const       =   0x20
    sc_type_var         =   0x40

    # sc-element positivity
    sc_type_arc_pos     =   0x80
    sc_type_arc_neg     =   0x100
    sc_type_arc_fuz     =   0x200

    # sc-element premanently
    sc_type_arc_temp    =   0x400
    sc_type_arc_perm    =   0x800

    # struct node types
    sc_type_node_tuple  =   (0x80)
    sc_type_node_struct =   (0x100)
    sc_type_node_role   =   (0x200)
    sc_type_node_norole =   (0x400)
    sc_type_node_class  =   (0x800)
    sc_type_node_abstract   =   (0x1000)
    sc_type_node_material   =   (0x2000)

    sc_type_arc_pos_const_perm  =   (sc_type_arc_access | sc_type_const | sc_type_arc_pos | sc_type_arc_perm)

    # type mask
    sc_type_element_mask    =   (sc_type_node | sc_type_link | sc_type_edge_common | sc_type_arc_common | sc_type_arc_access)
    sc_type_constancy_mask  =   (sc_type_const | sc_type_var)
    sc_type_positivity_mask =   (sc_type_arc_pos | sc_type_arc_neg | sc_type_arc_fuz)
    sc_type_permanency_mask =   (sc_type_arc_perm | sc_type_arc_temp)
    sc_type_node_struct_mask=   (sc_type_node_tuple | sc_type_node_struct | sc_type_node_role | sc_type_node_norole | sc_type_node_class | sc_type_node_abstract | sc_type_node_material)
    sc_type_arc_mask        =   (sc_type_arc_access | sc_type_arc_common | sc_type_edge_common)

class ScEventType:

    SC_EVENT_ADD_OUTPUT_ARC = 0
    SC_EVENT_ADD_INPUT_ARC = 1
    SC_EVENT_REMOVE_OUTPUT_ARC = 2
    SC_EVENT_REMOVE_INPUT_ARC = 3
    SC_EVENT_REMOVE_ELEMENT = 4


class ScAddr:
    def __init__(self, _seg, _offset):
        self.seg = _seg
        self.offset = _offset

    def __str__(self):
        return 'sc-addr: %d, %d' % (self.seg, self.offset)

    def __eq__(self, other):
        return self.seg == other.seg and self.offset == other.offset

    def to_id(self):
        return "%d" % (self.seg | (self.offset << 16))

    @staticmethod
    def parse_from_string(addr_str):
        """Parse sc-addr from string 'seg_offset'
        @return: Return parsed sc-addr
        """
        try:
            a = int(addr_str)
            addr = ScAddr(a & 0xffff, a >> 16)
        except:
            return None

        return addr

    @staticmethod
    def parse_binary(data):

        try:
            seg, offset = struct.unpack('=HH', data)
            return ScAddr (seg, offset)
        except:
            return None


class ScStatItem:

    def __init__(self):
        self.time = None # unix time
        self.nodeCount = 0 # amount of all nodes
        self.arcCount = 0 # amount of all arcs
        self.linksCount = 0 # amount of all links
        self.liveNodeCount = 0 # amount of live nodes
        self.liveArcCount = 0 # amount of live arcs
        self.liveLinkCount = 0# amount of live links
        self.emptyCount = 0 # amount of empty sc-elements
        self.connectionsCount = 0 # amount of collected clients
        self.commandsCount = 0 # amount of processed commands (it includes commands with errors)
        self.commandErrorsCount = 0 # amount of command, that was processed with error
        self.isInitStat = False   # flag on initial stat save

    def toList(self):
        return [self.time,
                self.nodeCount,
                self.arcCount,
                self.linksCount,
                self.liveNodeCount,
                self.liveArcCount,
                self.liveLinkCount,
                self.emptyCount,
                self.connectionsCount,
                self.commandsCount,
                self.commandErrorsCount,
                self.isInitStat
                ]


class EventStruct:
    
    def __init__(self, event_id, event_type, addr, callback):
        self.event_id = event_id
        self.addr = addr
        self._event_type = event_type
        self.callback = callback
    
    
class SctpClient:
    
    def __init__(self):
        self.sock = None
        self.events = {}
                
    def __del__(self):
        self.shutdown()    
                
    def receiveData(self, dataSize):
        res = ''
        while (len(res) < dataSize):
            data = self.sock.recv(dataSize - len(res))
            res += data
            time.sleep(0.001)
        assert len(res) == dataSize

        return res 

    def initialize(self, host, port):
        """Initialize network session with server
        @param host: Name of server host (str)
        @param port: connection listening port (int)
        """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((host, port))
        except Exception, e:
            print "can't connect to %s:%d. Exception type is %s" % (host, port, `e`)

    def shutdown(self):
        """Close network session
        """
        for event_id in self.events.keys():
            self.event_destroy(event_id)
        self.events = {}
            
    def erase_element(self, el_addr):
        """Erase element with specified sc-addr
        @param el_addr sc-addr of sc-element to remove
        @return If sc-element erased, then return True; otherwise return False
        """
        # send request
        params = struct.pack('=HH', el_addr.seg, el_addr.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_ERASE_ELEMENT, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)

        return resCode == SctpResultCode.SCTP_RESULT_OK

    def get_link_content(self, link_addr):
        """Get content of sc-link with specified sc-addr
        @param link_addr: sc-addr of sc-link to get content
        @return: If data was returned without any errors, then return it;
        otherwise return None
        """

        # send request
        params = struct.pack('=HH', link_addr.seg, link_addr.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_GET_LINK_CONTENT, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)

        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        content_data = None
        if resSize > 0:
            content_data = self.receiveData(resSize)

        return content_data

    def check_element(self, el_addr):
        """Check if sc-element with specified sc-addr exist
        @param el_addr: sc-addr of element to check
        @return: If specified sc-element exist, then return True; otherwise return False
        """

        # send request
        params = struct.pack('=HH', el_addr.seg, el_addr.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_CHECK_ELEMENT, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)

        return resCode == SctpResultCode.SCTP_RESULT_OK

    def get_element_type(self, el_addr):
        """Returns type of specified sc-element
        @param el_addr: sc-addr of element to get type
        @return: If type got without any errors, then return it; otherwise return None
        """

        # send request
        params = struct.pack('=HH', el_addr.seg, el_addr.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_GET_ELEMENT_TYPE, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        data = self.receiveData(2)
        elType = struct.unpack("=H", data)[0]

        return elType
    
    def get_arc(self, arc):
        """Returns sc-addr of arc element begin
        @param arc sc-addr of arc to get beign
        @return If there are no any errors, then returns sc-addr of arc begin; 
        otherwise returns None
        """
        # send request
        params = struct.pack('=HH', arc.seg, arc.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_GET_ARC, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        addr = ScAddr(0, 0)
        data = self.receiveData(4)
        addr.seg, addr.offset = struct.unpack('=HH', data)
        
        addr2 = ScAddr(0, 0)
        data = self.receiveData(4)
        addr2.seg, addr2.offset = struct.unpack('=HH', data)

        return (addr, addr2)
    
    def create_node(self, el_type):
        """Create new sc-node in memory with specified type
        @param el_type: Type of node that would be created
        @return: If sc-node was created, then returns it sc-addr; otherwise return None
        """

        # send request
        params = struct.pack('=H', el_type)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_CREATE_NODE, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        addr = ScAddr(0, 0)
        data = self.receiveData(4)
        addr.seg, addr.offset = struct.unpack('=HH', data)

        return addr

    def create_link(self):
        """Create new sc-link in memory
        @return: If sc-link was created, then returns it sc-addr; otherwise return None
        """
        # send request
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_CREATE_LINK, 0, 0, 0)
        alldata = data

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        addr = ScAddr(0, 0)
        data = self.receiveData(4)
        addr.seg, addr.offset = struct.unpack('=HH', data)

        return addr

    def create_arc(self, arc_type, begin_addr, end_addr):
        """Create new arc in sc-memory with specified type and begin, end elements
        @param arc_type: Type of sc-arc
        @param begin_addr: sc-addr of begin arc element
        @param end_addr: sc-addr of end arc element
        @return: If sc-arc was created, then returns it sc-addr; otherwise return None
        """
        # send request
        params = struct.pack('=HHHHH', arc_type, begin_addr.seg, begin_addr.offset, end_addr.seg, end_addr.offset)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_CREATE_ARC, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK:
            return None

        addr = ScAddr(0, 0)
        data = self.receiveData(4)
        addr.seg, addr.offset = struct.unpack('=HH', data)

        return addr

    def find_links_with_content(self, data):
        """Find sc-links with specified content
        @param data: Content data for search
        @return: Returns list of sc-addrs of founded sc-links. If there are any error, then return None
        """
        # send request
        params = struct.pack('=I%ds' % len(data), len(data), data)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_FIND_LINKS, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK or resSize < 4:
            return None

        res = []
        data = self.receiveData(resSize)
        resCount = struct.unpack('=I', data[:4])[0]
        for i in xrange(resCount):
            addr = ScAddr(0, 0)
            data = data[4:]
            addr.seg, addr.offset = struct.unpack('=HH', data)
            res.append(addr)

        return res
    
    def set_link_content(self, addr, data):
        """Find sc-links with specified content
        @param addr: sc-addr of sc-link
        @param data: Content data 
        @return: If link content changed, then return True; otherwise return False
        """
        # send request
        params = struct.pack('=HHI%ds' % len(data), addr.seg, addr.offset, len(data), data)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_SET_LINK_CONTENT, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode == SctpResultCode.SCTP_RESULT_OK:
            return True

        return False

    def iterate_elements(self, iterator_type, *args):
        """Iterate element by specified template and return results
        """
        params = None
        params_count = None
        if iterator_type == SctpIteratorType.SCTP_ITERATOR_3A_A_F:
            params_count = 3
            params = struct.pack('=BHHHH', iterator_type, args[0], args[1], args[2].seg, args[2].offset)
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_3F_A_A:
            params_count = 3
            params = struct.pack('=BHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2])
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_3F_A_F:
            params_count = 3
            params = struct.pack('=BHHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2].seg, args[2].offset)
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5_A_A_F_A_A:
            params_count = 5
            params = struct.pack('=BHHHHHH', iterator_type, args[0], args[1], args[2].seg, args[2].offset, args[3], args[4])
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5_A_A_F_A_F:
            params_count = 5
            params = struct.pack('=BHHHHHHH', iterator_type, args[0], args[1], args[2].seg, args[2].offset, args[3], args[4].seg, args[4].offset)
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5_F_A_A_A_A:
            params_count = 5
            params = struct.pack('=BHHHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2], args[3], args[4])
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5_F_A_F_A_A:
            params_count = 5
            params = struct.pack('=BHHHHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2].seg, args[2].offset, args[3], args[4])
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5_F_A_F_A_F:
            params_count = 5
            params = struct.pack('=BHHHHHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2].seg, args[2].offset, args[3], args[4].seg, args[4].offset)
        elif iterator_type == SctpIteratorType.SCTP_ITERATOR_5F_A_A_A_F:
            params_count = 5
            params = struct.pack('=BHHHHHHH', iterator_type, args[0].seg, args[0].offset, args[1], args[2], args[3], args[4].seg, args[4].offset)

        params_len = len(params)
        # send request
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_ITERATE_ELEMENTS, 0, 0, params_len)
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK or resSize == 0:
            return None

        res_count_data = self.receiveData(4)
        res_count = struct.unpack('=I', res_count_data)[0]

        if res_count == 0:
            return None

        results = []
        for idx in xrange(res_count):
            result_item = []
            for j in xrange(params_count):
                addr_data = self.receiveData(4)
                addr = ScAddr(0, 0)
                addr.seg, addr.offset = struct.unpack('=HH', addr_data)
                result_item.append(addr)

            results.append(result_item)


        return results

    def find_element_by_system_identifier(self, idtf_data):
        """Find sc-element by it system identifier
        @param idtf_data: Identifier data for search
        @return: Returns sc-addrs of founded sc-element.
        If there are any error or sc-element wasn't found, then return None
        """
        # send request
        params = struct.pack('=I%ds' % len(idtf_data), len(idtf_data), idtf_data)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_FIND_ELEMENT_BY_SYSITDF, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK or resSize < 4:
            return None

        addr = ScAddr(0, 0)
        data = self.receiveData(4)
        addr.seg, addr.offset = struct.unpack('=HH', data)

        return addr
    
    def set_system_identifier(self, addr, idtf_data):
        """Set new system identifier for sc-element
        @param idtf_data: Identifier data 
        @return: If identifier changed, then return True; otherwise return False
        """
        # send request
        params = struct.pack('=HHI%ds' % len(idtf_data), addr.seg, addr.offset, len(idtf_data), idtf_data)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_SET_SYSIDTF, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        return resCode == SctpResultCode.SCTP_RESULT_OK
        
    def get_statistics(self, beg_time, end_time):
        """Returns statistics from sctp server, for a specified time range.
        (http://docs.python.org/2/library/time.html)
        @param beg_time: Time structure, that contains range begin
        @param end_time: Time structure, that contains range end
        @return: Returns sorted list of statistics info
        """
        # send request
        params = struct.pack('=QQ', beg_time * 1000, end_time * 1000)
        data = struct.pack('=BBII', SctpCommandType.SCTP_CMD_STATISTICS, 0, 0, len(params))
        alldata = data + params

        self.sock.send(alldata)

        # receive response
        data = self.receiveData(10)
        cmdCode, cmdId, resCode, resSize = struct.unpack('=BIBI', data)
        if resCode != SctpResultCode.SCTP_RESULT_OK or resSize < 4:
            return None

        # read number of stat items
        data = self.receiveData(4)
        items_count = struct.unpack('=I', data)[0]

        # read items
        result = []
        item_struct = '=QQQQQQQQQQQB'
        item_struct_size = struct.calcsize(item_struct)
        for idx in xrange(items_count):
            data = self.receiveData(item_struct_size)

            item = ScStatItem()

            item_tuple = struct.unpack(item_struct, data)

            item.time = item_tuple[0]
            item.nodeCount = item_tuple[1]
            item.arcCount = item_tuple[2]
            item.linksCount = item_tuple[3]
            item.liveNodeCount = item_tuple[4]
            item.liveArcCount = item_tuple[5]
            item.liveLinkCount = item_tuple[6]
            item.emptyCount = item_tuple[7]
            item.connectionsCount = item_tuple[8]
            item.commandsCount = item_tuple[9]
            item.commandErrorsCount = item_tuple[10]
            item.isInitStat = (item_tuple[11] != 0)

            result.append(item)

        return result
