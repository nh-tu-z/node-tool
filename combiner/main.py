import argparse
import os
import uuid
from os.path import join, relpath, getsize
from termcolor import colored


MAX_OUTPUT_FILE_SIZE = 256 * 1024 * 1024 #256MB


class ReadFileError(Exception):
    def __init__(self, message, delete_path):
        self.message = message
        self.delete_path = delete_path
   
    def __str__(self):
        return f"ReadFileError: {self.message}"
   
    def get_delete_path(self) -> str:
        return self.delete_path


def execute_combine(executed_dir: str,output_dir: str, exclude_folders: "list[str]"=None, verbose: bool=False):
    """TODO:"""
    if exclude_folders is not None:
        list_of_excluded_folders = ', '.join(exclude_folders)
        info(verbose, f'Exclude folders: {list_of_excluded_folders}')
    output_filename = generate_output_filename()
    for root, dirs, files in os.walk(executed_dir):


        if exclude_folders is not None:
            dirs[:] = [d for d in dirs if d not in exclude_folders]


        for filename in files:
            file_path = join(root, filename)
            info(verbose, f'Executing file: {file_path}')
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    output_file_path = join(output_dir, output_filename)
                    with open(output_file_path, 'a') as new_file:
                        #FACT: some files that does not end with newline, so add newline by default to work around with this
                        new_file.write('\n')
                        new_file.write(generate_header_line(relpath(file_path, executed_dir), len(lines)))
                        new_file.writelines(lines)
                        new_file.write('\n')
                        new_file.write(generate_footer_line(relpath(file_path, executed_dir)))
                        info(verbose, f'Combined successfully: {file_path}')
                   
                    #FACT: an output file size shoule be less than max file size
                    if (getsize(output_file_path) > MAX_OUTPUT_FILE_SIZE):
                        output_filename = generate_output_filename()
                        info(verbose, f'Exceed default file size ({MAX_OUTPUT_FILE_SIZE}MB), creating new file {output_filename}')
            except Exception as ex:
                error(verbose, f'Exception: {ex}')


def execute_spread(executed_dir: str,output_dir: str, verbose: bool=False):
    for root, _, files in os.walk(executed_dir):
        for filename in files:
            file_path = join(root, filename)
            with open(file_path, 'r') as file:
                file_path = ''
                line = file.readline()
                while line:
                    if line.startswith('#begin#') and line.endswith('#/begin#\n'):
                        print(line)
                        headers = join(output_dir, line[7:-9]).split('#')
                        parent_dir = os.path.dirname(headers[0])
                        if not os.path.exists(parent_dir):
                            os.makedirs(parent_dir)
                        with open(headers[0], 'a') as new_file:
                            for _ in range(int(headers[1])):
                                new_file.write(file.readline())
                    line = file.readline()

def generate_output_filename():
    return f'{uuid.uuid4()}.txt'


def generate_header_line(file_path: str, num_of_lines: int) -> str:
    return f'#begin#{file_path}#{num_of_lines}#/begin#\n'


def generate_footer_line(file_path: str):
    return f'#end#{file_path}#/end#\n'


def info(verbose: bool, *args):
    if verbose:
        text = colored('[info]', 'green')
        print(text, *args)


def error(verbose: bool, *args):
    if verbose:
        text = colored('[err] ', 'red')
        print(text, *args)

if (__name__== '__main__'):
    parser = argparse.ArgumentParser(description='File combiner.')
    parser.add_argument('mode', metavar='mode', type=str,
                        choices=['combine', 'spread'],
                        help='should be \'combine\' or \'spread\'.')
    #TODO: default get current directory and validate string input is a valid directory
    parser.add_argument('-ed', '--executed-directory', dest='executed_directory', type=str,
                        default=os.getcwd(),
                        help='Input executed directory. Default value is current directory')
    parser.add_argument('-od', '--output-directory', dest='output_directory', type=str,
                        required=True,
                        help='Input output directory')
    parser.add_argument('-e', '--exclude-folder', dest='exclude_folder', type=str,
                        nargs='*',
                        help='Exclude directories')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Dry run')
    #TODO: add dry run mode
    args = parser.parse_args()


    # validate input arguments
    execution_mode = args.mode
    executed_dir = args.executed_directory
    output_dir = args.output_directory
    exclude_folders = args.exclude_folder
    verbose = args.verbose


    info(verbose, f'Executing - {execution_mode} mode...')
    match execution_mode:
        case 'combine':  
            execute_combine(executed_dir=executed_dir, output_dir=output_dir, exclude_folders=exclude_folders, verbose=verbose)
            pass
        case 'spread':
            execute_spread(executed_dir=executed_dir, output_dir=output_dir, verbose=verbose)
        case _:
            parser.print_usage()
   