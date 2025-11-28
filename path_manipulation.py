import os

def replace_star_with_x(directory):
    """
    Rename all files in the given directory by replacing '*' with 'x'.
    """
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)
        if os.path.isfile(old_path):
            # Replace '*' with 'x'
            new_filename = filename.replace('*', 'x')
            new_path = os.path.join(directory, new_filename)
            
            # Avoid overwriting existing files
            if new_path != old_path:
                os.rename(old_path, new_path)
                print(f'Renamed: {filename} -> {new_filename}')


if __name__ == "__main__":
    replace_star_with_x(r"result/base_expressions")