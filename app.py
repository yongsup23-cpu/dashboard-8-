import json
import os
from datetime import datetime
from pathlib import Path

from flask import Flask, abort, jsonify, render_template, request
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

EDIT_PASSWORD = os.environ.get("EDIT_PASSWORD", "8454")
BASE_DIR = Path(__file__).resolve().parent
LOCAL_DB_PATH = BASE_DIR / "dashboard.db"

ITEMS = json.loads(r"""[{"no": 1, "opinion": "동절기 보양 시 화재위험으로 당직근무 강제(내한콘크리트 공법 적용)", "related": "건축공사관리팀, 기술견적팀", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "건축", "quarter": "3분기"}]}, {"no": 2, "opinion": "습식공사 물량 오차 커서 개선 필요(습식→건식)", "related": "건축공사관리팀, 기술견적팀", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "건축", "quarter": "4분기"}]}, {"no": 3, "opinion": "TBM 시 위험작업 관련 전파가 일 1회 한계성 존재(확대 필요)", "related": "건축공사관리팀, 토목공사관리팀", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "건축", "quarter": "2분기"}]}, {"no": 4, "opinion": "입주예정자 설계변경 동의서 우편 수령 → 누락 다수, 예산 과투입", "related": "DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "건축", "quarter": "4분기"}]}, {"no": 5, "opinion": "협력업체 사용 전기세 업체 부과 검토(낭비 원가 과도)", "related": "건축공사관리팀", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "건축", "quarter": "2분기"}]}, {"no": 6, "opinion": "매달 메일로 회신하는 예비비 현황조사를 KAUS 시스템 자동 표시로 개선", "related": "DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "토목플랜트", "quarter": "4분기"}]}, {"no": 7, "opinion": "도급기성 발주처 제출 내역서와 내부시스템 양식 상이하여 정확한 입력 어려움", "related": "DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "토목플랜트", "quarter": "4분기"}]}, {"no": 8, "opinion": "사업수지 예비비 현황 현재 매월 Excel로 전략기획팀 회신 → 시스템화 필요", "related": "전략기획팀, DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "주택", "quarter": "3분기"}]}, {"no": 9, "opinion": "간접비 지급 시마다 자금팀 별도 메일 송부 필요 → 자동화 검토", "related": "자금팀, DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "주택", "quarter": "4분기"}]}, {"no": 10, "opinion": "KAUS 상 옵션항목별 계약현황 금액 부가세 포함여부 미기재로 혼선 발생", "related": "DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "주택", "quarter": "1분기"}]}, {"no": 11, "opinion": "자금집행절차 카우스 시스템화 필요(외주/자재 자금집계 시스템 개발)", "related": "DI, 자금팀", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "구매품질환경", "quarter": "2분기"}]}, {"no": 12, "opinion": "하자처리 후 작업완료 확인서 날인 방식 변경(오프라인→핸드폰/태블릿)", "related": "DI", "category": "방어형 관성_업무처리 방식 관성", "depts": [{"dept": "AS", "quarter": "3분기"}]}, {"no": 13, "opinion": "아파트 커뮤니티 시설의 중요성 대두, 당사 담당자 부재", "related": "상품설계팀", "category": "방어형 관성_변화 대응 관성", "depts": [{"dept": "주택", "quarter": "하반기"}]}, {"no": 14, "opinion": "외국인 근로자 관리 강화 필요(모국어 교육 등)", "related": "안전", "category": "방어형 관성_변화 대응 관성", "depts": [{"dept": "안전", "quarter": "3분기"}]}, {"no": 15, "opinion": "많은 보고자료와 PPT 위주의 보여주기식 보고서 작성 문화 개선", "related": "전사", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "토목플랜트", "quarter": "3분기"}, {"dept": "주택", "quarter": "2분기"}]}, {"no": 16, "opinion": "시공관리 가이드북·표준시방서·표준시공상세도 등 매뉴얼 부족 개선", "related": "건축공사관리팀, 기전팀, AS팀", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "건축", "quarter": "3분기"}, {"dept": "기전", "quarter": "4분기"}, {"dept": "AS", "quarter": "2분기"}]}, {"no": 17, "opinion": "준공 후 현장 실적자료 등 참고 불가능 → 공유 체계 필요", "related": "건축공사관리팀", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "건축", "quarter": "3분기"}]}, {"no": 18, "opinion": "현장별 공사일보·업체 출력일보·검측 서류 양식 상이함 → 통일 필요", "related": "건축공사관리팀", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "건축", "quarter": "3분기"}]}, {"no": 19, "opinion": "품의서 작성 시 양식 공유 어려움 → 양식 공유 체계 필요", "related": "토목공사관리팀, 구매품질환경팀", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "토목플랜트", "quarter": "2분기"}, {"dept": "구매품질환경", "quarter": "2분기"}]}, {"no": 20, "opinion": "현장별 단가산출 자료 전산화 및 전체공유 필요", "related": "토목공사관리팀", "category": "과거 의존형 관성_보고·문서 관성", "depts": [{"dept": "토목플랜트", "quarter": "2분기"}]}, {"no": 21, "opinion": "현장별 예산 구간 적용 시 불평등 발생(499억 공사 500억 미만 구간 적용)", "related": "기술견적팀", "category": "과거 의존형 관성_의사결정 관성", "depts": [{"dept": "건축", "quarter": "4분기"}]}, {"no": 22, "opinion": "폐기물처리비 현실화: 면적 기준 과소 편성 → 비율 적용", "related": "기술견적팀", "category": "과거 의존형 관성_의사결정 관성", "depts": [{"dept": "건축", "quarter": "2분기"}]}, {"no": 23, "opinion": "함바 有 6,500원 / 無 7,000원 현실에 맞지 않는 단가 조정", "related": "기술견적팀", "category": "과거 의존형 관성_의사결정 관성", "depts": [{"dept": "건축", "quarter": "2분기"}]}, {"no": 24, "opinion": "안전화 지급 및 안전감시단(패트롤) 배치 기준 없음", "related": "안전보건팀", "category": "과거 의존형 관성_의사결정 관성", "depts": [{"dept": "건축", "quarter": "2분기"}]}, {"no": 25, "opinion": "중복품의 간소화(AS수행방안품의·집행품의 중복, 임시등록 품의 등)", "related": "건축공사관리팀, 토목공사관리팀, 구매품질환경팀, AS팀", "category": "과거 의존형 관성_의사결정 관성", "depts": [{"dept": "건축", "quarter": "4분기"}, {"dept": "토목플랜트", "quarter": "3분기"}]}, {"no": 26, "opinion": "업무 시간 중 잦은 호출·회의로 개별 집중 업무 시간 확보 어려움", "related": "주택", "category": "과거 의존형 관성_회의 관성", "depts": [{"dept": "주택", "quarter": "1분기"}]}, {"no": 27, "opinion": "사전 준비 없이 기계적인 회의 참석 문화 개선", "related": "안전", "category": "과거 의존형 관성_회의 관성", "depts": [{"dept": "안전", "quarter": "4분기"}]}, {"no": 28, "opinion": "매출·원가·직간접비 관리 사업주관팀·공사팀 이원화로 혼선", "related": "건축공사관리팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "건축", "quarter": "4분기"}]}, {"no": 29, "opinion": "주택본부 내 사업장 정보 통합 관리 필요", "related": "주택사업관리팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "주택", "quarter": "3분기"}]}, {"no": 30, "opinion": "현장 안전보건만이 아닌 관리감독자·협력회사 참여 필요", "related": "안전", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "안전", "quarter": "3분기"}]}, {"no": 31, "opinion": "지하주차장 중층 바닥방수 적용 필요(하부층 누수로 차량 오염 AS 다수)", "related": "건축공사관리팀, 기술견적팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "AS", "quarter": "2분기"}]}, {"no": 32, "opinion": "BS점검 시 인근 현장 건축직 직원 참여 및 결과 공유 필요", "related": "건축공사관리팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "AS", "quarter": "2분기"}]}, {"no": 33, "opinion": "현장 AS인수인계 기준 준수 및 잉여자재 추가 확보(도배·마루 등)", "related": "건축공사관리팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "AS", "quarter": "2분기"}]}, {"no": 34, "opinion": "본공사 시 시공담당자 책임실명제 도입(스마트공사관리시스템 활용)", "related": "건축공사관리팀", "category": "형식 중심형 관성_책임·협업 관성", "depts": [{"dept": "AS", "quarter": "3분기"}]}, {"no": 35, "opinion": "TBM 시 근로자들이 위험예지 이해 없이 작업사항 위주로 청취 → 개선", "related": "안전", "category": "형식 중심형 관성_커뮤니케이션 관성", "depts": [{"dept": "안전", "quarter": "2분기"}]}, {"no": 36, "opinion": "일방향적인 안전교육·소통문화 개선(쌍방향 소통 체계 구축)", "related": "안전", "category": "형식 중심형 관성_커뮤니케이션 관성", "depts": [{"dept": "안전", "quarter": "3분기"}]}, {"no": 37, "opinion": "결재 합의 시 종료 기한 없어 지연 발생 → 알람 기능 설정 필요", "related": "DI", "category": "반응형 관성_시간 운영 관성", "depts": [{"dept": "토목플랜트", "quarter": "3분기"}, {"dept": "주택", "quarter": "3분기"}]}, {"no": 38, "opinion": "견적기간 장기화에 따른 적기 사업성 검토 및 발주처 협의 난항", "related": "건축견적팀", "category": "반응형 관성_시간 운영 관성", "depts": [{"dept": "주택", "quarter": "4분기"}]}, {"no": 39, "opinion": "형식적 건수 채우기 안전지킴이 활동 → 합동 점검 등 개선", "related": "안전", "category": "반응형 관성_우선순위 판단 관성", "depts": [{"dept": "안전", "quarter": "2분기"}]}, {"no": 40, "opinion": "매달 위험성평가 과거 평가항목(DB)만 사용한 형식적 평가 개선", "related": "안전", "category": "반응형 관성_우선순위 판단 관성", "depts": [{"dept": "안전", "quarter": "2분기"}]}]""")

DEPTS = ["건축", "토목플랜트", "기전", "주택", "구매품질환경", "DI", "안전", "AS"]
QUARTER_ORDER = ["1분기", "2분기", "3분기", "4분기", "하반기", "제외"]
MONTH_KEYS = ["4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"]

app = Flask(__name__, template_folder=".")
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


def get_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL", "").strip()
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = "postgresql://" + database_url[len("postgres://"):]
        return database_url
    return f"sqlite:///{LOCAL_DB_PATH.as_posix()}"


engine = create_engine(
    get_database_url(),
    future=True,
    pool_pre_ping=True,
)


def require_password():
    if request.headers.get("X-Password") != EDIT_PASSWORD:
        return jsonify({"ok": False, "message": "관리자 비밀번호가 필요합니다."}), 403
    return None


def default_progress():
    return {m: {"text": "", "done": False} for m in MONTH_KEYS}


def normalize_progress(raw):
    data = default_progress()
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            raw = {}
    if isinstance(raw, dict):
        for m in MONTH_KEYS:
            value = raw.get(m, {})
            if isinstance(value, dict):
                data[m] = {
                    "text": str(value.get("text", "") or ""),
                    "done": bool(value.get("done", False)),
                }
    return data


def init_db():
    updated_at_type = "TIMESTAMP" if engine.dialect.name == "postgresql" else "TEXT"
    create_sql = f"""
        CREATE TABLE IF NOT EXISTS dashboard_rows (
            id TEXT PRIMARY KEY,
            no INTEGER NOT NULL,
            seq_no INTEGER NOT NULL,
            dept TEXT NOT NULL,
            quarter TEXT NOT NULL,
            opinion TEXT NOT NULL,
            related TEXT NOT NULL,
            category TEXT,
            multi_total INTEGER NOT NULL,
            multi_idx INTEGER NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            progress_json TEXT DEFAULT '',
            updated_at {updated_at_type}
        )
    """

    with engine.begin() as conn:
        conn.execute(text(create_sql))
        count = conn.execute(text("SELECT COUNT(*) FROM dashboard_rows")).scalar_one()

        if count == 0:
            seq_no = 0
            now = datetime.now().isoformat(timespec="seconds")
            for item in ITEMS:
                depts = item.get("depts", [])
                for idx, d in enumerate(depts):
                    seq_no += 1
                    row_id = f"{item['no']}_{d['dept']}"
                    conn.execute(
                        text("""
                            INSERT INTO dashboard_rows
                            (id, no, seq_no, dept, quarter, opinion, related, category, multi_total, multi_idx, done, progress_json, updated_at)
                            VALUES
                            (:id, :no, :seq_no, :dept, :quarter, :opinion, :related, :category, :multi_total, :multi_idx, :done, :progress_json, :updated_at)
                        """),
                        {
                            "id": row_id,
                            "no": item["no"],
                            "seq_no": seq_no,
                            "dept": d["dept"],
                            "quarter": d["quarter"],
                            "opinion": item["opinion"],
                            "related": item["related"],
                            "category": item.get("category", ""),
                            "multi_total": len(depts),
                            "multi_idx": idx,
                            "done": 0,
                            "progress_json": json.dumps(default_progress(), ensure_ascii=False),
                            "updated_at": now,
                        },
                    )
        else:
            rows = conn.execute(text("SELECT id, progress_json FROM dashboard_rows")).mappings().all()
            for row in rows:
                normalized = normalize_progress(row["progress_json"])
                conn.execute(
                    text("UPDATE dashboard_rows SET progress_json = :progress_json WHERE id = :id"),
                    {
                        "progress_json": json.dumps(normalized, ensure_ascii=False),
                        "id": row["id"],
                    },
                )


def row_to_dict(row):
    progress = normalize_progress(row["progress_json"])
    completed = sum(1 for v in progress.values() if v["done"])
    written = sum(1 for v in progress.values() if (v["text"] or "").strip())
    updated_at = row["updated_at"]
    updated_str = "" if updated_at is None else str(updated_at)

    return {
        "id": row["id"],
        "no": row["no"],
        "seqNo": row["seq_no"],
        "dept": row["dept"],
        "quarter": row["quarter"],
        "opinion": row["opinion"],
        "related": row["related"],
        "category": row["category"] or "",
        "multiTotal": row["multi_total"],
        "multiIdx": row["multi_idx"],
        "done": bool(row["done"]),
        "fileName": "",
        "hasFile": False,
        "downloadUrl": "",
        "updatedAt": updated_str,
        "progress": progress,
        "progressDoneCount": completed,
        "progressWrittenCount": written,
    }


def sorted_rows_query():
    dept_case = "CASE dept " + " ".join([f"WHEN '{d}' THEN {i}" for i, d in enumerate(DEPTS, start=1)]) + " ELSE 99 END"
    quarter_case = "CASE quarter " + " ".join([f"WHEN '{q}' THEN {i}" for i, q in enumerate(QUARTER_ORDER, start=1)]) + " ELSE 99 END"
    return text(f"SELECT * FROM dashboard_rows ORDER BY {dept_case}, {quarter_case}, seq_no ASC")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/state")
def api_state():
    with engine.connect() as conn:
        rows = conn.execute(sorted_rows_query()).mappings().all()
    return jsonify({"rows": [row_to_dict(r) for r in rows], "serverTime": datetime.now().isoformat(timespec="seconds")})


@app.route("/api/update_row", methods=["POST"])
def api_update_row():
    pw_error = require_password()
    if pw_error:
        return pw_error

    data = request.get_json(silent=True) or {}
    row_id = data.get("id")
    if not row_id:
        return jsonify({"ok": False, "message": "id가 없습니다."}), 400

    fields = []
    params = {"id": row_id}

    if "quarter" in data:
        quarter = data["quarter"]
        if quarter not in QUARTER_ORDER:
            return jsonify({"ok": False, "message": "개선기한 값이 올바르지 않습니다."}), 400
        fields.append("quarter = :quarter")
        params["quarter"] = quarter

    if "done" in data:
        fields.append("done = :done")
        params["done"] = 1 if data["done"] else 0

    if not fields:
        return jsonify({"ok": False, "message": "변경할 값이 없습니다."}), 400

    fields.append("updated_at = :updated_at")
    params["updated_at"] = datetime.now().isoformat(timespec="seconds")

    try:
        with engine.begin() as conn:
            result = conn.execute(
                text(f"UPDATE dashboard_rows SET {', '.join(fields)} WHERE id = :id"),
                params,
            )
            if result.rowcount == 0:
                return jsonify({"ok": False, "message": "대상을 찾지 못했습니다."}), 404

            row = conn.execute(
                text("SELECT * FROM dashboard_rows WHERE id = :id"),
                {"id": row_id},
            ).mappings().first()

        return jsonify({"ok": True, "row": row_to_dict(row)})
    except SQLAlchemyError as e:
        return jsonify({"ok": False, "message": f"저장 중 DB 오류가 발생했습니다: {e}"}), 500


@app.route("/api/progress/<row_id>", methods=["POST"])
def api_progress(row_id):
    pw_error = require_password()
    if pw_error:
        return pw_error

    try:
        data = request.get_json(silent=True) or {}
        progress = normalize_progress(data.get("progress", {}))

        with engine.begin() as conn:
            row = conn.execute(
                text("SELECT * FROM dashboard_rows WHERE id = :id"),
                {"id": row_id},
            ).mappings().first()
            if not row:
                return jsonify({"ok": False, "message": "대상을 찾지 못했습니다."}), 404

            result = conn.execute(
                text("""
                    UPDATE dashboard_rows
                    SET progress_json = :progress_json, updated_at = :updated_at
                    WHERE id = :id
                """),
                {
                    "progress_json": json.dumps(progress, ensure_ascii=False),
                    "updated_at": datetime.now().isoformat(timespec="seconds"),
                    "id": row_id,
                },
            )
            if result.rowcount == 0:
                return jsonify({"ok": False, "message": "진행상황 저장에 실패했습니다."}), 500

            row = conn.execute(
                text("SELECT * FROM dashboard_rows WHERE id = :id"),
                {"id": row_id},
            ).mappings().first()

        return jsonify({"ok": True, "row": row_to_dict(row), "message": "저장되었습니다."})
    except SQLAlchemyError as e:
        return jsonify({"ok": False, "message": f"저장 중 DB 오류가 발생했습니다: {e}"}), 500
    except Exception as e:
        return jsonify({"ok": False, "message": f"저장 중 오류가 발생했습니다: {e}"}), 500


@app.route("/api/upload/<row_id>", methods=["POST"])
def api_upload(row_id):
    return jsonify({"ok": False, "message": "증빙자료 기능은 사용하지 않습니다."}), 400


@app.route("/api/file/<row_id>", methods=["DELETE"])
def api_delete_file(row_id):
    return jsonify({"ok": False, "message": "증빙자료 기능은 사용하지 않습니다."}), 400


@app.route("/download/<row_id>")
def download_file(row_id):
    abort(404)


@app.route("/api/reset", methods=["POST"])
def api_reset():
    pw_error = require_password()
    if pw_error:
        return pw_error

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM dashboard_rows"))

    init_db()
    return jsonify({"ok": True})


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
