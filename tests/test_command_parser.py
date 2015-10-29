import unittest
from ui.cli.parser import *
from ui.cli.token import *


class TestParseNode(unittest.TestCase):
    def setUp(self):
        # Set up a parse tree for all test cases. It has the following commands:
        #
        # 1. show <INT:line_num>
        # 2. show <HEX:start_addr>
        # 3. show <HEX:start_addr> <HEX:stop_addr>
        # 4. save
        # 5. clear all info
        # 6. print <STR:mesasge>
        self.root = ParseNode(Token(Token.ROOT), 'root node')
        self.show_node = self.root.add(KeywordToken('show'), 'Show command')
        self.line_num_node = self.show_node.add(IntegerToken('line_num'), 'Line number')
        self.show_line_num_cmd = self.line_num_node.add(self.show_line_num_callback, 'Show a line number')

        self.start_addr_node = self.show_node.add(HexToken('start_addr'), 'Address')
        self.show_addr_cmd = self.start_addr_node.add(self.show_addr_callback, 'Show an address')

        self.stop_addr_node = self.start_addr_node.add(HexToken('stop_addr'), 'Stop address')
        self.show_start_stop_addr_cmd = self.stop_addr_node.add(self.show_start_stop_addr_callback,
                                                                'Show a range of addresses')
        self.save_node = self.root.add(KeywordToken('save'), 'Save command')
        self.save_cmd = self.save_node.add(self.save_callback, 'Save states')

        self.clear_node = self.root.add(KeywordToken('clear'), 'Clear command')
        self.all_node = self.clear_node.add(KeywordToken('all'), 'All')
        self.info_node = self.all_node.add(KeywordToken('info'), 'Info')
        self.clear_all_info_cmd = self.info_node.add(self.clear_all_info_callback, 'Clear all info')

        self.print_node = self.root.add(KeywordToken('print'), 'Print command')
        self.message_node = self.print_node.add(StringToken('message'), 'Message to be printed')
        self.print_cmd = self.message_node.add(self.print_callback, 'Print a message')

        self.callback = None
        self.call_params = None

    def show_line_num_callback(self, line_num):
        self.called = {'line_num': line_num}
        self.callback = 'show_line_num_callback'

    def show_addr_callback(self, addr):
        self.called = {'addr': addr}
        self.callback = 'show_addr_callback'

    def show_start_stop_addr_callback(self, start_addr, stop_addr):
        self.called = {'start_addr': start_addr, 'stop_addr': stop_addr}
        self.callback = 'show_start_stop_addr_callback'

    def save_callback(self):
        self.called = {}
        self.callback = 'save_callback'

    def clear_all_info_callback(self):
        self.called = {}
        self.callback = 'clear_all_info_callback'

    def print_callback(self, message):
        self.called = {'message': message}
        self.callback = 'print_callback'

    def test_parse_node(self):
        # Verify is_end_of_command()
        for node in (self.root, self.show_node, self.clear_node, self.save_node, self.print_node, self.line_num_node,
                     self.start_addr_node, self.stop_addr_node, self.message_node):
            self.assertFalse(node.is_end_of_command())
        for node in (self.show_line_num_cmd, self.show_addr_cmd, self.show_start_stop_addr_cmd,
                     self.clear_all_info_cmd, self.print_cmd):
            self.assertTrue(node.is_end_of_command())

        # At root node
        # 1. Match against an empty string. Should return 3 child nodes
        matches = self.root.match('')
        self.assertListEqual([self.show_node, self.save_node, self.clear_node, self.print_node], matches)

        # 2. Match against 's'. Should return 2 child nodes
        matches = self.root.match('s')
        self.assertListEqual([self.show_node, self.save_node], matches)

        # 3. Match against 'sh'. Should return show node only
        matches = self.root.match('sh')
        self.assertListEqual([self.show_node], matches)

        # 4. Match against 'sa'. Should return save node only
        matches = self.root.match('sa')
        self.assertListEqual([self.save_node], matches)

        # 5. Match against 'c'. Should return clear node only
        matches = self.root.match('c')
        self.assertListEqual([self.clear_node], matches)

        # At show node
        # 1. Match against ''. Should return all 2 child nodes
        matches = self.show_node.match('')
        self.assertListEqual([self.line_num_node, self.start_addr_node], matches)

        # 2. Match against '0'. Should return all 2 child node
        matches = self.show_node.match('0')
        self.assertListEqual([self.line_num_node, self.start_addr_node], matches)

        # 3. Match against '0x'. Should return 1 child node with hex token
        matches = self.show_node.match('0x')
        self.assertListEqual([self.start_addr_node], matches)

        # At start address node
        # 1. Match against ''. Should return 2 child nodes
        matches = self.start_addr_node.match('')
        self.assertListEqual([self.show_addr_cmd, self.stop_addr_node], matches)

        # 2. Match against '0'. Should return only stop address node
        matches = self.start_addr_node.match('0')
        self.assertListEqual([self.stop_addr_node], matches)

        # Verify has_child_string_token()
        self.assertFalse(self.show_node.has_string_child_token())
        self.assertTrue(self.print_node.has_string_child_token())

        # Verify find_executable_node()
        self.assertEqual(self.save_cmd, self.save_node.find_executable_node())
        self.assertEqual(self.clear_all_info_cmd, self.clear_node.find_executable_node())
        self.assertIsNone(self.show_node.find_executable_node())
        self.assertIsNone(self.print_node.find_executable_node())
