import os

def print_tree(startpath, exclude_dirs):
    for root, dirs, files in os.walk(startpath):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

if __name__ == '__main__':
    excludes = {'node_modules', '.venv', '.git', '.next', '__pycache__', 'coverage', '.pytest_cache', '.ruff_cache', 'dist', 'build', '.local'}
    print_tree('.', excludes)
