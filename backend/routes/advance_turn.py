# backend/routes/advance_turn.py
from fastapi import APIRouter, Form, HTTPException
from db import get_db
from mqtt_client import publish_active

router = APIRouter()

def monster_health_description(c):
    try:
        current_hp = int(c["current_hp"])
        hp_max = int(c["hp_max"])
    except (TypeError, ValueError):
        return "Unknown"

    if hp_max <= 0:
        return "Unknown"

    pct = (current_hp / hp_max) * 100

    if pct > 80:
        return "Healthy"
    if pct > 50:
        return "Injured"
    if pct > 20:
        return "Bloodied"
    return "Near Death"


@router.post("/api/advance_turn")
def advance_turn(
    encounter_id: int = Form(...),
    combatant_count: int = Form(...)
):
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Fetch current state
    cur.execute("""
        SELECT current_turn_index, round
        FROM encounters
        WHERE id = %s
    """, (encounter_id,))
    encounter = cur.fetchone()

    if not encounter:
        raise HTTPException(404, "Encounter not found")

    current_turn = encounter["current_turn_index"] + 1
    round_num = encounter["round"]

    if current_turn >= combatant_count:
        current_turn = 0
        round_num += 1

    # Persist
    cur.execute("""
        UPDATE encounters
        SET current_turn_index = %s, round = %s
        WHERE id = %s
    """, (current_turn, round_num, encounter_id))

    # Fetch active combatant (for MQTT)
    cur.execute("""
        SELECT name, current_hp, hp_max, type
        FROM (
            -- PCs
            SELECT 
                a.name AS name,
                ea.current_hp AS current_hp,
                NULL AS hp_max,
                'pc' AS type,
                ea.initiative_roll
            FROM encounter_adventurers ea
            JOIN adventurers a ON a.id = ea.adventurer_id
            WHERE ea.encounter_id = %s

            UNION ALL

            -- Monsters
            SELECT 
                COALESCE(ec.instance_name, c.name) AS name,
                ec.current_hp AS current_hp,
                c.hp_max AS hp_max,
                'monster' AS type,
                ec.initiative_roll
            FROM encounter_creatures ec
            JOIN creatures c ON c.id = ec.creature_id
            WHERE ec.encounter_id = %s
        ) t
        ORDER BY initiative_roll DESC
        LIMIT 1 OFFSET %s
    """, (encounter_id, encounter_id, current_turn))

    active = cur.fetchone()
    if active:
        if active["type"] == "monster":
            hp_value = monster_health_description(active)
        else:
            hp_value = active["current_hp"]

        publish_active(active["name"], hp_value)


    return {
        "currentTurnIndex": current_turn,
        "round": round_num,
        "active_player_name": active["name"],
        "active_player_hp": active["current_hp"],
        "encounter_id": encounter_id,
        "combatant_count": combatant_count
    }
