import os
import gzip
import bz2
import lzma
import zstandard as zstd
import click
import shutil

COMPRESSORS = {
    'gzip': gzip.open,
    'bzip2': bz2.open,
    'lzma': lzma.open,
    'zstd': zstd.ZstdCompressor,
}


def clean_directory(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
    os.makedirs(directory_path)


def compress_file(compressor, input_file, output_file):
    try:
        if compressor not in COMPRESSORS:
            print(f"Invalid compressor: {compressor}. Please use a valid compressor.")
            return

        if compressor == 'zstd':
            with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
                f_out.write(COMPRESSORS[compressor]().compress(f_in.read()))
        else:
            with open(input_file, 'rb') as f_in, COMPRESSORS[compressor](output_file, 'wb') as f_out:
                f_out.writelines(f_in)
    except Exception as e:
        print(f"Error occurred while compressing file: {e}")


def get_outfile_path(compressed_dir, base_name, extension):
    if not os.path.isdir(compressed_dir) or not base_name:
        print(f"Invalid directory or base name: {compressed_dir}, {base_name}")
        return None
    return os.path.join(compressed_dir, f'{base_name}{extension}')


def compress_files(compression_methods):
    signatures_dir = './song_signatures'
    compressed_dir = './compressed'

    if not os.path.isdir(signatures_dir) or not os.path.isdir(compressed_dir):
        print("Invalid directory path / paths do not exist.")
        return

    for sign_file in os.listdir(signatures_dir):
        input_path = os.path.join(signatures_dir, sign_file)
        base_name = os.path.splitext(sign_file)[0]
        for method in compression_methods:
            compress_file(method, input_path, get_outfile_path(compressed_dir, base_name, '.' + method))
    print("Compression complete.")


def concatenate_files(file1, file2, output_file):
    if not os.path.isfile(file1) or not os.path.isfile(file2):
        print("One or both input files do not exist.")
        return

    if os.path.exists(output_file):
        print(f"Warning: {output_file} already exists and will be overwritten.")
    with open(output_file, 'wb') as f_out:
        for file in [file1, file2]:
            with open(file, 'rb') as f_in:
                f_out.write(f_in.read())


def get_file_size_in_bits(file_path):
    if not os.path.isfile(file_path):
        print(f"Invalid file path: {file_path}")
        return None
    file_size_bytes = os.path.getsize(file_path)
    file_size_bits = file_size_bytes * 8
    return file_size_bits


@click.command()
@click.option('-c', '--compress', is_flag=True, help='Compress all songs.')
@click.option('-gzip', is_flag=True, help='Compress using gzip.')
@click.option('-bzip2', is_flag=True, help='Compress using bzip2.')
@click.option('-lzma', is_flag=True, help='Compress using lzma.')
@click.option('-zstd', is_flag=True, help='Compress using zstd.')
def main(compress, gzip, bzip2, lzma, zstd):
    if not (compress and (gzip or bzip2 or lzma or zstd)):
        print('Please provide valid compression option(s). Use --help for more info.')
        return
    compress_flags = {'gzip': gzip, 'bzip2': bzip2, 'lzma': lzma, 'zstd': zstd}
    selected_methods = [method for method, flag in compress_flags.items() if flag]

    if compress and selected_methods:
        compress_files(selected_methods)
    else:
        print("No valid compression method specified.")
        return

    trim_segment_file = './trim/output_segment'
    compressed_dir = './compressed'
    files_ordered_by_bits = []

    for method in selected_methods:
        compressed_trim_segment_file = f'./trim/output_segment.{method}'
        compress_file(method, trim_segment_file, compressed_trim_segment_file)
        compressed_trim_segment = get_file_size_in_bits(compressed_trim_segment_file)

        for signature_file in os.listdir('./song_signatures'):
            signature_file_path = os.path.join('./song_signatures', signature_file)
            base_name = os.path.splitext(signature_file)[0]
            compressed_file_path = get_outfile_path(compressed_dir, base_name, '.' + method)

            if os.path.exists(compressed_file_path):
                file_size_bits = get_file_size_in_bits(compressed_file_path)
                combined_file = './trim/temp_combined'
                concatenate_files(signature_file_path, './trim/output_segment', combined_file)
                compress_file(method, combined_file, f'./trim/temp_combined.{method}')
                combined_file_size_bits = get_file_size_in_bits('./trim/temp_combined.' + method)
                normalized_compressed_distance = (combined_file_size_bits - min(file_size_bits,
                                                                                compressed_trim_segment)) / max(
                    file_size_bits, compressed_trim_segment)
                files_ordered_by_bits.append((compressed_file_path, normalized_compressed_distance))
                os.remove('./trim/temp_combined.' + method)
                os.remove(combined_file)

    files_ordered_by_bits.sort(key=lambda item: item[1])
    for file_path, distance in files_ordered_by_bits:
        print(f"Path: {file_path}, Normalized Compressed Distance: {distance}")


if __name__ == "__main__":
    main()
