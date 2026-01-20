# backend/routes/advance_turn.py
from fastapi import APIRouter, Form, HTTPException
from db import get_db
from mqtt_client import publish_active

router = APIRouter()

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
        SELECT name, current_hp
        FROM (
            SELECT ea.current_hp, a.name, ea.initiative_roll
            FROM encounter_adventurers ea
            JOIN adventurers a ON a.id = ea.adventurer_id
            WHERE ea.encounter_id = %s
            UNION ALL
            SELECT ec.current_hp, COALESCE(ec.instance_name, c.name), ec.initiative_roll
            FROM encounter_creatures ec
            JOIN creatures c ON c.id = ec.creature_id
            WHERE ec.encounter_id = %s
        ) t
        ORDER BY initiative_roll DESC
        LIMIT 1 OFFSET %s
    """, (encounter_id, encounter_id, current_turn))

    active = cur.fetchone()
    if active:
        publish_active(active["name"], active["current_hp"])

    return {
        "currentTurnIndex": current_turn,
        "round": round_num
    }
