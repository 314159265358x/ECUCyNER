#!/usr/bin/python3
r"""
Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
this script is used to check the runtime environment of both pytorch and tensorflow
e.g. cuda availability, dependency integrity
"""

can_cuda:bool=True

try:
    import torch
except ImportError:
	exit(1)
	
if bool(torch.cuda.is_available()):
	pass
else:
	can_cuda=False
del torch


try:
    import tensorflow
except ImportError:
	exit(1)
	
if bool(tensorflow.config.list_physical_devices('GPU')):
	pass
else:
	can_cuda=False
del tensorflow

if can_cuda:
	print('cuda')
else:
	print('cpu')
