from converters import *


def main():    
    source_currency = input('Введите исходную валюту: \n')
    amount = int(input('Введите размер исходной валюты: \n'))
    target_currency = input('Введите целевую валюту: \n')
    converter = CurrencyConverter(source_currency, target_currency)
    print(f"{amount} {source_currency} to {target_currency}: {converter.convert(amount)}")

if __name__ == "__main__":
    main()