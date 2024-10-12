#!/usr/bin/python3
r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this script used to detect tensorrt native library path
"""
import pkg_resources

installed_packages = pkg_resources.working_set
# print install path if installed
for i in installed_packages:
 if i.key == "tensorrt-libs":
  print(i.location)
  exit(0)

exit(1)
