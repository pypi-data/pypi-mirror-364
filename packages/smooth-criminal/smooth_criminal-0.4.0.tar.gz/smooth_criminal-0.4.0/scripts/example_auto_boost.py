from smooth_criminal.core import auto_boost

@auto_boost()
def my_function():
    total = 0
    for i in range(1_000_000):
        total += i
    return total

if __name__ == "__main__":
    print("Result:", my_function())
