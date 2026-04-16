import json
from pathlib import Path
from app.db import run_select

sql = """
SELECT
    u.ID_user,
    u.username,
    u.password,
    COALESCE(SUM(CASE WHEN l.action = 'login' THEN 1 ELSE 0 END), 0) AS total_login
FROM userC u
LEFT JOIN user_log l ON l.user_id = u.ID_user
GROUP BY u.ID_user, u.username, u.password
ORDER BY total_login DESC;
"""

rows = run_select(sql)

data = [
]
for r in rows:
    data.append({
        "id_user": r[0],
        "username": r[1],
        "password": r[2],
        "total_login": int(r[3]) if r[3] > 0 else 0
    })
out_path = Path("output") / "user_log_with_stocks.json"
out_path.parent.mkdir(exist_ok=True)

out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding = "utf-8"
)
print(f"JSON salvat: {out_path}")