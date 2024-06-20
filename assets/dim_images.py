import os
from PIL import Image, ImageEnhance

def dim_image(input_path, output_path, dim_factor=0.2):
    """Dim the image by the specified factor and save it to the output path"""
    image = Image.open(input_path)
    
    # Convert image to RGBA mode if it has an alpha channel
    if image.mode == 'RGBA':
        image = image.convert('RGBA')
        enhancer = ImageEnhance.Brightness(image)
        dimmed_image = enhancer.enhance(dim_factor)
        
        # Split alpha channel and merge with dimmed RGB image
        r, g, b, a = dimmed_image.split()
        dimmed_image = Image.merge('RGB', (r, g, b))
        dimmed_image.save(output_path, 'JPEG')
    else:
        image = image.convert('RGB')
        enhancer = ImageEnhance.Brightness(image)
        dimmed_image = enhancer.enhance(dim_factor)
        dimmed_image.save(output_path, 'JPEG')
        
def process_images(input_folder, output_folder, dim_factor=0.2):
    """ Process all images in the input folder and save dimmed versions in the output folder """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            dim_image(input_path, output_path, dim_factor)
            print(f"Processed {filename}")

if __name__ == '__main__':
    input_folder = '/Users/skyliu/Documents/philine/assets/illustrations'
    output_folder = '/Users/skyliu/Documents/philine/assets/dim'
    process_images(input_folder, output_folder)
