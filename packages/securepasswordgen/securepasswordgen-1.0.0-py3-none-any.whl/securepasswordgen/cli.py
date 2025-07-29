import argparse
from securepassgen.generator import generate_password

def main():
    parser = argparse.ArgumentParser(description="Secure Password Generator")
    parser.add_argument('-l', '--length', type=int, default=16, help='Password length (default: 16)')
    parser.add_argument('-nu','--no-upper', action='store_true', help='Exclude uppercase letters')
    parser.add_argument('-nl','--no-lower', action='store_true', help='Exclude lowercase letters')
    parser.add_argument('-nd','--no-digits', action='store_true', help='Exclude digits')
    parser.add_argument('-ns','--no-symbols', action='store_true', help='Exclude symbols')

    args = parser.parse_args()

    try:
        password = generate_password(
            length=args.length,
            use_upper=not args.no_upper,
            use_lower=not args.no_lower,
            use_digits=not args.no_digits,
            use_symbols=not args.no_symbols
        )
        print(f"Generated Password: {password}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
