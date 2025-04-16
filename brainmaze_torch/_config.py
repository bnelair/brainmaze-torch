# Copyright 2020-present, Mayo Clinic Department of Neurology
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.


import yaml
import os
import numpy as np


class ObjDict(dict):
    """
    Dictionary which you can access a) as a dict; b) as a struct with attributes. Can use both foo adding and deleting
    attributes resp items. Inherits from dict
    """

    def __init__(self, VT_={}):
        super().__init__(VT_)
        for key in VT_.keys():
            self.__setattr__(key, VT_[key])

    def __setitem__(self, key, value):
        if key in self:
            del self[key]

        super().__setitem__(key, value)
        if not key in self.__dir__():
            self.__setattr__(key, value)

    def __setattr__(self, key, value):
        if key in self.__dir__():
            self.__delattr__(key)

        super().__setattr__(key, value)
        if not key in self:
            self.__setitem__(key, value)

    def __delitem__(self, key):
        value = super().pop(key)
        try:
            super().pop(value, None)
        except: pass
        if key in dir(self):
            self.__delattr__(key)

    def __delattr__(self, key):
        super().__delattr__(key)
        if key in self:
            self.__delitem__(key)

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"

    def __missing__(self, key):
        self[key] = ObjDict()
        return self[key]

    def __getattr__(self, item):
        if not item in self.__dir__():
            self.__missing__(item)
        return super().__getattribute__(item)


def DictToObjDict(d):
    """
    Converts dictionary into object where, keys - converts keys into attributes
    """
    if isinstance(d, dict):
        #print(d.keys())
        top = ObjDict(d)

        #print(top.keys())
        for key in d.keys():
            if isinstance(d[key], dict):
                tmp = DictToObjDict(d[key])
                del top[key]
                top[key] = tmp

        return top
    else: return d


def config(path_config):
    with open(path_config, 'r') as stream:
        Cfg = yaml.safe_load(stream)
    return DictToObjDict(Cfg)


def ObjDictToDict(d):
    """
    Converts dictionary into object where, keys - converts keys into attributes
    """
    if isinstance(d, ObjDict):
        #print(d.keys())
        top = dict(d)

        #print(top.keys())
        for key in d.keys():
            if isinstance(d[key], ObjDict):
                tmp = ObjDictToDict(d[key])
                del top[key]
                top[key] = tmp

        return top
    else: return d


