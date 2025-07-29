# cli.py
import argparse
from . import simple
import sys

def main():
    parser = argparse.ArgumentParser(description="CollectionFC Simple Mode")
    parser.add_argument('--mode', required=True, choices=['simple'], help='Mode to run')
    parser.add_argument('--input', required=True, help='Input ledger CSV')
    parser.add_argument('--forecast_path', default='forecast.csv', help='Output forecast CSV')
    parser.add_argument('--matrix_path', default='transition_matrix.csv', help='Output transition matrix CSV')
    parser.add_argument('--validation_path', default='validation.json', help='Output validation JSON')
    args = parser.parse_args()

    if args.mode == 'simple':
        simple.run_simple_mode(args.input, args.forecast_path, args.matrix_path, args.validation_path)
    else:
        print(f"Unknown mode: {args.mode}")
        sys.exit(1)

if __name__ == "__main__":
    main() 