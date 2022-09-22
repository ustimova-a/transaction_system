def generate():
    for i in range(3):
        yield i

generator = generate()
print(next(generator))
print(next(generator))
print(next(generator))