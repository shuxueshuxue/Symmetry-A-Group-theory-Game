def tuple_plus(*v: tuple) -> tuple:
    return tuple(map(lambda *a: sum(a), *v))


def negative(v: tuple) -> tuple:
    return tuple(-num for num in v)


def multiply(v: tuple, factor) -> tuple:
    return tuple(num * factor for num in v)


def isprime(n):
    if n <= 1:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def string_of(lst: list):
    return lst.__str__().replace('[', "").replace("]", "")

if __name__ == "__main__":
    print(tuple_plus((1, 2, 3), (1, 1, 1), (0, 1, 0)))
