
# parser_EggLex_parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'ADD AS ASS AXE BBQ BUILD CHICKEN COMMENT COMPARE DOT EQ FOX FR FUNCTION HATCH ID IFF IFT INT LBRACE LBRACK LPAREN PECK PICK PUSH RBRACE RBRACK ROOSTER RPAREN STR WHILEF WHILEThatch : HATCH FUNCTION'
    
_lr_action_items = {'HATCH':([0,],[2,]),'$end':([1,3,],[0,-1,]),'FUNCTION':([2,],[3,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'hatch':([0,],[1,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> hatch","S'",1,None,None,None),
  ('hatch -> HATCH FUNCTION','hatch',2,'p_HATCH','main.py',148),
]