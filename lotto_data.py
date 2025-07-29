import json
import random
import os
from datetime import datetime
from collections import Counter, defaultdict

RECOMMEND_FILE = 'recommendation_history.json'
WINNING_FILE = 'winning_numbers.json'

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

# ✅ 출현율 기반 하이브리드 추천
def generate_hybrid_lotto():
    freq_counter = get_number_frequencies(n=100)
    top_20 = [num for num, _ in freq_counter.most_common(20)]

    if len(top_20) < 3:
        top_20 = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]  # fallback

    selected_hot = random.sample(top_20, 3)
    remaining_pool = list(set(range(1, 46)) - set(selected_hot))
    selected_random = random.sample(remaining_pool, 3)

    result = sorted(selected_hot + selected_random)
    return {
        "numbers": result,
        "reason": "출현율 상위 번호 + 무작위 조합",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

def generate_smart_lotto():
    while True:
        candidate = random.sample(range(1, 46), 6)
        if is_valid(candidate):
            return {
                "numbers": sorted(candidate),
                "reason": "번호 균형 알고리즘 기반 필터링",
                "date": datetime.now().strftime("%Y-%m-%d")
            }

# ✅ 출현율 기반 AI 추천
def generate_ai_lotto():
    freq_counter = get_number_frequencies(n=200)
    top_30 = [num for num, _ in freq_counter.most_common(30)]

    if len(top_30) < 4:
        top_30 = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]  # fallback

    while True:
        selected_hot = random.sample(top_30, 4)
        remaining_pool = list(set(range(1, 46)) - set(selected_hot))
        selected_random = random.sample(remaining_pool, 2)
        candidate = sorted(selected_hot + selected_random)

        if is_valid(candidate):
            return {
                "numbers": candidate,
                "reason": "출현율 기반 AI 최적 조합",
                "date": datetime.now().strftime("%Y-%m-%d")
            }

def save_recommendation(round_num, numbers_list, rtype):
    if os.path.exists(RECOMMEND_FILE):
        with open(RECOMMEND_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    for item in numbers_list:
        entry = {
            "round": round_num,
            "numbers": item["numbers"],
            "type": rtype,
            "reason": item["reason"],
            "date": item.get("date", datetime.now().strftime("%Y-%m-%d"))
        }
        if "rank" in item:
            entry["rank"] = item["rank"]
        data.append(entry)

    with open(RECOMMEND_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_winning_numbers(round_num, numbers, bonus):
    if os.path.exists(WINNING_FILE):
        with open(WINNING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {}

    data[str(round_num)] = {
        "numbers": numbers,
        "bonus": bonus
    }

    with open(WINNING_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_recommendation_history():
    if os.path.exists(RECOMMEND_FILE):
        with open(RECOMMEND_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def load_winning_numbers():
    if os.path.exists(WINNING_FILE):
        with open(WINNING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def get_latest_round():
    data = load_winning_numbers()
    if isinstance(data, dict):
        numeric_keys = [int(k) for k in data.keys() if k.isdigit()]
        return max(numeric_keys) if numeric_keys else 1181
    elif isinstance(data, list):
        return max((item.get("round", 0) for item in data if isinstance(item, dict)), default=1181)
    return 1181

def get_result_rank(winning, candidate):
    win_numbers = winning.get("numbers", [])
    bonus = winning.get("bonus")
    matched = len(set(win_numbers) & set(candidate))
    if matched == 6:
        return "1등"
    elif matched == 5 and bonus in candidate:
        return "2등"
    elif matched == 5:
        return "3등"
    elif matched == 4:
        return "4등"
    elif matched == 3:
        return "5등"
    else:
        return "낙첨"

def fetch_latest_winning_numbers():
    return {
        "draw_no": 1181,
        "numbers": [8, 10, 14, 20, 33, 41],
        "bonus": 28
    }

def run_simulation(n=1000):
    winning_data = load_winning_numbers()
    latest_round = get_latest_round()
    winning = winning_data.get(str(latest_round), None)

    if not winning:
        print("❗ 최신 회차 당첨번호가 없습니다.")
        return

    print(f"🎯 기준 당첨 회차: {latest_round}")
    print(f"🏆 당첨번호: {winning['numbers']}, 보너스: {winning['bonus']}\n")

    results = []
    for _ in range(n):
        result = generate_ai_lotto()
        rank = get_result_rank(winning, result['numbers'])
        results.append(rank)

    counter = Counter(results)
    print(f"📊 시뮬레이션 {n}회 결과:")
    for rank, count in counter.items():
        print(f"  {rank}: {count}회 ({count/n*100:.2f}%)")

    return {
        "round": latest_round,
        "winning_numbers": winning["numbers"],
        "bonus": winning["bonus"],
        "total": n,
        "counts": dict(counter),
        "prob": {rank: (count / n * 100) for rank, count in counter.items()}
    }

def summarize_statistics():
    history = load_recommendation_history()
    stats = defaultdict(Counter)
    for record in history:
        method = record.get("type", "unknown")
        rank = record.get("rank", "정보 없음")
        stats[method][rank] += 1
    return stats

# ✅ 출현 빈도 계산 함수
def get_number_frequencies(n=100):
    history = load_recommendation_history()
    history = sorted(history, key=lambda x: x.get("round", 0), reverse=True)[:n]
    
    counter = Counter()
    for record in history:
        numbers = record.get("numbers", [])
        counter.update(numbers)

    return counter













