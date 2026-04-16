import json
from pathlib import Path
from app.db import run_select

sql = """
SELECT 
    u.action,
    COUNT(*) AS numar_actiuni,
    COUNT(*) / COUNT(DISTINCT u.user_id) AS medie_actiuni_per_user,
    COALESCE(SUM(CASE WHEN u.action = 'login' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_LOGINS,
    COALESCE(SUM(CASE WHEN u.action = 'logout' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_LOGOUTS,
    COALESCE(SUM(CASE WHEN u.action = 'programare_creata' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_BOOKINGS,
    COALESCE(SUM(CASE WHEN u.action = 'programare_anulata' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_C_BOOKINS,
    COALESCE(SUM(CASE WHEN u.action = 'feedback_adaugat' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_FEEDBACKS,
    COALESCE(SUM(CASE WHEN u.action = 'abonament_cumparat' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_SUBSCRIPTIONS,
    COALESCE(SUM(CASE WHEN u.action = 'abonament_anulat' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_C_SUBSCRIPTIONS,
    COALESCE(SUM(CASE WHEN u.action = 'plata_efectuata' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_PAYMENTS,
    COALESCE(SUM(CASE WHEN u.action = 'refund_plata' THEN 1 ELSE 0 END), 0) / MAX(u.ID_client) AS medie_REFUNDS
FROM user_log u
GROUP BY u.action
ORDER BY numar_actiuni DESC;
"""

rows = run_select(sql)

data = [
]
for r in rows:
    data.append({
        "actiune": r[0],
        "nr_actiuni_totale": r[1],
        "medie_actiuni_per_user": float(r[2]),
        "medie_totala_LOGINS": float(r[3]) if r[3] > 0 else "-",
        "medie_totala_LOGOUTS": float(r[4]) if r[4] > 0 else "-",
        "medie_totala_BOOKINGS": float(r[5]) if r[5] > 0 else "-",
        "medie_totala_C_BOOKINS": float(r[6]) if r[6] > 0 else "-",
        "medie_totala_FEEDBACKS": float(r[7]) if r[7] > 0 else "-",
        "medie_totala_SUBSCRIPTIONS": float(r[8]) if r[8] > 0 else "-",
        "medie_totala_C_SUBSCRIPTIONS": float(r[9]) if r[9] > 0 else "-",
        "medie_totala_PAYMENTS": float(r[10]) if r[10] > 0 else "-",
        "medie_totala_REFUNDS": float(r[11]) if r[11] > 0 else "-",
    })

out_path = Path("output") / "actions_stats.json"
out_path.write_text(
    json.dumps(data, indent=2, ensure_ascii=False),
    encoding = "utf-8"
)
print(f"JSON salvat: {out_path}")

