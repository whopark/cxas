import os
if 'HOME' not in os.environ:
    os.environ['HOME'] = os.environ.get('USERPROFILE', '')
import torch
original_load = torch.load
def safe_load(*args, **kwargs):
    kwargs['weights_only'] = False
    kwargs['map_location'] = torch.device('cpu')
    return original_load(*args, **kwargs)
torch.load = safe_load

from cxas.segmentor import CXAS
try:
    print('\nTrying to initialize CXAS...')
    analyzer = CXAS()
    print('Initialized!')
    res = analyzer.process_file('images/RibFrac4frontal.png', do_store=True, output_directory='outputs', create=True, storage_type='png')
    print('Prediction keys:', res.keys())
    if 'segmentation_preds' in res:
        preds = res['segmentation_preds'][0]
        print('Masks shape:', preds.shape)
        print('Positive pixels:', preds.sum().item())
except Exception as e:
    import traceback
    traceback.print_exc()
