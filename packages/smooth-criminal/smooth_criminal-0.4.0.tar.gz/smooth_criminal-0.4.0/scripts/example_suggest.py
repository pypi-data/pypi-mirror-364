from smooth_criminal.core import auto_boost

@auto_boost()
def to_analyze():
    total = 0
    for i in range(1000):
        total += i
    return total

if __name__ == "__main__":
    print("Running to_analyze() to register execution...")
    result = to_analyze()
    print("Result:", result)
