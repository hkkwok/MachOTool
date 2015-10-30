import sys
import string
from token import Token, ParameterToken, StringToken


class ParseNode(object):
    def __init__(self, token, desc=None):
        assert isinstance(token, Token) or token is None
        self.token = token
        self._children = list()
        self.desc = desc

    def match(self, s):
        """
        Return a list of children nodes that can match this
        """
        matches = list()
        for child in self._children:
            token = child.token
            if token is None:
                # This is a end-of-command node
                if s == '':
                    matches.append(child)
            elif token.accept(s):
                matches.append(child)
        return matches

    def add(self, token_or_command, desc=None):
        if isinstance(token_or_command, Token):
            for child in self._children:
                if child.token is not None and child.token == token_or_command:
                    return child  # this node already exists
            new_child = ParseNode(token_or_command, desc)
        else:
            assert callable(token_or_command)
            new_child = EndOfCommandNode(token_or_command, desc)
        self._children.append(new_child)
        return new_child

    def find_executable_node(self, s=''):
        if self.is_end_of_command():
            return self
        assert isinstance(self, ParseNode)
        nodes = self.find_complete_child_nodes(s)
        if len(nodes) != 1:
            return None
        if nodes[0].is_end_of_command():
            return nodes[0]
        return nodes[0].find_executable_node()

    def is_end_of_command(self):
        return isinstance(self, EndOfCommandNode)

    def has_string_child_token(self):
        for child in self._children:
            if isinstance(child.token, StringToken):
                return True
        return False

    def find_complete_child_nodes(self, s):
        complete_nodes = list()
        for child in self._children:
            if child.token is None:
                # end-of-command node
                if s == '':
                    complete_nodes.append(child)
                else:
                    continue
            else:
                if child.token.is_complete(s):
                    complete_nodes.append(child)
        return complete_nodes


class EndOfCommandNode(ParseNode):
    """
    An end-of-command node is a specialized ParseNode. It has no token but has a callable command.
    """
    def __init__(self, command, desc):
        super(EndOfCommandNode, self).__init__(None, desc)
        assert callable(command)
        self._command = command

    def match(self, s):
        return list()

    def add(self, token, desc=None):
        return False

    def execute(self, *params):
        self._command(*params)


class ParseStackLevel(object):
    def __init__(self, parse_node):
        self._node = parse_node
        self.string = ''

    def add_char(self, ch):
        assert len(ch) == 1
        if len(self._node.match(self.string + ch)) == 0:
            return False
        self.string += ch
        return True

    def del_char(self):
        if len(self.string) == 0:
            return False
        self.string = self.string[:-1]
        return True

    def is_parameter(self):
        return self._node.token.is_parameter()

    def match(self):
        return self._node.match(self.string)

    def value(self, s):
        token = self._node.token
        if token is None:
            return None
        return token.value(s)

    def complete(self):
        nodes = self._node.find_complete_child_nodes(self.string)
        if len(nodes) == 1:
            return True, nodes[0]
        else:
            return False, None

    def find_executable_node(self):
        return self._node.find_executable_node(self.string)


class ParseStack(object):
    def __init__(self):
        self._stack = list()

    def push(self, parse_node):
        self._stack.append(ParseStackLevel(parse_node))

    def pop(self):
        return self._stack.pop()

    def empty(self):
        return len(self._stack) == 0

    def add_char(self, ch):
        return self._stack[-1].add_char(ch)

    def del_char(self):
        if self._stack[-1].del_char():
            return True
        # Top-of-stack token has no character. Pop it off and try delete if the stack is not empty
        self._stack.pop()
        if self.empty():
            return False
        rc = self._stack[-1].del_char()
        assert rc
        return True

    def execute(self):
        # first, make sure that there is a single path to a end-of-command node.
        eoc_node = self._stack[-1].find_executable_node()
        if eoc_node is None:
            return False, 'incomplete command'
        assert eoc_node.is_end_of_command()

        # walk the stack to grab all parameters
        params = list()
        for idx in xrange(0, self.depth()-1):
            token_string = self._stack[idx].string
            level = self._stack[idx+1]
            if level.is_parameter():
                params.append(level.value(token_string))

        # Process the last level
        token_string = self._stack[-1].string
        is_complete, node = self._stack[-1].complete()
        assert is_complete  # otherwise (i.e. if incomplete), eoc_node would be None
        if node.token.is_parameter():
            params.append(node.token.value(token_string))

        # call the command callback
        eoc_node.execute(*params)
        return True, None

    def top_of_stack(self):
        return self._stack[-1]

    def depth(self):
        """
        Return the depth of the stack. Mainly for unit tests
        """
        return len(self._stack)


class CommandParser(object):
    STATE_CHAR = 'CHAR'
    STATE_SPACE = 'SPACE'
    STATE_QUOTE = 'QUOTE'
    STATE_ERROR = 'ERROR'

    def __init__(self, prompt):
        self._root = ParseNode(Token(Token.ROOT))
        self._stack = ParseStack()
        self._line = None
        self._state = None
        self._last_good = None
        self._quote_start = None
        self._reset_line()
        self.prompt = prompt
        self.outfile = sys.stdout

    def _display(self, s):
        self.outfile.write(s)
        self.outfile.flush()

    def _reset_line(self):
        self._line = ''
        self._state = self.STATE_CHAR
        self._last_good = 0
        self._quote_start = -1
        self._display(self.prompt)

    def add_command(self, command, callback, cmd_desc, token_desc):
        """
        Add a command to the parse tree.
        :param command: A command string.
        :param cmd_desc:  The description of the command.
        :param token_desc: A dictionary for description of each token.
        :return: None
        """
        tokens = [Token.from_string(x) for x in command.split()]
        cur_node = self._root
        for token in tokens:
            cur_node = cur_node.add(token)
        cur_node.add(callback, cmd_desc)

    def input(self, s):
        for ch in s:
            self._input_char(ch)

    def _last_char_index(self):
        return len(self._line) - 1

    def _in_state(self, state):
        assert state in (self.STATE_CHAR, self.STATE_SPACE, self.STATE_QUOTE, self.STATE_ERROR)
        return self._state == state

    def _in_error(self):
        return self._state == self.STATE_ERROR

    def _in_quote(self):
        return self._state == self.STATE_QUOTE

    def _display_error_pointer(self):
        line = ' ' * (len(self.prompt) + self._last_good + 1)
        self._display('\n' + line + '^\n')

    def _display_line(self):
        self._display(self.prompt + self._line)

    def _display_nodes(self, nodes):
        def format_node(node):
            if node.is_end_of_command():
                return '<LF>', node.desc
            else:
                return str(node.token), node.desc
        max_width = 0
        lines = list()
        for node in nodes:
            token_str, desc = format_node(node)
            token_width = len(token_str)
            if token_width > max_width:
                max_width = token_width
            lines.append((token_str, desc))
        fmt = '%-' + str(max_width) + 's %s'
        self._display('\n'.join(fmt % (x, y) for (x, y) in lines))
        self._display('\n')

    def _input_char(self, ch):
        assert len(ch) == 1
        if self._state == self.STATE_CHAR:
            self._state_char(ch)
        elif self._state == self.STATE_QUOTE:
            self._state_quote(ch)
        elif self._state == self.STATE_SPACE:
            self._state_space(ch)
        elif self._state == self.STATE_ERROR:
            self._state_error(ch)

    def _add_char(self, ch):
        self._line += ch
        self._display(ch)

    def _del_char(self):
        if len(self._line) == 0:
            return None
        ch = self._line[-1]
        self._line = self._line[:-1]
        self._display('/b')
        return ch

    @staticmethod
    def _either_or(cond, val_a, val_b):
        if cond:
            return val_a
        else:
            return val_b

    def _last_char(self):
        if len(self._line) == 0:
            return None
        return self._line[-1]

    def _state_from_last_char(self):
        last_ch = self._last_char()
        if last_ch == ' ':
            return self.STATE_SPACE
        elif last_ch == '"':
            return self.STATE_QUOTE
        else:
            return self.STATE_CHAR

    def _state_char(self, ch):
        self._add_char(ch)
        if ch == ' ':
            is_complete, next_node = self._stack.top_of_stack().complete()
            if is_complete:
                self._state = self.STATE_SPACE
                self._stack.push(next_node)
            else:
                self._state = self.STATE_ERROR
        elif ch == '"':
            # Only open a quote if there is a child string token
            self._state = self._either_or(self._stack.top_of_stack().has_string_child_token(),
                                          self.STATE_QUOTE, self.STATE_ERROR)
        elif ch == '\t':
            stack_top = self._stack.top_of_stack()
            matched_nodes = stack_top.match()
            if len(matched_nodes) > 1:
                # print the possible completions
                self._display_nodes(matched_nodes)
                self._display_line()
                return ''
            else:
                # return the string that needs to complete the command
                node = matched_nodes[0]
                if node.token.is_parameter():
                    if stack_top.complete():
                        self.input(' ')
                    else:
                        self._display_nodes([node])
                else:
                    token = node.token
                    assert token.is_keyword()
                    assert token.keyword.startswith(stack_top.string)
                    self.input(token.keyword[len(stack_top.string):])
        elif ch == '\n':
            succeeded, reason = self._stack.execute()
            if not succeeded:
                self._display('ERROR: %s\n' % reason)
        elif ch == '\b':
            self._del_char()
            self._state = self._state_from_last_char()
        else:
            self._state = self._either_or(self._stack.add_char(ch), self.STATE_CHAR, self.STATE_ERROR)

    def _state_quote(self, ch):
        if ch == '"':
            # End of the quoted string
            self._add_char(ch)
            self._last_good += 1
            self._state = self.STATE_CHAR
        elif ch == '\b':
            del_ch = self._del_char()
            if del_ch == '"':
                # Delete 1st quote mark of the quoted string
                self._state = self._state_from_last_char()
        elif ch == '\n':
            self._display('ERROR: quote is not closed\n')
            self._reset_line()
        else:
            if ch not in string.ascii_letters and ch not in string.digits and ch not in string.punctuation:
                return  # quoted strings have restricted character set.
            self._line += ch
            self._display(ch)
            succeeded = self._stack.add_char(ch)
            assert succeeded
            self._last_good += 1

    def _state_error(self, ch):
        if ch == '\b':
            self._del_char()
            if self._last_char_index() == self._last_good:
                self._state = self._state_from_last_char()
        elif ch == '\n':
            self._display_error_pointer()
            self._display('ERROR: parse error at character %d\n' % (self._last_good + 1))
            self._reset_line()
        else:
            self._add_char(ch)

    def _state_space(self, ch):
        if ch == ' ':
            self._add_char(ch)
            self._last_good += 1
        elif ch == '\b':
            self._del_char()
            self._state = self._state_from_last_char()
        elif ch == '\n':
            self._stack.execute()
        else:
            self._state = self._either_or(self._stack.add_char(ch), self.STATE_CHAR, self.STATE_ERROR)
