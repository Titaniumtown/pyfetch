#!/bin/bash
rm -frv pyfetch pyfetch_cpp pyfetch.c


#C
cython3 -3 --embed -o pyfetch.c pyfetch.py

# clang -O3 -mfpu=native -mcpu=native -I/usr/include/python3.8 -o pyfetch pyfetch.c -lpython3.8 -lpthread -lpthread -lm -lutil -ldl

gcc -O3 -mtune=native -march=native -I/usr/include/python3.8 -o pyfetch pyfetch.c -lpython3.8 -lpthread