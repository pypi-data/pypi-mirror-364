from PIL import Image
import nibabel as nib
import numpy as np
from rembg import remove, new_session
from tqdm import tqdm
from pathlib import Path
import pdb

def clean_data(data, axis = 2):
    data = np.squeeze(data)
    processed_data = np.zeros_like(data)
    mask_data = np.zeros_like(data)
    session = new_session("u2net")

    for i in tqdm(range(data.shape[axis])):
        if axis == 2:
            slice_data = data[:,:,i]
        elif axis == 1:
            slice_data = data[:,i,:]
        elif axis == 0:
            slice_data = data[i,:,:]

        slice_normalized = ((slice_data - slice_data.min()) / (slice_data.max() - slice_data.min()) * 255).astype(np.uint8)
        slice_img = Image.fromarray(slice_normalized).convert('RGB')
        output = remove(slice_img, session=session, alpha_matting=True, alpha_matting_foreground_threshold=240)
        output_array = np.array(output)
        mask_array = output_array[:,:,3]
        processed_slice = slice_data * (mask_array / 255)

        if axis == 2:
            processed_data[:,:,i] = processed_slice
            mask_data[:,:,i] = mask_array
        elif axis == 1:
            processed_data[:,i,:] = processed_slice
            mask_data[:,i,:] = mask_array
        elif axis == 0:
            processed_data[i,:,:] = processed_slice
            mask_data[i,:,:] = mask_array
    
    return processed_data, mask_data

def remove_background_nifti(input_path, output_path=None, mask_path=None, dims=[2]):
    """
    Remove background from a grayscale NIfTI file using rembg and save the result and mask as NIfTI files.
    
    :param input_path: Path to the input NIfTI file
    :param output_path: Path to save the output NIfTI file with background removed
    :param mask_path: Path to save the mask NIfTI file
    """
    # Load the NIfTI file
    dir = str(Path(input_path).parent)
    filename = str(Path(input_path).name)

    img = nib.load(input_path)
    data = img.get_fdata()
    
    masks = []
    for dim in dims:
        _, mask_array = clean_data(data, axis = dim)
        masks.append((mask_array > 0))

    mask = np.stack(masks).mean(0)

    processed_img = mask * data

    if mask_path is not None:
        nib.save(nib.Nifti1Image(np.int16(mask), img.affine), mask_path)    
        print(f"Mask NIfTI saved to: {mask_path}") 
    else:
        nib.save(nib.Nifti1Image(np.int16(mask), img.affine), f'{dir}/mask_{filename}')    
        print(f"Mask NIfTI saved to: {dir}/mask_{filename}") 
       

    if output_path is not None:
        nib.save(nib.Nifti1Image(processed_img, img.affine), output_path)  
        print(f"Background removed NIfTI saved to: {mask_path}")
    else:
        nib.save(nib.Nifti1Image(processed_img, img.affine), f'{dir}/rembg_{filename}') 
        print(f"Background removed NIfTI saved to: {dir}/mask_{filename}")

    
     

if __name__ == "__main__":

    remove_background_nifti('/Users/jinghangli/Downloads/md_MH484.nii.gz')