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

        self.callback_func = None
        self.callback_params = None

    def show_line_num_callback(self, line_num):
        self.callback_func = 'show_line_num_callback'
        self.callback_params = {'line_num': line_num}

    def show_addr_callback(self, addr):
        self.callback_func = 'show_addr_callback'
        self.callback_params = {'addr': addr}

    def show_start_stop_addr_callback(self, start_addr, stop_addr):
        self.callback_func = 'show_start_stop_addr_callback'
        self.callback_params = {'start_addr': start_addr, 'stop_addr': stop_addr}

    def save_callback(self):
        self.callback_func = 'save_callback'
        self.callback_params = {}

    def clear_all_info_callback(self):
        self.callback_func = 'clear_all_info_callback'
        self.callback_params = {}

    def print_callback(self, message):
        self.callback_func = 'print_callback'
        self.callback_params = {'message': message}

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

    def _check_complete(self, stack, expected_is_complete, expected_next_node=None):
        is_complete, next_node = stack.top_of_stack().complete()
        self.assertEqual(expected_is_complete, is_complete)
        self.assertEqual(expected_next_node, next_node)
        return next_node

    def _check_execute(self, stack, expected_succeeded, expected_reason=None, expected_func=None, expected_params=None):
        self.callback_func = None
        self.callback_params = None
        succeeded, reason = stack.execute()
        self.assertEqual(expected_succeeded, succeeded)
        self.assertEqual(expected_reason, reason)
        if expected_succeeded:
            self.assertEqual(expected_func, self.callback_func)
            self.assertDictEqual(expected_params, self.callback_params)
        else:
            self.assertIsNone(self.callback_func)
            self.assertIsNone(self.callback_params)

    def test_parse_stack(self):
        stack = ParseStack()

        # Issue 'sh 0x1'
        stack.push(self.root)
        self.assertTrue(stack.add_char('s'))
        self._check_complete(stack, False)

        self.assertTrue(stack.add_char('h'))
        next_node = self._check_complete(stack, True, self.show_node)

        stack.push(next_node)
        self.assertTrue(stack.add_char('0'))
        self._check_complete(stack, True, self.line_num_node)
        self._check_execute(stack, True, None, 'show_line_num_callback', {'line_num': 0})

        self.assertTrue(stack.add_char('x'))
        self._check_complete(stack, False)
        self._check_execute(stack, False, 'incomplete command')

        self.assertTrue(stack.add_char('1'))
        next_node = self._check_complete(stack, True, self.start_addr_node)
        self._check_execute(stack, True, None, 'show_addr_callback', {'addr': 0x1})

        # Issue 'sh 0x1 0x2'
        stack.push(next_node)
        self.assertTrue(stack.add_char('0'))
        self._check_complete(stack, False)

        self.assertTrue(stack.add_char('x'))
        self._check_complete(stack, False)
        self._check_execute(stack, False, 'incomplete command')

        self.assertTrue(stack.add_char('2'))
        self._check_complete(stack, True, self.stop_addr_node)
        self._check_execute(stack, True, None, 'show_start_stop_addr_callback', {'start_addr': 0x1, 'stop_addr': 0x2})


class TestCommandParser(unittest.TestCase):
    def show_line_num_callback(self, line_num):
        self.callback_func = 'show_line_num_callback'
        self.callback_params = {'line_num': line_num}

    def show_addr_callback(self, addr):
        self.callback_func = 'show_addr_callback'
        self.callback_params = {'addr': addr}

    def show_start_stop_addr_callback(self, start_addr, stop_addr):
        self.callback_func = 'show_start_stop_addr_callback'
        self.callback_params = {'start_addr': start_addr, 'stop_addr': stop_addr}

    def save_callback(self):
        self.callback_func = 'save_callback'
        self.callback_params = {}

    def clear_all_info_callback(self):
        self.callback_func = 'clear_all_info_callback'
        self.callback_params = {}

    def print_callback(self, message):
        self.callback_func = 'print_callback'
        self.callback_params = {'message': message}

    def setUp(self):
        self.parser = CommandParser('>> ')
        self.callback_func = None
        self.callback_params = None
        self.parser.add_command('show <INT:line_num>', self.show_line_num_callback, 'Show line number', {})
        self.parser.add_command('show <HEX:start_addr>', self.show_addr_callback, 'Show an address', {})
        self.parser.add_command('show <HEX:start_addr> <HEX:stop_addr>', self.show_start_stop_addr_callback,
                                'Show a range of addresses', {})
        self.parser.add_command('save', self.save_callback, 'Save states', {})
        self.parser.add_command('clear all info', self.clear_all_info_callback, 'Clear all info', {})
        self.parser.add_command('print <STR:message>', self.print_callback, 'Print a message', {})

    def _reset_callback_states(self):
        self.callback_func = None
        self.callback_params = None

    def _check_callback(self, func, params):
        self.assertEqual(func, self.callback_func)
        self.assertDictEqual(params, self.callback_params)

    def test_basic_command(self):
        self._reset_callback_states()
        self.parser.input('show 0\n')
        self._check_callback('show_line_num_callback', {'line_num': 0})

        self._reset_callback_states()
        self.parser.input('show 0x1\n')
        self._check_callback('show_addr_callback', {'addr': 0x1})

        self._reset_callback_states()
        self.parser.input('show 0x1 0x2\n')
        self._check_callback('show_start_stop_addr_callback', {'start_addr': 0x1, 'stop_addr': 0x2})
