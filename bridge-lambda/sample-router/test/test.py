#!/usr/bin/env python

import sys, os, inspect
from lambda_local.main import call
from lambda_local.context import Context

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir+"/src")

import lambda_handler

def test():
    event = {
    }
    context = Context(5)
    call(lambda_handler.handler, event, context)


if __name__ == "__main__" :
    test()
