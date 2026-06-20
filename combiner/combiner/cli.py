"""Command-line interface for combiner package."""


import argparse
import os
from .core import (
    execute_combine,
    execute_spread,
    execute_encode,
    execute_decode,
    info,
    DEFAULT_ENCODE_MAX_SIZE,
)
from . import __version__




def main():
    """Main entry point for the combiner CLI."""
    parser = argparse.ArgumentParser(
        description='Combiner - A tool to combine and spread files across directories.',
        prog='combiner'
    )
   
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
   
    parser.add_argument(
        'mode',
        metavar='mode',
        type=str,
        choices=['combine', 'spread', 'encode', 'decode'],
        help="Operation mode: 'combine', 'spread', 'encode', or 'decode'."
    )
   
    parser.add_argument(
        '-ed', '--executed-directory',
        dest='executed_directory',
        type=str,
        default=os.getcwd(),
        help='Input executed directory. Default value is current directory'
    )
   
    parser.add_argument(
        '-od', '--output-directory',
        dest='output_directory',
        type=str,
        required=True,
        help='Input output directory'
    )
   
    parser.add_argument(
        '-e', '--exclude-folder',
        dest='exclude_folder',
        type=str,
        nargs='*',
        help='Exclude directories'
    )
   
    parser.add_argument(
        '--use-gitignore',
        dest='use_gitignore',
        action='store_true',
        help='(encode) Respect .gitignore rules in the executed directory'
    )
   
    parser.add_argument(
        '--max-size',
        dest='max_size',
        type=int,
        default=100,
        help='(encode) Maximum output part size in MB (default: 100)'
    )
   
    parser.add_argument(
        '--output-name',
        dest='output_name',
        type=str,
        default='combined',
        help='(encode) Base name for output part files (default: combined)'
    )
   
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        help='Enable verbose output'
    )
   
    args = parser.parse_args()


    # Extract arguments
    execution_mode = args.mode
    executed_dir = args.executed_directory
    output_dir = args.output_directory
    exclude_folders = args.exclude_folder
    use_gitignore = args.use_gitignore
    max_size_bytes = args.max_size * 1024 * 1024
    output_name = args.output_name
    verbose = args.verbose


    info(verbose, f'Executing - {execution_mode} mode...')
   
    # Execute the appropriate mode
    if execution_mode == 'combine':
        execute_combine(
            executed_dir=executed_dir,
            output_dir=output_dir,
            exclude_folders=exclude_folders,
            verbose=verbose
        )
    elif execution_mode == 'spread':
        execute_spread(
            executed_dir=executed_dir,
            output_dir=output_dir,
            verbose=verbose
        )
    elif execution_mode == 'encode':
        execute_encode(
            executed_dir=executed_dir,
            output_dir=output_dir,
            output_name=output_name,
            use_gitignore=use_gitignore,
            exclude_folders=exclude_folders,
            max_size_bytes=max_size_bytes,
            verbose=verbose
        )
    elif execution_mode == 'decode':
        execute_decode(
            executed_dir=executed_dir,
            output_dir=output_dir,
            verbose=verbose
        )
    else:
        parser.print_usage()




if __name__ == '__main__':
    main()





