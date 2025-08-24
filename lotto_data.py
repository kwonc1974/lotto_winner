import json
import random
import os
from datetime import datetime
from collections import Counter, defaultdict

# 파일 경로
RECOMMEND_FILE = 'recommendation_history.json'
WINNING_FILE = 'winning_numbers.json'

# -----------------------------
# 공통 유효성 필터 (스마트 규칙)
# -----------------------------
def is_valid(numbers):
    nums = sorted(numbers)
    odd = sum(1 for n in nums if n % 2 == 1)
    low = sum(1 for n in nums if n <= 22)
    total = sum(nums)

    if not (2 <= odd <= 4):          # 홀짝 2~4
        return False
    if not (2 <= low <= 4):          # 저/고 2~4
        return False
    if not (120 <= total <= 160):    # 합계 범위
        return False

    # 연속 제한
    consecutive = 0
    for i in range(5):
        if nums[i] + 1 == nums[i + 1]:
            consecutive += 1
    if consecutive > 2:
        return False

    return True

# -----------------------------
# I/O 유틸
# -----------------------------
def _read_json(path, default):
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return default

def _write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_recommendation_history():
    return _read_json(RECOMMEND_FILE, [])

def load_winning_numbers():
    return _read_json(WINNING_FILE, {})

def save_recommendation(round_num, numbers_list, rtype):
    data = load_recommendation_history()
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
    _write_json(RECOMMEND_FILE, data)

def save_winning_numbers(round_num, numbers, bonus):
    data = load_winning_numbers()
    data[str(round_num)] = {"numbers": numbers, "bonus": bonus}
    _write_json(WINNING_FILE, data)

# -----------------------------
# 회차/결과 관련
# -----------------------------
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
    # 필요 시 외부 크롤링으로 교체
    return {"draw_no": 1181, "numbers": [8, 10, 14, 20, 33, 41], "bonus": 28}

# -----------------------------
# 빈도 계산
# -----------------------------
def get_number_frequencies(n=100):
    history = load_recommendation_history()
    history = sorted(history, key=lambda x: x.get("round", 0), reverse=True)[:n]
    counter = Counter()
    for record in history:
        counter.update(record.get("numbers", []))
    return counter

# -----------------------------
# 기존 개별 생성기 (호환 유지)
# -----------------------------
def generate_hybrid_lotto():
    freq_counter = get_number_frequencies(n=100)
    top_20 = [num for num, _ in freq_counter.most_common(20)]
    if len(top_20) < 3:
        top_20 = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]
    selected_hot = random.sample(top_20, 3)
    remaining = list(set(range(1, 46)) - set(selected_hot))
    selected_random = random.sample(remaining, 3)
    result = sorted(selected_hot + selected_random)
    return {"numbers": result, "reason": "출현율 상위 번호 + 무작위 조합", "date": datetime.now().strftime("%Y-%m-%d")}

def generate_smart_lotto():
    while True:
        candidate = random.sample(range(1, 46), 6)
        if is_valid(candidate):
            return {"numbers": sorted(candidate), "reason": "번호 균형 알고리즘 기반 필터링", "date": datetime.now().strftime("%Y-%m-%d")}

def generate_ai_lotto():
    freq_counter = get_number_frequencies(n=200)
    top_30 = [num for num, _ in freq_counter.most_common(30)]
    if len(top_30) < 4:
        top_30 = [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]
    while True:
        selected_hot = random.sample(top_30, 4)
        remaining = list(set(range(1, 46)) - set(selected_hot))
        selected_random = random.sample(remaining, 2)
        candidate = sorted(selected_hot + selected_random)
        if is_valid(candidate):
            return {"numbers": candidate, "reason": "출현율 기반 AI 최적 조합", "date": datetime.now().strftime("%Y-%m-%d")}

# -----------------------------
# ✅ 통합 엔진
#   (하이브리드 + 스마트 + AI 장점 결합)
# -----------------------------
def generate_unified_lotto():
    """
    전략:
      1) 최근 기록 빈도 상위(HOT)에서 3~4개 뽑기
      2) 나머지는 전체 풀에서 분산되게 채우기
      3) 스마트 필터(is_valid) 통과
      4) 중복/편향 방지를 위해 번호대(1~10/11~20/21~30/31~40/41~45) 분포 보정
    """
    freq = get_number_frequencies(n=200)
    hot = [num for num, _ in freq.most_common(30)] or [1, 3, 7, 10, 13, 17, 23, 27, 33, 38, 40, 44]

    # 번호 구간
    bands = [(1,10), (11,20), (21,30), (31,40), (41,45)]

    def fill_with_distribution(base):
        need = 6 - len(base)
        candidate_pool = list(set(range(1,46)) - set(base))
        # 구간별 한두 개씩 섞이게 샘플링
        picks = []
        random.shuffle(bands)
        for lo, hi in bands:
            band_nums = [x for x in candidate_pool if lo <= x <= hi and x not in picks]
            random.shuffle(band_nums)
            if band_nums:
                picks.append(band_nums[0])
                if len(picks) >= need:
                    break
        # 부족하면 아무거나 채우기
        if len(picks) < need:
            remain = list(set(candidate_pool) - set(picks))
            picks += random.sample(remain, need - len(picks))
        return sorted(base + picks)

    # 여러 시도에서 첫 통과안이 나올 때까지
    for _ in range(500):
        # 3~4개는 HOT에서
        k_hot = random.choice([3,4])
        chosen_hot = random.sample(hot, k_hot) if len(hot) >= k_hot else random.sample(range(1,46), k_hot)
        candidate = fill_with_distribution(chosen_hot)
        if is_valid(candidate):
            return {
                "numbers": sorted(candidate),
                "reason": "통합엔진(HOT+분포보정+스마트필터)",
                "date": datetime.now().strftime("%Y-%m-%d")
            }

    # 최악의 경우라도 반환
    fallback = sorted(random.sample(range(1,46), 6))
    return {
        "numbers": fallback,
        "reason": "통합엔진 Fallback",
        "date": datetime.now().strftime("%Y-%m-%d")
    }

# -----------------------------
# 시뮬레이션
# -----------------------------
def run_simulation(n=1000):
    winning_data = load_winning_numbers()
    latest_round = get_latest_round()
    winning = winning_data.get(str(latest_round))
    if not winning:
        print("❗ 최신 회차 당첨번호가 없습니다.")
        return

    results = []
    for _ in range(n):
        result = generate_ai_lotto()  # 시뮬은 기존 로직 유지
        rank = get_result_rank(winning, result['numbers'])
        results.append(rank)

    counter = Counter(results)
    return {
        "round": latest_round,
        "winning_numbers": winning["numbers"],
        "bonus": winning["bonus"],
        "total": n,
        "counts": dict(counter),
        "prob": {rank: (count / n * 100) for rank, count in counter.items()}
    }

# -----------------------------
# 통계 요약
# -----------------------------
def summarize_statistics():
    history = load_recommendation_history()
    stats = defaultdict(Counter)
    for record in history:
        method = record.get("type", "unknown")
        rank = record.get("rank", "정보 없음")
        stats[method][rank] += 1
    return stats
















