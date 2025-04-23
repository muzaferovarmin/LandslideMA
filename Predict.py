import numpy as np
import os
import torch
import torch.nn as nn
from torch.utils import data

import utils
from model.Networks import unet
import h5py


class SingleH5Dataset(data.Dataset):
    def __init__(self, h5_path):
        super().__init__()
        self.h5_path = h5_path
        with h5py.File(h5_path, 'r') as f:
            self.data = f['img'][:]  # Load entire dataset into memory

    def __len__(self):
        return 1  # Only single file

    def __getitem__(self, index):
        img = self.data.astype(np.float32)
        img = torch.from_numpy(img).permute(2, 0, 1)  # CHW format
        return img, os.path.basename(self.h5_path)


name_classes = ['Non-Landslide', 'Landslide']
epsilon = 1e-14

def importName(modulename, name):
    """ Import a named object from a module in the context of this function. """
    try:
        module = __import__(modulename, globals(), locals(), [name])
    except ImportError:
        return None
    return vars(module)[name]


    return parser.parse_args()
restore_from=utils.resource_path('exp/batch2500_F1_7383.pth')
def main(input_file,size, outputdir):
    snapshot_dir = outputdir
    if not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)
    # Create network
    model = unet(n_classes=2)

    saved_state_dict = torch.load(restore_from, map_location=torch.device('cpu'))
    model.load_state_dict(saved_state_dict)

    test_loader = data.DataLoader(
        SingleH5Dataset(input_file),
        batch_size=1, shuffle=False, num_workers=0, pin_memory=True
    )
    w, h = map(int, size.split(','))
    input_size = (w, h)
    interp = nn.Upsample(size=(input_size[1], input_size[0]), mode='bilinear')

    print('Testing..........')
    model.eval()

    for index, batch in enumerate(test_loader):
        image, name = batch  # Now gets name from H5 filename
        name = name[0].replace('.h5', '_mask')  # Clean filename

        with torch.no_grad():
            pred = model(image)

        _, pred = torch.max(interp(nn.functional.softmax(pred, dim=1)).detach(), 1)
        pred = pred.squeeze().data.numpy().astype('uint8')

        with h5py.File(os.path.join(snapshot_dir, f"{name}.h5"), 'w') as hf:
            hf.create_dataset('mask', data=pred)

if __name__ == '__main__':
    main()
