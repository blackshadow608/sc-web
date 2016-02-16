from client import *
from urllib2 import urlopen
import json
import sys


class Convert:
    tezt = SctpClient()
    servise_name = ''
    data = ''

    def get_or_create_sc_node(self, sc_type, sc_idtf, client_instace):
        sc_node = client_instace.find_element_by_system_identifier(sc_idtf)
        if not sc_node:
            sc_node = client_instace.create_node(sc_type)
            client_instace.set_system_identifier(sc_node, sc_idtf)
        return sc_node

    def create_multirelation(self, current_sc_addr, sc_addr, key, value):
        relation_element = self.tezt.create_node(
            ScElementType.sc_type_node | ScElementType.sc_type_node_norole | ScElementType.sc_type_const)
        self.tezt.set_system_identifier(relation_element, str(key) + '-' + self.servise_name + '*')
        for child_value in value:
            if isinstance(child_value, dict):
                self.create_graph_from_json(child_value, current_sc_addr)
            elif isinstance(child_value, list):
                self.create_multirelation(relation_element, current_sc_addr, key, child_value)
            else:
                value_node_sc_addr = self.tezt.create_node(ScElementType.sc_type_node | ScElementType.sc_type_const)
                self.tezt.set_system_identifier(value_node_sc_addr, str(child_value))
                value_arc_sc_addr = self.tezt.create_arc(
                    ScElementType.sc_type_const | ScElementType.sc_type_edge_common,
                    sc_addr,
                    value_node_sc_addr)
                self.tezt.create_arc(ScElementType.sc_type_arc_pos_const_perm,
                                     relation_element,
                                     value_arc_sc_addr)

    def create_graph_from_json(self, kwargs, sc_addr):
        for key, value in kwargs.iteritems():
            current_sc_addr = self.tezt.create_node(
                ScElementType.sc_type_node | ScElementType.sc_type_node_norole | ScElementType.sc_type_const)
            self.tezt.set_system_identifier(current_sc_addr, str(key) + '-' + self.servise_name + '*')

            if isinstance(value, dict):
                node_cur = self.tezt.create_node(ScElementType.sc_type_node | ScElementType.sc_type_const)
                value_arc_sc_addr = self.tezt.create_arc(
                    ScElementType.sc_type_const | ScElementType.sc_type_edge_common,
                    sc_addr,
                    node_cur)
                self.tezt.create_arc(ScElementType.sc_type_arc_pos_const_perm, current_sc_addr, value_arc_sc_addr)
                self.create_graph_from_json(value, node_cur)
            elif isinstance(value, list):
                node_cur = self.tezt.create_node(ScElementType.sc_type_node | ScElementType.sc_type_const)
                value_arc_sc_addr = self.tezt.create_arc(
                    ScElementType.sc_type_const | ScElementType.sc_type_edge_common,
                    sc_addr,
                    node_cur)
                self.tezt.create_arc(ScElementType.sc_type_arc_pos_const_perm, current_sc_addr, value_arc_sc_addr)
                self.create_multirelation(current_sc_addr, node_cur, key, value)
            else:
                if isinstance(value, unicode):
                    value = value.encode('utf-8')
                value_node_sc_addr = self.tezt.create_node(ScElementType.sc_type_node | ScElementType.sc_type_const)
                self.tezt.set_system_identifier(value_node_sc_addr, str(value))
                value_arc_sc_addr = self.tezt.create_arc(
                    ScElementType.sc_type_const | ScElementType.sc_type_edge_common,
                    sc_addr,
                    value_node_sc_addr)
                self.tezt.create_arc(ScElementType.sc_type_arc_pos_const_perm, current_sc_addr, value_arc_sc_addr)

    def c(self, service_name, data):
        print service_name
        service_name = str(service_name)
        self.servise_name = service_name
        self.data = data
        self.tezt.initialize('127.0.0.1', 55770)
        aseet = json.loads(data)
        print aseet
        user = self.get_or_create_sc_node(
            ScElementType.sc_type_node | ScElementType.sc_type_node_norole | ScElementType.sc_type_const, 'user',
            self.tezt)
        self.tezt.set_system_identifier(
            self.tezt.create_node(
                ScElementType.sc_type_node | ScElementType.sc_type_node_norole | ScElementType.sc_type_const),
            service_name + " profile*")

        node = self.tezt.create_node(ScElementType.sc_type_node | ScElementType.sc_type_const)
        self.tezt.set_system_identifier(node, service_name + " profile current user")

        root_sc_addr = user

        relation_node = self.tezt.find_element_by_system_identifier(service_name + " profile*")
        relation_edge = self.tezt.create_arc(ScElementType.sc_type_arc_pos_const_perm, relation_node,
                                             self.tezt.create_arc(
                                                 ScElementType.sc_type_const | ScElementType.sc_type_edge_common,
                                                 root_sc_addr, node))
        self.create_graph_from_json(aseet, node)

        self.tezt.shutdown()