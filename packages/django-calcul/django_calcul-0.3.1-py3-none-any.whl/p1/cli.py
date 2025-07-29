import argparse
from . import addition, soustraction, multiplication, division

def main():
    parser = argparse.ArgumentParser(description="Petite calculatrice en ligne de commande")
    parser.add_argument("operation", choices=["add", "sub", "mul", "div"], help="Opération à effectuer")
    parser.add_argument("a", type=float, help="Premier nombre")
    parser.add_argument("b", type=float, help="Deuxième nombre")
    
    args = parser.parse_args()

    if args.operation == "add":
        result = addition(args.a, args.b)
    elif args.operation == "sub":
        result = soustraction(args.a, args.b)
    elif args.operation == "mul":
        result = multiplication(args.a, args.b)
    elif args.operation == "div":
        result = division(args.a, args.b)

    print(f"Résultat : {result}")
