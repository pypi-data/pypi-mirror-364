from smooth_criminal.core import auto_boost

@auto_boost()
def calculate_stuff():
    return sum(range(500_000))

if __name__ == "__main__":
    print("Running calculate_stuff() to record its performance...")
    result = calculate_stuff()
    print("Result:", result)
