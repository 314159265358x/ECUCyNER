
# installing

this application should be run in a separated isolation environment, due to the Flask framework vulnerability. For example, a user account without root access, a nobody user, or docker container.
In the first start, main.sh will automatically install most dependencies which are under pip. However, some package which is system package will not be installed automatically, run following command as root to install:

`apt install graphviz`
`apt install nvidia-cuda-toolkit`

In the first run, the application may crash and exit, which is the normal circumstances.
This caused by spacy does not download its data in a good way, which should be ignored. Just run it again, it will become normal.

# running

After setup in an isolated environment, the application will be ready to run.
It starts by opening the isolated environment, then using `screen` to create the window, then type `./main.sh` , the application will start its service.
