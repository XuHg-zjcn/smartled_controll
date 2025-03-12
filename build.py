#!/usr/bin/python3
###############################################################################
# Copyright 2024 Xu Ruijun
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnishedto do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
from datetime import date
import re
from git import Repo
import pcbnew
import teardrops

def _prepare_infostr_var():
    str_date = date.strftime(date.today(), '%Y.%m.%d')
    print('date', str_date)

    repo = Repo('.')
    is_dirty = repo.is_dirty()
    if is_dirty:
        while True:
            x = input('git repo is dirty, continue?: (Y/n)')
            if x.capitalize() == 'Y' or x == '':
                break
            elif x.capitalize() == 'N':
                raise RuntimeError('git repo dirty, abort.')

    str_git = 'g' + repo.head.commit.hexsha[:7]
    if is_dirty:
        str_git += '-dirty'
    print('git', str_git)

    str_ver = None
    curr_tags = tuple(filter(lambda x:x.commit==repo.head.commit, repo.tags))
    for tag in curr_tags:
        m = re.match(r'(v\d+\.\d+).*', tag.name)
        if m:
            str_ver = m.group(1)
    print('ver', 'unknown' if str_ver is None else str_ver)
    return str_date, str_git, str_ver

def _replace_infostr(board, str_date, str_git, str_ver):
    for dr in board.Drawings():
        if hasattr(dr, 'GetText'):
            text = dr.GetText()
            text_old = text
            if 'yyyy.mm.dd' in text:
                text = text.replace('yyyy.mm.dd', str_date)
            if 'gxxxxxxx' in text:
                text = text.replace('gxxxxxxx', str_git)
            if 'vx.x' in text and str_ver is not None:
                text = text.replace('vx.x', str_ver)
            if text != text_old:
                print('replaced')
                print(text_old)
                print('-=-=-=-=-=-')
                print(text)
                print()
            dr.SetText(text)

def teardrop():
    # the teardrop plugin also refill zones
    teardrops.td.RmTeardrops()
    teardrops.td.SetTeardrops()

def infostr():
    board = pcbnew.GetBoard()
    _replace_infostr(board, *_prepare_infostr_var())

def all():
    infostr()
    teardrop()
    pcbnew.Refresh()
