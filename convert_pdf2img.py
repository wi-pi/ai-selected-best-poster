import argparse
import os
from pdf2image import convert_from_path

def convert_pdfs_to_images(input_dir, output_dir, dpi=300):
    """
    Otained this code snippert from GPT
    Convert all PDF files in a directory to PNG images and save them in another directory.

    Parameters:
    - input_dir (str): Path to the directory containing PDF files.
    - output_dir (str): Path to the directory where PNG files will be saved.
    - dpi (int): Resolution of the output images. Default is 300 DPI.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Get all PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]

    if not pdf_files:
        print(f"No PDF files found in {input_dir}")
        return

    print(f"Found {len(pdf_files)} PDF(s) in {input_dir}. Converting to images...")

    # Iterate over PDF files and convert them
    for pdf_file in pdf_files:
        pdf_path = os.path.join(input_dir, pdf_file)
        pdf_name = os.path.splitext(pdf_file)[0]

        # Convert PDF to images
        images = convert_from_path(pdf_path, dpi=dpi)
        
        # Save each page as a separate PNG file
        for i, image in enumerate(images):
            output_file = os.path.join(output_dir, f"{pdf_name}_page_{i + 1}.png")
            image.save(output_file, "PNG")
            print(f"Saved: {output_file}")

    print("Conversion completed!")

def parse_args():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input_dir', default="./pdfs", type=str, help='Path to the directory containing PDF files.')
    parser.add_argument('--output_dir', default="./images", type=str, help='Path to the directory where PNG files will be saved.')

    return parser.parse_args() 


if __name__ == "__main__":
    args = parse_args()
    convert_pdfs_to_images(args.input_dir, args.output_dir)


