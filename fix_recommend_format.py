import json

OLD_FILE = 'recommend_history.json'
NEW_FILE = 'recommend_history.json'  # 덮어쓰기 할 경우 동일한 파일 이름

def convert_recommend_format():
    try:
        with open(OLD_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)

        # 새로운 리스트 형식으로 변환
        new_data = []
        for round_str, entries in old_data.items():
            round_num = int(round_str)
            for entry in entries:
                numbers = entry.get('numbers', [])
                new_data.append({
                    "round": round_num,
                    "numbers": numbers,
                    "type": "hybrid"  # 또는 smart / ai 로 구분 가능하면 바꿔줘
                })

        # 덮어쓰기 저장
        with open(NEW_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_data, f, ensure_ascii=False, indent=2)

        print("✅ recommend_history.json 변환 완료!")
    
    except Exception as e:
        print(f"❌ 변환 중 오류 발생: {e}")

if __name__ == '__main__':
    convert_recommend_format()
