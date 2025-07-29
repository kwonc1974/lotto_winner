import os
import sys
from datetime import datetime
import logging

from lotto_data import (
    fetch_latest_winning_numbers,
    save_winning_numbers,
    generate_ai_lotto,
    get_latest_round,
    save_recommendation,
    get_result_rank,
    load_winning_numbers
)

# 📁 로그 폴더 생성
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 📅 오늘 날짜 기준 로그 파일명
today_str = datetime.now().strftime("%Y-%m-%d")
log_filename = os.path.join(LOG_DIR, f"{today_str}_log.txt")

# 📝 로깅 설정 (한글/이모지 깨지지 않게 UTF-8 인코딩 포함!)
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"  # ✅ 요게 핵심!
)

def main():
    try:
        logging.info("🤖 자동 업데이트 시작")

        # 1. 최신 당첨번호 수집
        result = fetch_latest_winning_numbers()
        draw_no = result["draw_no"]
        numbers = result["numbers"]
        bonus = result["bonus"]

        logging.info(f"📢 최신 회차: {draw_no}, 번호: {numbers}, 보너스: {bonus}")

        # 2. 당첨번호 저장
        save_winning_numbers(draw_no, numbers, bonus)
        logging.info("✅ 당첨번호 저장 완료")

        # 3. AI 추천번호 생성 및 저장
        recs = []
        for _ in range(5):
            r = generate_ai_lotto()
            rank = get_result_rank(result, r["numbers"])
            r["rank"] = rank
            recs.append(r)

        save_recommendation(draw_no + 1, recs, rtype="ai")
        logging.info("✅ 추천번호 저장 완료")

        # 4. 추천번호 로그 출력
        for idx, r in enumerate(recs, 1):
            logging.info(f"추천 {idx}: {r['numbers']} → {r['rank']}")

        logging.info("🎉 자동 업데이트 완료")

    except Exception as e:
        logging.exception(f"❌ 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()







