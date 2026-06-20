"""Core functionality for combiner package."""


import base64
import hashlib
import os
import uuid
from os.path import join, relpath, getsize
from termcolor import colored


try:
    import pathspec
except ImportError:
    pathspec = None




MAX_OUTPUT_FILE_SIZE = 256 * 1024 * 1024  # 256 MB
DEFAULT_ENCODE_MAX_SIZE = 100 * 1024 * 1024  # 100 MB




class ReadFileError(Exception):
    def __init__(self, message, delete_path):
        self.message = message
        self.delete_path = delete_path
   
    def __str__(self):
        return f"ReadFileError: {self.message}"
   
    def get_delete_path(self) -> str:
        return self.delete_path




# ---------------------------------------------------------------------------
# Helpers for encode / decode
# ---------------------------------------------------------------------------


def load_gitignore_spec(source_dir: str, enabled: bool):
    """Return a PathSpec built from <source_dir>/.gitignore, or None."""
    if not enabled:
        return None
    if pathspec is None:
        raise RuntimeError(
            "'pathspec' package is required when --use-gitignore is set. "
            "Install it with: pip install pathspec"
        )
    gitignore_path = join(source_dir, '.gitignore')
    if not os.path.exists(gitignore_path):
        return None
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        patterns = [
            line.rstrip('\n')
            for line in f
            if line.strip() and not line.lstrip().startswith('#')
        ]
    return pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, patterns)




def is_excluded(file_path: str, source_dir: str, gitignore_spec, exclude_folders: set) -> bool:
    """Return True if file_path should be skipped during encoding."""
    rel = relpath(file_path, source_dir).replace('\\', '/')
    parts = rel.split('/')
    # Check manual folder exclusions against every path segment except the filename
    if any(part in exclude_folders for part in parts[:-1]):
        return True
    # Check gitignore spec — check the file itself and every ancestor directory
    if gitignore_spec is not None:
        if gitignore_spec.match_file(rel):
            return True
        # Also check parent directories for directory patterns like __pycache__/
        parts_without_file = parts[:-1]
        for i in range(1, len(parts_without_file) + 1):
            parent = '/'.join(parts_without_file[:i]) + '/'
            if gitignore_spec.match_file(parent):
                return True
    return False




def read_file_content(file_path: str) -> tuple:
    """Read a file and return (content_str, encoding_tag).


    Text files (UTF-8) are returned as-is with tag 'text'.
    Binary files are Base64-encoded and returned with tag 'base64'.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), 'text'
    except UnicodeDecodeError:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('ascii'), 'base64'




def _sha256_of_content(content: str, encoding_tag: str) -> str:
    """SHA-256 hex digest of the logical content used for encode/decode verification.


    For text files: hashes the UTF-8 bytes of the normalised content string.
    For base64 files: hashes the original raw binary bytes.
    This matches what execute_decode reconstructs, so the hash is platform-independent.
    """
    if encoding_tag == 'base64':
        raw = base64.b64decode(content)
    else:
        raw = content.encode('utf-8')
    return hashlib.sha256(raw).hexdigest()




def _encode_part_filename(output_name: str, part_index: int) -> str:
    return f'{output_name}_part{part_index:03d}.txt'




def _open_encode_part(output_dir: str, output_name: str, part_index: int):
    path = join(output_dir, _encode_part_filename(output_name, part_index))
    return path, open(path, 'w', encoding='utf-8', newline='')




def execute_encode(executed_dir: str, output_dir: str, output_name: str = 'combined',
                   use_gitignore: bool = False, exclude_folders: 'list[str]' = None,
                   max_size_bytes: int = DEFAULT_ENCODE_MAX_SIZE, verbose: bool = False):
    """Encode files from a directory into one or more output files.
   
    Args:
        executed_dir: Source directory to encode
        output_dir: Directory to write encoded files
        output_name: Base name for output files
        use_gitignore: Whether to respect .gitignore rules
        exclude_folders: List of folder names to exclude
        max_size_bytes: Maximum size per output file
        verbose: Whether to print verbose output
    """
    os.makedirs(output_dir, exist_ok=True)
    exclude_set = set(exclude_folders) if exclude_folders else set()
    gitignore_spec = load_gitignore_spec(executed_dir, use_gitignore)
    real_output_dir = os.path.realpath(output_dir)


    part_index = 1
    out_path, out_file = _open_encode_part(output_dir, output_name, part_index)
    try:
        for root, dirs, files in os.walk(executed_dir):
            # Prune excluded directories so os.walk never descends into them
            dirs[:] = [d for d in dirs if d not in exclude_set]
            # Prune directories matching gitignore patterns (e.g. __pycache__/, build/)
            if gitignore_spec is not None:
                dirs[:] = [
                    d for d in dirs
                    if not gitignore_spec.match_file(
                        relpath(join(root, d), executed_dir).replace('\\', '/') + '/'
                    )
                ]


            for filename in files:
                file_path = join(root, filename)


                # Never encode files that live inside the output directory
                real_file = os.path.realpath(file_path)
                if real_file.startswith(real_output_dir + os.sep) or real_file == real_output_dir:
                    continue


                if is_excluded(file_path, executed_dir, gitignore_spec, exclude_set):
                    info(verbose, f'Excluded: {relpath(file_path, executed_dir)}')
                    continue


                try:
                    content, encoding = read_file_content(file_path)
                    rel_path = relpath(file_path, executed_dir).replace('\\', '/')


                    if encoding == 'text':
                        num_lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
                    else:
                        num_lines = 0


                    sha256 = _sha256_of_content(content, encoding)
                    header = f'#begin#{rel_path}#{num_lines}#{encoding}#{sha256}#/begin#\n'
                    footer = f'#end#{rel_path}#/end#\n'
                    # Ensure body ends with newline so footer sits on its own line
                    body = content if (not content or content.endswith('\n')) else content + '\n'


                    out_file.write(header)
                    out_file.write(body)
                    out_file.write(footer)
                    out_file.flush()
                    info(verbose, f'Encoded ({encoding}): {rel_path}')


                    if getsize(out_path) > max_size_bytes:
                        if getsize(out_path) - len(header) - len(body) - len(footer) == 0:
                            # This single file exceeds the limit — warn but keep it
                            error(verbose, f'Warning: single file exceeds --max-size limit: {rel_path}')
                        out_file.close()
                        part_index += 1
                        out_path, out_file = _open_encode_part(output_dir, output_name, part_index)


                except Exception as ex:
                    error(verbose, f'Failed to encode {file_path}: {ex}')
    finally:
        out_file.close()


    # Remove the last part if it was opened but nothing was written into it
    if os.path.exists(out_path) and getsize(out_path) == 0:
        os.remove(out_path)




def _parse_encode_header(line: str):
    """Parse a #begin# header line. Returns (rel_path, num_lines, encoding, sha256) or None.


    sha256 is None for legacy files encoded before the integrity-hash feature.
    """
    stripped = line.rstrip('\n')
    if not stripped.startswith('#begin#') or not stripped.endswith('#/begin#'):
        return None
    payload = stripped[len('#begin#'):-len('#/begin#')]
    parts = payload.split('#')
    if len(parts) == 4:
        return parts[0], int(parts[1]), parts[2], parts[3]
    if len(parts) == 3:
        return parts[0], int(parts[1]), parts[2], None
    if len(parts) == 2:
        return parts[0], int(parts[1]), 'text', None  # legacy combine format
    return None




def execute_decode(executed_dir: str, output_dir: str, verbose: bool = False):
    """Decode files from encoded format back to original files.
   
    Args:
        executed_dir: Directory containing encoded .txt files
        output_dir: Directory to write decoded files
        verbose: Whether to print verbose output
    """
    os.makedirs(output_dir, exist_ok=True)


    txt_files = []
    for root, _, files in os.walk(executed_dir):
        for filename in files:
            if filename.endswith('.txt'):
                txt_files.append(join(root, filename))
    txt_files.sort()


    for file_path in txt_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            line = f.readline()
            while line:
                header = _parse_encode_header(line)
                if header is None:
                    line = f.readline()
                    continue


                rel_path, num_lines, encoding, stored_sha256 = header
                # Normalise separators from the stored header
                rel_path = rel_path.replace('/', os.sep)
                out_path = join(output_dir, rel_path)
                parent_dir = os.path.dirname(out_path)
                if parent_dir:
                    os.makedirs(parent_dir, exist_ok=True)


                actual_sha256 = None
                if encoding == 'base64':
                    b64_line = f.readline().rstrip('\n')
                    decoded_bytes = base64.b64decode(b64_line)
                    with open(out_path, 'wb') as out:
                        out.write(decoded_bytes)
                    if stored_sha256 is not None:
                        actual_sha256 = hashlib.sha256(decoded_bytes).hexdigest()
                else:
                    content_lines = [f.readline() for _ in range(num_lines)]
                    with open(out_path, 'w', encoding='utf-8', newline='') as out:
                        out.writelines(content_lines)
                    if stored_sha256 is not None:
                        actual_sha256 = hashlib.sha256(''.join(content_lines).encode('utf-8')).hexdigest()


                info(verbose, f'Decoded: {rel_path}')
                if stored_sha256 is not None:
                    if actual_sha256 == stored_sha256:
                        info(verbose, f'SHA-256 OK: {rel_path}')
                    else:
                        print(colored('[err] ', 'red'), f'SHA-256 MISMATCH for {rel_path}')
                        print('  stored: ', stored_sha256)
                        print('  actual: ', actual_sha256)
                line = f.readline()




def execute_combine(executed_dir: str, output_dir: str, exclude_folders: "list[str]" = None, verbose: bool = False):
    """Combine files from a directory tree into one or more output files.


    Each input file is wrapped with begin/end markers and appended to a
    generated output file in the target directory. When the output file grows
    beyond the configured maximum size, a new output file is created.
   
    Args:
        executed_dir: Source directory to combine files from
        output_dir: Directory to write combined files
        exclude_folders: List of folder names to exclude
        verbose: Whether to print verbose output
    """
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
                        # FACT: some files that does not end with newline, so add newline by default to work around with this
                        new_file.write('\n')
                        new_file.write(generate_header_line(relpath(file_path, executed_dir), len(lines)))
                        new_file.writelines(lines)
                        new_file.write('\n')
                        new_file.write(generate_footer_line(relpath(file_path, executed_dir)))
                        info(verbose, f'Combined successfully: {file_path}')
                   
                    # FACT: an output file size shoule be less than max file size
                    if (getsize(output_file_path) > MAX_OUTPUT_FILE_SIZE):
                        output_filename = generate_output_filename()
                        info(verbose, f'Exceed default file size ({MAX_OUTPUT_FILE_SIZE}MB), creating new file {output_filename}')
            except Exception as ex:
                error(verbose, f'Exception: {ex}')




def execute_spread(executed_dir: str, output_dir: str, verbose: bool = False):
    """Spread combined files back to individual files.
   
    Args:
        executed_dir: Directory containing combined files
        output_dir: Directory to write spread files
        verbose: Whether to print verbose output
    """
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
    """Generate a unique output filename using UUID."""
    return f'{uuid.uuid4()}.txt'




def generate_header_line(file_path: str, num_of_lines: int) -> str:
    """Generate a header line for a combined file."""
    return f'#begin#{file_path}#{num_of_lines}#/begin#\n'




def generate_footer_line(file_path: str):
    """Generate a footer line for a combined file."""
    return f'#end#{file_path}#/end#\n'




def info(verbose: bool, *args):
    """Print info message if verbose is enabled."""
    if verbose:
        text = colored('[info]', 'green')
        print(text, *args)




def error(verbose: bool, *args):
    """Print error message if verbose is enabled."""
    if verbose:
        text = colored('[err] ', 'red')
        print(text, *args)





