import requests
import sys
import locale


def fetch_order_book(exchange, pair):
    if exchange == "coinbase":
        url = f"https://api.pro.coinbase.com/products/{pair}/book?level=2"
        response = requests.get(url)
        data = response.json()
        bids = [[float(bid[0]), float(bid[1])] for bid in data["bids"]]
        asks = [[float(ask[0]), float(ask[1])] for ask in data["asks"]]
    elif exchange == "gemini":
        url = f"https://api.gemini.com/v1/book/{pair}"
        response = requests.get(url)
        data = response.json()
        bids = [[float(bid["price"]), float(bid["amount"])] for bid in data["bids"]]
        asks = [[float(ask["price"]), float(ask["amount"])] for ask in data["asks"]]
    elif exchange == "kraken":
        url = f"https://api.kraken.com/0/public/Depth?pair={pair}"
        response = requests.get(url)
        data = response.json()["result"][list(response.json()["result"].keys())[0]]
        bids = [[float(bid[0]), float(bid[1])] for bid in data["bids"]]
        asks = [[float(ask[0]), float(ask[1])] for ask in data["asks"]]
    else:
        raise ValueError("Unsupported exchange")

    return {"bids": bids, "asks": asks}


def get_price(order_book, quantity, side):
    total_quantity = 0
    total_price = 0
    orders = order_book[side]
    for order in orders:
        price, qty = order
        if total_quantity + qty >= quantity:
            total_price += (quantity - total_quantity) * price
            break
        else:
            total_quantity += qty
            total_price += qty * price
    return total_price


DEFAULT_BTC_QUANTITY = 10


def main():
    quantity = float(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_BTC_QUANTITY

    print(f"price discovery for {quantity} btc")

    exchanges = {"coinbase": "btc-usd", "gemini": "btcusd", "kraken": "btcusd"}

    order_books = {}
    for exchange, ccy_pair in exchanges.items():
        order_books[exchange] = fetch_order_book(exchange, ccy_pair)

    buy_prices = []
    sell_prices = []
    for exchange, order_book in order_books.items():
        buy_price = get_price(order_book, quantity, "asks")
        sell_price = get_price(order_book, quantity, "bids")
        buy_prices.append((exchange, buy_price))
        sell_prices.append((exchange, sell_price))

    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

    print(f"Prices to buy {quantity} BTC - cheapest first:")
    for exchange, price in sorted(buy_prices, key=lambda x: x[1]):
        print(f"{exchange.capitalize()}: ${price:.2f}")

    print(f"\nPrices to sell {quantity} BTC - expensive first:")
    for exchange, price in sorted(sell_prices, key=lambda x: x[1], reverse=True):
        print(f"{exchange.capitalize()}: ${price:.2f}")


if __name__ == "__main__":
    main()
