# lextab.py. This file automatically created by PLY (version 3.11). Don't edit!
_tabversion   = '3.10'
_lextokens    = set(('ADD', 'ADDE', 'AS', 'AXE', 'BBQ', 'BUILD', 'CHICKEN', 'COMPARE', 'CONST', 'DIV', 'DOT', 'EQ', 'FLOAT', 'FOX', 'FR', 'HATCH', 'ID', 'IFF', 'IFT', 'INT', 'LBRACE', 'LBRACK', 'LOOPF', 'LOOPT', 'LPAREN', 'MUL', 'NEWLINE', 'PECK', 'PICK', 'POW', 'PUSH', 'RBRACE', 'RBRACK', 'REPF', 'REPT', 'ROOSTER', 'RPAREN', 'STR', 'SUB', 'TOP'))
_lexreflags   = 64
_lexliterals  = '()[]{}.=/+-*^'
_lexstateinfo = {'INITIAL': 'inclusive'}
_lexstatere   = {'INITIAL': [('(?P<t_ignore_COMMENT>(//[^\\n]*|/\\*(?:.|\\n)*?(?:\\*/|\\Z)|~~\\[==(?:.|\\n)*?(?:==\\]~~/|\\Z)))|(?P<t_NEWLINE>(?:\\r?\\n)+)|(?P<t_FLOAT>(?:\\d+\\.\\d*|\\d*\\.\\d+))|(?P<t_INT>\\b\\d+)|(?P<t_ID>\\b([A-Za-z_]\\w*)\\b)|(?P<t_STR>(?P<quote>["\\\'])(?P<str>(?:(?=(?P<slash>\\\\?))(?P=slash)[ -~])+?)(?P=quote))|(?P<t_ADD>\\+)|(?P<t_DOT>\\.)|(?P<t_LBRACK>\\[)|(?P<t_LPAREN>\\()|(?P<t_MUL>\\*)|(?P<t_POW>\\^)|(?P<t_RPAREN>\\))|(?P<t_DIV>/)|(?P<t_EQ>=)|(?P<t_LBRACE>{)|(?P<t_RBRACE>})|(?P<t_RBRACK>])|(?P<t_SUB>-)', [None, ('t_ignore_COMMENT', 'ignore_COMMENT'), None, ('t_NEWLINE', 'NEWLINE'), ('t_FLOAT', 'FLOAT'), ('t_INT', 'INT'), ('t_ID', 'ID'), None, (None, 'STR'), None, None, None, (None, 'ADD'), (None, 'DOT'), (None, 'LBRACK'), (None, 'LPAREN'), (None, 'MUL'), (None, 'POW'), (None, 'RPAREN'), (None, 'DIV'), (None, 'EQ'), (None, 'LBRACE'), (None, 'RBRACE'), (None, 'RBRACK'), (None, 'SUB')])]}
_lexstateignore = {'INITIAL': ' \t'}
_lexstateerrorf = {'INITIAL': 't_error'}
_lexstateeoff = {}
