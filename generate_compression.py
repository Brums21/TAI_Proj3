import os
import gzip
import bz2
import lzma
from typing import Optional, List, Tuple

import zstandard as zstd
import click
import shutil


class Compressor:
    COMPRESSORS = {
        'gzip': gzip.open,
        'bzip2': bz2.open,
        'lzma': lzma.open,
        'zstd': zstd.ZstdCompressor,
    }

    @staticmethod
    def compress_file(compressor: str, input_file: str, output_file: str) -> None:
        """
        Compresses a file using the specified compressor.

        :param compressor: The name of the compressor to use. Must be one of the supported compressors.
        :param input_file: The path to the input file to be compressed.
        :param output_file: The path to the output file where the compressed data will be written.
        :return: None
        """
        try:
            if compressor not in Compressor.COMPRESSORS:
                print(f"Invalid compressor: {compressor}. Please use a valid compressor.")
                return

            if compressor == 'zstd':
                with open(input_file, 'rb') as f_in, open(output_file, 'wb') as f_out:
                    f_out.write(Compressor.COMPRESSORS[compressor]().compress(f_in.read()))
            else:
                with open(input_file, 'rb') as f_in, Compressor.COMPRESSORS[compressor](output_file, 'wb') as f_out:
                    f_out.writelines(f_in)
        except Exception as e:
            print(f"Error occurred while compressing file: {e}")


class FileManager:
    @staticmethod
    def clean_directory(directory_path: str) -> None:
        """
        Clean the specified directory by removing its contents and creating a new directory.

        :param directory_path: The path of the directory to be cleaned.
        :return: None
        """
        if os.path.exists(directory_path):
            shutil.rmtree(directory_path)
        os.makedirs(directory_path)

    @staticmethod
    def get_outfile_path(compressed_dir: str, base_name: str, extension: str) -> Optional[str]:
        """
        Generates the output file path based on the compressed directory, base name, and extension.

        :param compressed_dir: The directory where the compressed file will be saved.
        :param base_name: The base name for the output file.
        :param extension: The extension for the output file.
        :return: The output file path.
        """
        if not os.path.isdir(compressed_dir) or not base_name:
            print(f"Invalid directory or base name: {compressed_dir}, {base_name}")
            return None
        return os.path.join(compressed_dir, f'{base_name}{extension}')

    @staticmethod
    def concatenate_files(file1: str, file2: str, output_file: str) -> None:
        """
        Concatenates the contents of file1 and file2 and writes them to output_file.

        :param file1: The path to the first input file.
        :param file2: The path to the second input file.
        :param output_file: The path to the output file where the concatenated contents will be written.
        :return: None
        """
        if not os.path.isfile(file1) or not os.path.isfile(file2):
            print("One or both input files do not exist.")
            return

        if os.path.exists(output_file):
            print(f"Warning: {output_file} already exists and will be overwritten.")
        with open(output_file, 'wb') as f_out:
            for file in [file1, file2]:
                with open(file, 'rb') as f_in:
                    f_out.write(f_in.read())

    @staticmethod
    def get_file_size_in_bits(file_path: str) -> Optional[int]:
        """
        Get the file size in bits.

        :param file_path: The path to the file.
        :return: The file size in bits, or None if the file path is invalid.
        """
        if not os.path.isfile(file_path):
            print(f"Invalid file path: {file_path}")
            return None
        file_size_bytes = os.path.getsize(file_path)
        file_size_bits = file_size_bytes * 8
        return file_size_bits


class CompressionInstance:
    def __init__(self, compression_methods: List[str]):
        self.compression_methods = compression_methods
        self.signatures_dir = './song_signatures'
        self.compressed_dir = './compressed'
        self.trim_segment_file = './trim/output_segment'

    def compress_files(self) -> None:
        """
        Compresses files using the specified compression methods.

        :return: None
        """
        if not os.path.isdir(self.signatures_dir) or not os.path.isdir(self.compressed_dir):
            print("Invalid directory path / paths do not exist.")
            return

        for sign_file in os.listdir(self.signatures_dir):
            input_path = os.path.join(self.signatures_dir, sign_file)
            base_name = os.path.splitext(sign_file)[0]
            for method in self.compression_methods:
                output_path = FileManager.get_outfile_path(self.compressed_dir, base_name, '.' + method)
                Compressor.compress_file(method, input_path, output_path)
        print("Compression complete.")

    def compress_trim_segment(self) -> List[Tuple[str, str, int]]:
        """
        Compresses a trim segment file using selected compression methods.

        :return: A list of tuples containing the compression method, the compressed file name, and the file size in bits.
        """
        compressed_files = []
        for method in self.compression_methods:
            compressed_trim_segment_file = f'{self.trim_segment_file}.{method}'
            Compressor.compress_file(method, self.trim_segment_file, compressed_trim_segment_file)
            compressed_files.append((method, compressed_trim_segment_file, FileManager.get_file_size_in_bits(compressed_trim_segment_file)))
        return compressed_files

    def calculate_normalized_compressed_distance(self, compressed_files: List[Tuple[str, str, int]]) -> None:
        """
        Calculates the normalized compressed distance for each signature file against the compressed trim segment files.

        :param compressed_files: A list of tuples containing information about compressed files.
        :return: None
        """
        files_ordered_by_bits = []

        for method, compressed_trim_segment_file, compressed_trim_segment in compressed_files:
            for signature_file in os.listdir(self.signatures_dir):
                signature_file_path = os.path.join(self.signatures_dir, signature_file)
                base_name = os.path.splitext(signature_file)[0]
                compressed_file_path = FileManager.get_outfile_path(self.compressed_dir, base_name, '.' + method)

                if os.path.exists(compressed_file_path):
                    file_size_bits = FileManager.get_file_size_in_bits(compressed_file_path)
                    combined_file = './trim/temp_combined'
                    FileManager.concatenate_files(signature_file_path, self.trim_segment_file, combined_file)
                    Compressor.compress_file(method, combined_file, f'{combined_file}.{method}')
                    combined_file_size_bits = FileManager.get_file_size_in_bits(f'{combined_file}.{method}')
                    normalized_compressed_distance = (combined_file_size_bits - min(file_size_bits, compressed_trim_segment)) / max(file_size_bits, compressed_trim_segment)
                    files_ordered_by_bits.append((compressed_file_path, normalized_compressed_distance))
                    os.remove(f'{combined_file}.{method}')
                    os.remove(combined_file)

        files_ordered_by_bits.sort(key=lambda item: item[1])
        list(map(lambda item: print(f"Path: {item[0]}, Normalized Compressed Distance: {item[1]}"), files_ordered_by_bits))

    def run(self) -> None:
        """
        Runs the compression application.

        :return: None
        """
        self.compress_files()
        compressed_files = self.compress_trim_segment()
        self.calculate_normalized_compressed_distance(compressed_files)


@click.command()
@click.option('-c', '--compress', is_flag=True, help='Compress all songs.')
@click.option('-gzip', is_flag=True, help='Compress using gzip.')
@click.option('-bzip2', is_flag=True, help='Compress using bzip2.')
@click.option('-lzma', is_flag=True, help='Compress using lzma.')
@click.option('-zstd', is_flag=True, help='Compress using zstd.')
def main(compress, gzip, bzip2, lzma, zstd):
    """
    Main function to compress songs using various compression methods.

    :param compress: Whether to compress the songs or not.
    :param gzip: Whether to compress using gzip.
    :param bzip2: Whether to compress using bzip2.
    :param lzma: Whether to compress using lzma.
    :param zstd: Whether to compress using zstd.
    :return: None
    """
    if not (compress and (gzip or bzip2 or lzma or zstd)):
        print('Please provide valid compression option(s). Use --help for more info.')
        return

    compress_flags = {'gzip': gzip, 'bzip2': bzip2, 'lzma': lzma, 'zstd': zstd}
    selected_methods = [method for method, selected in compress_flags.items() if selected]

    if compress and selected_methods:
        app = CompressionInstance(selected_methods)
        app.run()
    else:
        print("No valid compression method specified.")


if __name__ == "__main__":
    main()
