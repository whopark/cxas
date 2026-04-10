import sys
try:
    import cxas
    print('cxas module loaded')
    print('dir:', dir(cxas))
    print('doc:', cxas.__doc__)
    for attr_name in dir(cxas):
        attr = getattr(cxas, attr_name)
        if callable(attr) and not attr_name.startswith('_'):
            print(f'Callable: cxas.{attr_name}')
except Exception as e:
    import traceback
    traceback.print_exc()

# dir: ['CXAS', '__builtins__', '__cached__', '__doc__', '__file__', '__loader__', '__name__', '__package__', '__path__', '__spec__', 'extraction', 'file_io', 'helper', 'io_utils', 'label_mapper', 'models', 'segmentor']
doc: None