import readline

# For filename_quoting_function
SINGLE_MATCH = 1
MULT_MATCH = 2


class Completer(object):

    @apply
    def word_break_characters():
        def get(self):
            return readline.get_completer_delims()
        def set(self, string):
            readline.set_completer_delims(string)
        return property(get, set)

    @apply
    def special_prefixes():
        def get(self):
            return readline.get_special_prefixes()
        def set(self, string):
            return readline.set_special_prefixes(string)
        return property(get, set)

    @apply
    def quote_characters():
        def get(self):
            return readline.get_completer_quote_characters()
        def set(self, string):
            return readline.set_completer_quote_characters(string)
        return property(get, set)

    @apply
    def filename_quote_characters():
        def get(self):
            return readline.get_filename_quote_characters()
        def set(self, string):
            return readline.set_filename_quote_characters(string)
        return property(get, set)

    @apply
    def completer():
        def get(self):
            return readline.get_completer()
        def set(self, function):
            readline.set_completer(function)
        return property(get, set)

    @apply
    def display_matches_hook():
        def get(self):
            raise AttributeError('Write-only property: display_matches_hook')
        def set(self, function):
            readline.set_completion_display_matches_hook(function)
        return property(get, set)

    @apply
    def char_is_quoted_function():
        def get(self):
            raise AttributeError('Write-only property: char_is_quoted_function')
        def set(self, function):
            readline.set_char_is_quoted_function(function)
        return property(get, set)

    @apply
    def filename_quoting_function():
        def get(self):
            raise AttributeError('Write-only property: filename_quoting_function')
        def set(self, function):
            readline.set_filename_quoting_function(function)
        return property(get, set)

    @apply
    def filename_dequoting_function():
        def get(self):
            raise AttributeError('Write-only property: filename_dequoting_function')
        def set(self, function):
            readline.set_filename_dequoting_function(function)
        return property(get, set)

completer = Completer()


class Completion(object):

    SINGLE_MATCH = SINGLE_MATCH
    MULT_MATCH = MULT_MATCH

    @property
    def type(self):
        return readline.get_completion_type()

    @property
    def begidx(self):
        return readline.get_begidx()

    @property
    def endidx(self):
        return readline.get_endidx()

    @property
    def found_quote(self):
        return readline.get_completion_found_quote()

    @property
    def quote_character(self):
        return readline.get_completion_quote_character()

    @apply
    def query_items():
        def get(self):
            readline.get_query_items()
        def set(self, value):
            readline.set_query_items(value)
        return property(get, set)

    @apply
    def append_character():
        def get(self):
            return readline.get_completion_append_character()
        def set(self, string):
            return readline.set_completion_append_character(string)
        return property(get, set)

    @apply
    def suppress_append():
        def get(self):
            raise AttributeError('Write-only property: suppress_append')
        def set(self, suppress):
            readline.set_completion_suppress_append(suppress)
        return property(get, set)

    @apply
    def suppress_quote():
        def get(self):
            raise AttributeError('Write-only property: suppress_quote')
        def set(self, suppress):
            readline.set_completion_suppress_quote(suppress)
        return property(get, set)

    @apply
    def filename_completion_desired():
        def get(self):
            raise AttributeError('Write-only property: filename_completion_desired')
        def set(self, value):
            readline.set_filename_completion_desired(value)
        return property(get, set)

    @apply
    def filename_quoting_desired():
        def get(self):
            raise AttributeError('Write-only property: filename_quoting_desired')
        def set(self, value):
            readline.set_filename_quoting_desired(value)
        return property(get, set)

    @apply
    def attempted_completion_over():
        def get(self):
            raise AttributeError('Write-only property: attempted_completion_over')
        def set(self, value):
            readline.set_attempted_completion_over(value)
        return property(get, set)

    # Stock completers
    def filename_completion_function(self, text, state):
        return readline.filename_completion_function(text, state)

    def username_completion_function(self, text, state):
        return readline.username_completion_function(text, state)

completion = Completion()

