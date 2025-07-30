from smooth_criminal.core import auto_boost

@auto_boost(workers=4)
def double(x):
    return x * 2

if __name__ == "__main__":
    numbers = list(range(10_000))
    result = double(numbers)
    print(f"Processed {len(result)} numbers.")
