from copy import deepcopy
import re

def _equal(a, b):
    raise NotImplementedError()

def _parts(path):
    raise NotImplementedError()

def _key(parent, part, add=False):
    raise NotImplementedError()

def apply(document, operations):
    raise NotImplementedError()
