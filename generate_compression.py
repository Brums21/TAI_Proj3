import os
import gzip
import bz2
import lzma
from typing import Optional, List, Tuple
import zstandard as zstd
import click
import shutil
import csv


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

    @staticmethod
    def list_existing_files() -> None:
        """
        List the files in the specified directory.

        :param directory: The directory to list the files from.
        :return: A list of file names in the directory.
        """
        directories_to_list = ['./song_signatures', './compressed']
        for directory in directories_to_list:
            if os.path.isdir(directory):
                for filename in os.listdir(directory):
                    print(os.path.join(directory, filename))
            else:
                print(f"Directory does not exist: {directory}")


class CompressionInstance:
    def __init__(self, compression_methods: List[str], \
        folder_test: Optional[str] = None, file_test: Optional[str] = None, \
            noise_type: Optional[str] = None, noise_percentage: Optional[str] = None, \
            test_start: Optional[str] = None, test_duration: Optional[str] = None, \
            csv_file: Optional[str] = None):
        folder_test = folder_test if folder_test is not None else "analyze"
        file_test = file_test if file_test is not None else "signature_test"
        
        self.file_test = file_test
        
        self.noise_type = noise_type if noise_type is not None else "none"
        self.noise_percentage = noise_percentage if noise_percentage is not None else "none"
        
        self.test_start = test_start if test_start is not None else "none"
        self.test_duration = test_duration if test_duration is not None else "none"
        
        self.csv_file = csv_file
        self.folder_test = folder_test
        self.compression_methods = compression_methods
        self.signatures_dir = './song_signatures'
        self.compressed_dir = './compressed'
        self.trim_segment_file = f'./{folder_test}/{file_test}'

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
            file_size_bits = FileManager.get_file_size_in_bits(compressed_trim_segment_file)
            if file_size_bits is not None:
                compressed_files.append((method, compressed_trim_segment_file, file_size_bits))
        return compressed_files

    def calculate_normalized_compressed_distance(self, compressed_files: List[Tuple[str, str, int]], folder_test: Optional[str] = None) -> None:
        """
        Calculates the normalized compressed distance for each signature file against the compressed trim segment files.

        :param compressed_files: A list of tuples containing information about compressed files.
        :return: None
        """
        files_ordered_by_bits = []
        csv_file = getattr(self, 'csv_file', None)

        csv_writer = None
        if csv_file:
            file_exists = os.path.isfile(csv_file)
            csv_file_handle = open(csv_file, mode='a', newline='')
            csv_writer = csv.writer(csv_file_handle)
            if not file_exists:
                csv_writer.writerow(['file', 'NCD', 'encoding', 'noise_type', 'file_tested', 'noise_percentage', 'test_start', 'test_duration'])

        for method, compressed_trim_segment_file, compressed_trim_segment in compressed_files:
            for signature_file in os.listdir(self.signatures_dir):
                signature_file_path = os.path.join(self.signatures_dir, signature_file)
                base_name = os.path.splitext(signature_file)[0]
                compressed_file_path = FileManager.get_outfile_path(self.compressed_dir, base_name, '.' + method)

                if os.path.exists(compressed_file_path):
                    file_size_bits = FileManager.get_file_size_in_bits(compressed_file_path)
                    
                    folder_test = folder_test if folder_test is not None else "interpretations_trim"
                    combined_file = f'./{folder_test}/temp_combined'
                    
                    FileManager.concatenate_files(signature_file_path, self.trim_segment_file, combined_file)
                    Compressor.compress_file(method, combined_file, f'{combined_file}.{method}')
                    combined_file_size_bits = FileManager.get_file_size_in_bits(f'{combined_file}.{method}')
                    
                    if combined_file_size_bits is None:
                        continue
                    
                    normalized_compressed_distance = (combined_file_size_bits - min(file_size_bits, compressed_trim_segment)) / max(file_size_bits, compressed_trim_segment)
                    result = (base_name, normalized_compressed_distance, method, self.noise_type, self.file_test, self.noise_percentage, self.test_start, self.test_duration)
                    files_ordered_by_bits.append(result)
                    
                    if csv_writer:
                        csv_writer.writerow(result)
                    
                    os.remove(f'{combined_file}.{method}')
                    os.remove(combined_file)

        if csv_writer:
            csv_file_handle.close()
        else:
            files_ordered_by_bits.sort(key=lambda item: item[1])
            for item in files_ordered_by_bits:
                print(f"Path: {item[0]}, Normalized Compressed Distance: {item[1]}, Encoding: {item[2]}, Noise: {item[3]}")

    def run(self, compress) -> None:
        """
        Runs the compression application.

        :return: None
        """
        if compress:
            self.compress_files()
        compressed_files = self.compress_trim_segment()
        self.calculate_normalized_compressed_distance(compressed_files, self.folder_test)


@click.command()
@click.option('-c', '--compress', is_flag=True, help='Compress all songs.')
@click.option('-gzip', is_flag=True, help='Compress using gzip.')
@click.option('-bzip2', is_flag=True, help='Compress using bzip2.')
@click.option('-lzma', is_flag=True, help='Compress using lzma.')
@click.option('-zstd', is_flag=True, help='Compress using zstd.')
@click.option('-folder-test', help="Folder where tests are.")
@click.option('-test-file', help="Signature file to test.")
@click.option('-noise-type', help="Type of noise used.")
@click.option('-noise-percentage', help="Percentage of noise used.")
@click.option('-test-start', help="Test file start time.")
@click.option('-test-duration', help="Test file duration.")
@click.option('-csv-file', help="File to write the tests to.")
def main(compress, gzip, bzip2, lzma, zstd, folder_test, test_file, noise_type, noise_percentage, test_start, test_duration, csv_file):
    """
    Main function to compress songs using various compression methods.

    :param compress: Whether to compress the songs or not.
    :param gzip: Whether to compress using gzip.
    :param bzip2: Whether to compress using bzip2.
    :param lzma: Whether to compress using lzma.
    :param zstd: Whether to compress using zstd.
    :param folder-test: Folder where the files to be tested are located.
    :param test-file: File to be tested.
    :param noise-type: Type of noise used.
    :param noise-percentage: Percentage of noise used.
    :param test-start: Test file start time.
    :param test-duration: Test file duration.
    :param csv-file: File to write the tests to.
    :return: None
    """

    compress_flags = {'gzip': gzip, 'bzip2': bzip2, 'lzma': lzma, 'zstd': zstd}
    selected_methods = [method for method, selected in compress_flags.items() if selected]
    if selected_methods:
        app = CompressionInstance(selected_methods, folder_test, test_file, noise_type, noise_percentage, test_start, test_duration, csv_file)
        app.run(compress)
    else:
        print("No valid compression method specified.")


if __name__ == "__main__":
    main()
