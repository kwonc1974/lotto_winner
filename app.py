from flask import Flask, render_template, jsonify, request
import random

app = Flask(__name__)

def is_valid(numbers):
    odd = len([n for n in numbers if n % 2 == 1])
    even = 6 - odd
    if not (2 <= odd <= 4):
        return False
    low = len([n for n in numbers if n <= 22])
    high = 6 - low
    if not (2 <= low <= 4):
        return False
    total = sum(numbers)
    if not (120 <= total <= 160):
        return False
    numbers.sort()
    consecutive = 0
    for i in range(5):
        if numbers[i] + 1 == numbers[i + 1]:
            consecutive += 1
    if consecutive > 2:
        return False
    return True

def generate_hybrid_lotto():
    hot_numbers = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]
    selected_hot = random.sample(hot_numbers, 3)
    remaining_pool = list(set(range(1, 46)) - set(selected_hot))
    selected_random = random.sample(remaining_pool, 3)
    return sorted(selected_hot + selected_random)

def generate_smart_lotto():
    while True:
        candidate = random.sample(range(1, 46), 6)
        if is_valid(candidate):
            return sorted(candidate)

def generate_ai_lotto():
    hot_numbers = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]
    while True:
        selected_hot = random.sample(hot_numbers, 3)
        remaining_pool = list(set(range(1, 46)) - set(selected_hot))
        selected_random = random.sample(remaining_pool, 3)
        candidate = sorted(selected_hot + selected_random)
        if is_valid(candidate):
            return candidate

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_multiple')
def generate_multiple():
    rtype = request.args.get('type')
    count = int(request.args.get('count', 1))
    results = []

    for _ in range(count):
        if rtype == 'hybrid':
            results.append(generate_hybrid_lotto())
        elif rtype == 'smart':
            results.append(generate_smart_lotto())
        elif rtype == 'ai':
            results.append(generate_ai_lotto())

    return jsonify(results=results)

if __name__ == '__main__':
    app.run(debug=True)


