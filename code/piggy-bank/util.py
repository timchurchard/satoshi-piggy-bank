

def get_total_balance(depth, coin):
    # Calculate total balance and find last unused address
    total_balance = 0.0
    first_unused_addr = None
    depth = int(depth)

    remaining = depth
    n = 0
    while True:
        addr = coin.generate_addr(n)
        balance, used = coin.check_balance(addr)
        if balance is None:
            # Note: Assume no internet so exit loop
            print("Running in offline mode. Addr {}".format(addr))
            first_unused_addr = addr
            break
        total_balance += balance
        print("Found n={} {} with balance {:.8f}".format(n, addr, balance))
        if not used:
            if first_unused_addr is None:
                first_unused_addr = addr
                print(" ^ First unused address")
            remaining = remaining - 1
        else:
            remaining = depth
        n = n + 1
        if remaining == 0:
            break

        if n == 1 and addr == coin.generate_addr(n):
            # Single mode!
            first_unused_addr = addr
            break
    return total_balance, first_unused_addr


def format_total_price(coin, total_balance, price):
    value = price * total_balance
    price = coin.price_fmt.format(price)
    value = coin.price_fmt.format(value)
    total_balance = coin.balance_fmt.format(total_balance)
    return total_balance, price, value
