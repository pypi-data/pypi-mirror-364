import argparse
from .converter import convert_currency

def main():
    parser = argparse.ArgumentParser(description="Convert currency using a fixed exchange rate.")
    parser.add_argument("amount", type=float, help="Amount to convert")
    parser.add_argument("rate", type=float, help="Exchange rate (ex: 0.85 for USD to EUR)")

    args = parser.parse_args()

    result = convert_currency(args.amount, args.rate)
    if result is not None:
        print(f"{args.amount} converted at rate {args.rate} = {result}")
    else:
        print("Error: Invalid input.")
