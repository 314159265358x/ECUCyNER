#!/bin/bash
# Copyright (C) haoyus@our.ecu.edu.au. All rights reserved.
# https://www.tensorflow.org/hub/tutorials/tf2_text_classification
# https://www.tensorflow.org/text/tutorials/classify_text_with_bert
# tensorflow is used to set up the environment
# apt install graphviz
# apt install nvidia-cuda-toolkit

# https://stackoverflow.com/questions/76028164/tensorflow-object-detection-tf-trt-warning-could-not-find-tensorrt
pip install -r requirements.txt
# detect the tensorrt lib path
path_tensorrt_lib=$(python3 ./scr/checkenv_tensorrt.py)

if [[ -z ${path_tensorrt_lib} ]]; then
pip install --no-cache-dir --extra-index-url https://pypi.nvidia.com tensorrt-libs
path_tensorrt_lib=$(python3 ./scr/checkenv_tensorrt.py)
fi # The first crash may be due to cuda graphics card driver is missing, so install it and try again

if [[ -z ${path_tensorrt_lib} ]]; then
echo "unable to detect TensorRT Lib path"
exit 1
fi

if [[ -z ${LD_LIBRARY_PATH} ]]; then
LD_LIBRARY_PATH=${path_tensorrt_lib}/tensorrt_libs
else
LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:${path_tensorrt_lib}/tensorrt_libs
fi
# This can effectively reduce GRAM consumption
# https://discuss.tensorflow.org/t/unable-to-get-tensorflow-working-correctly/18981
v1=$( PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:24 LD_LIBRARY_PATH=${LD_LIBRARY_PATH} python3 ./scr/checkenv.py )

if [[ "" == ${v1} ]]; then
echo "error install deps"
exit 1
fi

echo "checking tensorrt path:" ${path_tensorrt_lib}
echo "checking result:" ${v1}

echo "compiling"
python3 -m compileall -o 2 src

echo "running main.py"
# Actually launch the main application
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:24 LD_LIBRARY_PATH=${LD_LIBRARY_PATH} python3 src/main.py

exit $?
