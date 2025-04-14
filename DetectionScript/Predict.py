import argparse
import numpy as np
import os
import torch
import torch.nn as nn
from torch.utils import data

from dataset.landslide_dataset import LandslideDataSet
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

def get_arguments():
    parser = argparse.ArgumentParser(description="Baseline method for Land4Seen")

    parser.add_argument("--data_dir", type=str, default='./',
                        help="dataset path.")
    parser.add_argument("--model_module", type=str, default='model.Networks',
                        help='model module to import')
    parser.add_argument("--model_name", type=str, default='unet',
                        help='model name in given module')
    parser.add_argument("--input_file", type=str, default='gornjatuzla.h5',
                        help="Path to input H5 file")
    parser.add_argument("--input_size", type=str, default='256,256',
                        help="width and height of input images.")
    parser.add_argument("--num_classes", type=int, default=2,
                        help="number of classes.")
    parser.add_argument("--num_workers", type=int, default=0,
                        help="number of workers for multithread dataloading.")
    parser.add_argument("--snapshot_dir", type=str, default='./test_map/',
                        help="where to save predicted maps.")
    parser.add_argument("--restore_from", type=str, default='DetectionScript/exp/batch2500_F1_7383.pth',
                        help="trained model.")


    return parser.parse_args()

def main():
    args = get_arguments()
    snapshot_dir = args.snapshot_dir
    if not os.path.exists(snapshot_dir):
        os.makedirs(snapshot_dir)

    w, h = map(int, args.input_size.split(','))
    input_size = (w, h)

    # Create network
    model = unet(n_classes=args.num_classes)

    saved_state_dict = torch.load(args.restore_from, map_location=torch.device('cpu'))
    model.load_state_dict(saved_state_dict)

    test_loader = data.DataLoader(
        SingleH5Dataset(args.input_file),
        batch_size=1, shuffle=False, num_workers=args.num_workers, pin_memory=True
    )

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
