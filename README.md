# Simple Portable File Sharing Server

- Frontend side is made with svelte

- Backend side is written in python with no external modules

- Tested on Windows 10, Ubuntu 18.04, Android 10


## build
- run ```npm  i```
- put necessary icons in ```/ìcons```. see [icon list](/icons/README)
- run ```npm run extract```, ```src/iconlist.js``` should be created
- run ```npm run build```
- run ```npm run construct```
- ```server.py``` should be created on root dir and ready to run

## dev
- frontend : run ```npm run dev```
- backend : go to [template.py](/extras/template.py)

## notes
- Python3 has to be installed on the system
- Android user can use qpython, pydroid, or termux to run the ```server.py```