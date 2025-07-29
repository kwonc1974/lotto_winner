from flask import Flask, render_template, jsonify, request, redirect, url_for
import random
import os
from collections import Counter
from lotto_data import (
    load_winning_numbers,
    load_recommendation_history,
    get_result_rank,
    generate_hybrid_lotto,
    generate_smart_lotto,
    generate_ai_lotto,
    get_latest_round,
    save_recommendation,
    run_simulation,
    summarize_statistics  # 🔽 추가
)

app = Flask(__name__)

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

    next_round = get_latest_round() + 1
    save_recommendation(next_round, results, rtype)

    return jsonify(results=results)

@app.route('/results')
def results():
    recommendations = load_recommendation_history()
    winning_data = load_winning_numbers()

    result_list = []

    for item in recommendations:
        round_num = item.get('round')
        numbers = item.get('numbers', [])
        rtype = item.get('type', '알수없음')
        reason = item.get('reason', '')

        matched_winning = next(
            (entry for entry in winning_data if isinstance(entry, dict) and entry.get("round") == round_num),
            None
        )

        if matched_winning:
            rank = get_result_rank(matched_winning["numbers"], matched_winning["bonus"], numbers)
        else:
            latest_round = max((entry["round"] for entry in winning_data if isinstance(entry, dict)), default=0)
            if round_num > latest_round:
                rank = '미추첨'
            else:
                rank = '정보 없음'

        result_list.append({
            "round": round_num,
            "numbers": numbers,
            "type": rtype,
            "rank": rank,
            "reason": reason
        })

    result_list = sorted(result_list, key=lambda x: x["round"], reverse=True)

    return render_template('results.html', results=result_list)

@app.route('/clear', methods=['GET', 'POST'])
def clear():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == '123456':
            if os.path.exists('recommend_history.json'):
                os.remove('recommend_history.json')
            return redirect(url_for('clear_done'))
        else:
            return render_template('clear.html', error='비밀번호가 틀렸습니다.')
    return render_template('clear.html')

@app.route('/clear_done')
def clear_done():
    return render_template('clear_done.html')

@app.route('/simulation')
def simulation():
    try:
        result = run_simulation(n=1000)
    except Exception as e:
        result = None
        print(f"❌ 시뮬레이션 오류: {e}")

    return render_template("simulation.html", result=result)

# 📊 통계 페이지 추가
@app.route('/stats')
def stats():
    try:
        stats_data = summarize_statistics()
    except Exception as e:
        stats_data = {}
        print(f"❌ 통계 요약 오류: {e}")

    return render_template("stats.html", stats=stats_data)

if __name__ == '__main__':
    app.run(debug=True)












