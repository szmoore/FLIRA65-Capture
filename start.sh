#!/bin/bash

sudo bash -c "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$(pwd)/contrib/lib; contrib/bin/thttpd -C thttpd.conf"


