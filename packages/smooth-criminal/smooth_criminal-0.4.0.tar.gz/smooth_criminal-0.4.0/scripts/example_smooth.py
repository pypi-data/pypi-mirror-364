from smooth_criminal.core import smooth

@smooth
def fast_sum():
    total = 0
    for i in range(1_000_000):
        total += i
    return total

if __name__ == "__main__":
    print("Calling fast_sum() with @smooth applied directly...")
    result = fast_sum()
    print("Result:", result)
