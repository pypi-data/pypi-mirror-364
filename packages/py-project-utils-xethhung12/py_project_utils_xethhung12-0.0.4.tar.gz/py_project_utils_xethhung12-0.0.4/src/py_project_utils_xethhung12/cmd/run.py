import sys
import shutil
import os
import importlib.resources as resources
import py_project_utils_xethhung12 as py_project
def main():
    py_project.create_project(sys.argv[1],sys.argv[2:])