import argparse
from .resample import resample
from .registration import register
from .nii2mp4 import nii_to_mp4
from .round import round_nifti
from .denoise_mp2rage import robust_combination
from .crop import crop
from .clean_background import remove_background_nifti

def resample_cli():
    parser = argparse.ArgumentParser(description='Resample NIfTI image to specified resolution')
    parser.add_argument('-i', '--input', required=True,
                      help='Path to input NIfTI file')
    parser.add_argument('-o', '--output', required=True,
                      help='Path to save resampled NIfTI file')
    parser.add_argument('-s', '--spacing', nargs=3, type=float, default=[1.0, 1.0, 1.0],
                      help='Target voxel spacing in mm (x y z), default: 1.0 1.0 1.0')
    parser.add_argument('--interpolation', choices=['linear', 'nearest', 'bspline'], 
                      default='linear',
                      help='Interpolation method (default: linear)')
    
    args = parser.parse_args()
    
    resample(
        input_path=args.input,
        output_path=args.output,
        target_spacing=tuple(args.spacing),
        interpolation=args.interpolation
    )

def crop_cli():
    parser = argparse.ArgumentParser(description='Crop Or Pad NIfTI image to specified shape')
    parser.add_argument('-i', '--input', required=True,
                      help='Path to input NIfTI file')
    parser.add_argument('-o', '--output', required=True,
                      help='Path to save resampled NIfTI file')
    parser.add_argument('-s', '--shape', nargs=3, type=float, default=[256, 256, 256],
                      help='Target image shape, default: 256 256 256')
    
    args = parser.parse_args()
    
    crop(
        input_path=args.input,
        output_path=args.output,
        target_shape=tuple(args.shape),
    )

def register_cli():
    parser = argparse.ArgumentParser(description='Register moving image to fixed image')
    parser.add_argument('-f', '--fixed', required=True,
                      help='Path to fixed/reference NIfTI file')
    parser.add_argument('-m', '--moving', required=True,
                      help='Path to moving NIfTI file')
    parser.add_argument('-o', '--output', required=True,
                      help='Path to save registered NIfTI file')
    parser.add_argument('-t', '--type', choices=['rigid', 'affine', 'syn'], 
                      default='syn',
                      help='Registration type (default: syn)')
    parser.add_argument('--interpolation', default='linear',
                      help='Interpolation type (default: linear)')
    
    args = parser.parse_args()
    
    register(
        fixed_path=args.fixed,
        moving_path=args.moving,
        output_path=args.output,
        reg_type=args.type,
        interpolation=args.interpolation
    ) 

def nii_to_mp4_cli():
    parser = argparse.ArgumentParser(description='Convert NIfTI file to MP4 video')
    parser.add_argument('-i', '--input', required=True,
                      help='Path to input NIfTI file')
    parser.add_argument('-o', '--output', required=True,
                      help='Path to save MP4 file')
    parser.add_argument('-d', '--dimension', type=int, default=2, choices=[0, 1, 2],
                      help='Dimension to slice along (0: sagittal, 1: coronal, 2: axial (default))')
    parser.add_argument('--fps', type=int, default=10,
                      help='Frames per second (default: 10)')
    parser.add_argument('--no-normalize', action='store_false', dest='normalize',
                      help='Disable intensity normalization')
    
    args = parser.parse_args()
    
    # Ensure output path has .mp4 extension
    output_path = args.output
    if not output_path.endswith('.mp4'):
        output_path += '.mp4'
    
    nii_to_mp4(
        input_path=args.input,
        output_path=output_path,
        dimension=args.dimension,
        fps=args.fps,
        normalize=args.normalize
    ) 

def round_cli():
    parser = argparse.ArgumentParser(description='Round NIfTI image pixel values')
    parser.add_argument('-i', '--input', required=True,
                      help='Path to input NIfTI file (will be overwritten)')
    
    args = parser.parse_args()
    
    round_nifti(args.input) 

def rembg_cli():
    parser = argparse.ArgumentParser(description='rembg NIfTI image pixel values')
    parser.add_argument('-i', '--input', required=True,
                      help='Path to input NIfTI file (will be overwritten)')
    parser.add_argument('-o', '--output', 
                      help='Path to output NIfTI file')
    parser.add_argument('-m', '--mask', 
                      help='Path to output mask NIfTI file')
    parser.add_argument('-d', '--dims', type=int, nargs='+', default=[2],
                        help='Dimensions to process (e.g., 2 or 0 1 2)')
    
    args = parser.parse_args()

    remove_background_nifti(args.input, args.output, args.mask, args.dims)

def denoise_mp2rage():

    parser = argparse.ArgumentParser(description='MP2RAGE robust combination processing')
    
    parser.add_argument('--uni', type=str, required=True,
                        help='Path to UNI image (.nii or .nii.gz)')
    parser.add_argument('--inv1', type=str, required=True,
                        help='Path to INV1 image (.nii or .nii.gz)')
    parser.add_argument('--inv2', type=str, required=True,
                        help='Path to INV2 image (.nii or .nii.gz)')
    parser.add_argument('--output', '-o', type=str, required=True,
                        help='Output path for processed image')
    parser.add_argument('--regularization', '-r', type=float, default=None,
                        help='Noise regularization factor (default: None for interactive mode)')

    args = parser.parse_args()

    mp2rage_data = {
        'filenameUNI': args.uni,
        'filenameINV1': args.inv1,
        'filenameINV2': args.inv2,
        'filenameOUT': args.output
    }
    _, _ = robust_combination(mp2rage_data, regularization=args.regularization,)