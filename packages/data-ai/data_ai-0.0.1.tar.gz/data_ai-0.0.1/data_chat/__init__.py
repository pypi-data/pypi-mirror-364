import sys
import argparse
import numpy as np
import io
from IPython import embed


def main():
    parser = argparse.ArgumentParser(description="Load CSV file and drop into a Python shell.")
    parser.add_argument('file', help='Path to the CSV file to load')
    parser.add_argument('--no-header', action='store_true', help='CSV has no header row')
    args = parser.parse_args()

    # Read CSV data from file
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            csv_content = f.read()
        csv_buffer = io.StringIO(csv_content)
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file '{args.file}': {e}")
        sys.exit(1)

    # Use numpy.genfromtxt for structured array with column access
    data = np.genfromtxt(
        csv_buffer,
        delimiter=",",
        names=not args.no_header,  # True if header exists, False if --no-header
        dtype=None,                # infer dtypes
        encoding="utf-8"
    )

    if args.no_header:
        banner = f"Loaded CSV data from '{args.file}' as numpy array in variable 'data'. Access columns with data[column_index]."
    else:
        banner = f"Loaded CSV data from '{args.file}' as numpy structured array in variable 'data'. Access columns with data['column_name']."
    
    user_ns = {'data': data, 'np': np}
    try:
        import matplotlib.pyplot as plt
        user_ns['plt'] = plt
    except ImportError:
        pass

    embed(user_ns=user_ns, banner1=banner)