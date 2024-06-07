import os
import gzip
import bz2
import lzma
import zstandard as zstd
import click
import shutil

def clean_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path)

def compress_gzip(input_file, output_file):
    with open(input_file, 'rb') as f_in, gzip.open(output_file, 'wb') as f_out:
        f_out.writelines(f_in)

def compress_bzip2(input_file, output_file):
    with open(input_file, 'rb') as f_in, bz2.open(output_file, 'wb') as f_out:
        f_out.writelines(f_in)

def compress_lzma(input_file, output_file):
    with open(input_file, 'rb') as f_in, lzma.open(output_file, 'wb') as f_out:
        f_out.writelines(f_in)

def compress_zstd(input_file, output_file):
    cctx = zstd.ZstdCompressor()
    with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
        f_out.write(cctx.compress(f_in.read()))

def compress_files(gzip_flag, bzip2_flag, lzma_flag, zstd_flag):
    signatures_dir = './song_signatures'
    compressed_dir = './compressed'
    
    for sign_file in os.listdir(signatures_dir):
        input_path = os.path.join(signatures_dir, sign_file)
        base_name = os.path.splitext(sign_file)[0]

        if gzip_flag:
            compress_gzip(input_path, os.path.join(compressed_dir, f'{base_name}.gz'))
        if bzip2_flag:
            compress_bzip2(input_path, os.path.join(compressed_dir, f'{base_name}.bz2'))
        if lzma_flag:
            compress_lzma(input_path, os.path.join(compressed_dir, f'{base_name}.xz'))
        if zstd_flag:
            compress_zstd(input_path, os.path.join(compressed_dir, f'{base_name}.zst'))

    print("Compression complete.")

def concatenate_files(file1, file2, output_file):
    with open(output_file, 'wb') as f_out:
        for file in [file1, file2]:
            with open(file, 'rb') as f_in:
                f_out.write(f_in.read())

def get_file_size_in_bits(file_path):
    file_size_bytes = os.path.getsize(file_path)
    file_size_bits = file_size_bytes * 8
    return file_size_bits

@click.command()
@click.option('-c', '--compress', is_flag=True, help='Compress all songs')
@click.option('-gzip', is_flag=True, help='Compress using gzip')
@click.option('-bzip2', is_flag=True, help='Compress using bzip2')
@click.option('-lzma', is_flag=True, help='Compress using lzma')
@click.option('-zstd', is_flag=True, help='Compress using zstd')
def main(compress, gzip, bzip2, lzma, zstd):
    if compress:
        compress_files(gzip, bzip2, lzma, zstd)

    if not bzip2:
        print("Currently only supporting bzip2 for NCD calculation.")
        return

    # Ensure trim segment is compressed
    trim_segment_file = './trim/output_segment'
    compressed_trim_segment_file = './trim/output_segment.bz2'
    compress_bzip2(trim_segment_file, compressed_trim_segment_file)
    
    compressed_trim_segment = get_file_size_in_bits(compressed_trim_segment_file)
    print(f"Compressed trim segment size in bits: {compressed_trim_segment}")

    # Iterate over files in song_signatures and match with .bz2 files in compressed
    song_signatures_dir = './song_signatures'
    compressed_dir = './compressed'
    files_ordered_by_bits = []

    for signature_file in os.listdir(song_signatures_dir):
        signature_file_path = os.path.join(song_signatures_dir, signature_file)
        if os.path.isfile(signature_file_path):
            
            base_name = os.path.splitext(signature_file)[0]
            
            compressed_file_path = os.path.join(compressed_dir, f'{base_name}.bz2')

            if os.path.exists(compressed_file_path):
                file_size_bits = get_file_size_in_bits(compressed_file_path)
                
                combined_file = './trim/temp_combined'
                concatenate_files(signature_file_path, './trim/output_segment', combined_file)
                
                compress_bzip2('./trim/temp_combined', './trim/temp_combined.bz2')
                combined_file_size_bits = get_file_size_in_bits('./trim/temp_combined.bz2')
                
                normalized_compressed_distance = (combined_file_size_bits - min(file_size_bits, compressed_trim_segment)) / max(file_size_bits, compressed_trim_segment)
                files_ordered_by_bits.append({compressed_file_path: normalized_compressed_distance})
                
                os.remove('./trim/temp_combined.bz2')
                os.remove('./trim/temp_combined')
    
    files_ordered_by_bits = sorted(files_ordered_by_bits, key=lambda x: list(x.values())[0])
    for item in files_ordered_by_bits:
        print(item)

if __name__ == "__main__":
    main()
