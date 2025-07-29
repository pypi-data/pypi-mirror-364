import argparse
import time
import pandas as pd
import imageio.v3 as iio
import os
import torch

from pathlib import Path
from pyroothair.cnn import nnUNetv2
from pyroothair.images import ImageLoader
from pyroothair.pipeline import CheckArgs, Pipeline

description = '''
Thank you for using pyRootHair!
-------------------------------

Run pyRootHair on a demonstration set of images that are pre-installed with pyRootHair. 

Please read the tutorial documentation on the github repository: https://github.com/iantsang779/pyRootHair

This is useful to run after a fresh pyRootHair installation to ensure everything works, and to check that you have successfully requested a GPU.

Basic usage: pyroothair_run_demo -o demo

Please cite the following paper when using pyRootHair: 

Tsang, I. et al. pyRootHair: Machine Learning Accelerated Software for High-Throughput Phenotyping of Plant Root Hair Traits. Preprint at https://doi.org/10.1101/2025.07.14.664697 (2025).

Author: Ian Tsang
Contact: ian.tsang@niab.com
''' 

def parse_args():
    parser = argparse.ArgumentParser(prog='pyRootHair Demo',
                                     description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    ### Required Arguments    
    parser.add_argument('-o','--output', help='Filepath to save data. Must be a different directory relative to the input image directory.', type=str, dest='save_path')

    ### Optional Arguments
    parser.add_argument('--resolution', help='Bin size defining measurement intervals along each root hair segment. Default = 20 px', type=int, nargs='?', dest='height_bin_size', default=20)
    parser.add_argument('--conv', help='The number of pixels corresponding to 1mm in the original input images. Default = 102 px', nargs='?', type=int, dest='conv', default=102)
    parser.add_argument('--frac', help='Degree of smoothing of lowess regression line to model average root hair length per input image. Value must be between 0 and 1. See statsmodels.nonparametric.smoothers_lowess.lowess for more details. Default = 0.1', type=float, nargs='?', dest='frac', default=0.1)
    parser.add_argument('--length-cutoff', help='Set maximum length (mm) of root (as distance from the root tip) to standardize measurements for all images in the input batch. Please only use this argument once you have run pyroothair once on the existing batch.', dest='length_cutoff', type=float, default=None)
    parser.add_argument('--plot-segmentation', help='toggle plotting of predicted binary masks for each image (straightened mask, root hair segments, and cropped root hair segments). Must provide a valid filepath for --output', dest='show_segmentation', action='store_true')
    parser.add_argument('--plot-transformation', help='toggle plotting of co-ordinates illustrating how each input image is warped and straightened. Useful for debugging any strangely warped masks. Must provide a valid filepath for --output', dest='show_transformation', action='store_true')
    parser.add_argument('--plot-summary', help='toggle plotting of summary plots describing RHL and RHD for each image. Must provide a valid filepath for --output', dest='show_summary', action='store_true')

    return parser.parse_args(), parser


def main():
    args, parser = parse_args()
    check_args = CheckArgs(args, parser)
    check_args.check_argument_demo()

    args.batch_id = 'demo'

    raw = pd.DataFrame() # initialize empty data frames to append to in run_pipeline()
    summary = pd.DataFrame()    
    start = time.perf_counter()

    demo_img_dir = os.path.join(Path(__file__).parent, 'demo_images')
    demo_imgs = sorted([i for i in os.listdir(demo_img_dir) if i.endswith('.png')])
    
    model = nnUNetv2(demo_img_dir, args.batch_id)
    model.check_gpu() # determine which model to load depending on GPU availability

    if not Path(args.save_path).exists(): # check if --output path exists, create it if not
        Path(args.save_path).mkdir(parents=True, exist_ok=True)
    model.download_model()
    
    device = torch.device('cuda', 0) if model.gpu_exists else torch.device('cpu')
    
    for img in demo_imgs: # loop through all input images, modify and save with nnUNet prefix
        im_loader = ImageLoader(demo_img_dir, img)
        im_loader.resize_channel()
        im_loader.setup_dir(args.save_path, args.batch_id)
        im_loader.save_resized_image()

    model.initialize_model(device)
    model.run_inference(args.save_path)
    mask_path = Path(args.save_path)/'masks'/ args.batch_id
    mask_files = sorted([i for i in os.listdir(mask_path) if i.endswith('.png')])

    failed_images = []

    for mask, img in zip(mask_files, demo_imgs): # loop through each predicted mask
        main = Pipeline(args, parser, demo_img_dir, img)
        init_mask = iio.imread(os.path.join(mask_path, mask))
        s, r = main.run_pipeline(init_mask, mask) # run pipeline for each image
        if len(s) > 0:
            summary = pd.concat([s,summary]) # add data from each image to the correct data frame
            raw = pd.concat([r,raw])
        else:  
            failed_images.append(mask)
    
    print(f'\n{summary}')
    print(f'\n{raw}')

    data_path = Path(args.save_path) / 'data' / args.batch_id
    data_path.mkdir(exist_ok=True, parents=True)

    summary.to_csv(os.path.join(data_path, f'{args.batch_id}_summary.csv'))
    raw.to_csv(os.path.join(data_path, f'{args.batch_id}_raw.csv'))
    
    if failed_images:
        print(f'\nAn error occurred with the following image(s) and were skipped: {failed_images}')

    print(f'\nTotal runtime for batch_id {args.batch_id}: {time.perf_counter()-start:.2f} seconds.')
     
if __name__ == '__main__':
    main()
