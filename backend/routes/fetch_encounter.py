# backend/routes/encounter.py
from fastapi import APIRouter, Query, HTTPException
from db import get_db

router = APIRouter()

@router.get("/api/fetch_encounter")
def fetch_encounter(id: int = Query(...)):
    db = get_db()
    cur = db.cursor(dictionary=True)

    # Fetch encounter meta
    cur.execute("""
        SELECT current_turn_index, round
        FROM encounters
        WHERE id = %s
    """, (id,))
    encounter = cur.fetchone()

    if not encounter:
        raise HTTPException(status_code=404, detail="Encounter not found")

    # Fetch PCs
    cur.execute("""
        SELECT
            ea.id AS encounter_combatant_id,
            'pc' AS type,
            a.name,
            a.class,
            a.level,
            a.ac,
            ea.current_hp AS hp,
            a.hp_max AS max_hp,
            ea.initiative_roll AS initiative,
            ea.downed
        FROM encounter_adventurers ea
        JOIN adventurers a ON a.id = ea.adventurer_id
        WHERE ea.encounter_id = %s
    """, (id,))
    pcs = cur.fetchall()

    # Fetch Monsters
    cur.execute("""
        SELECT
            ec.id AS encounter_combatant_id,
            'monster' AS type,
            COALESCE(ec.instance_name, c.name) AS name,
            NULL AS class,
            NULL AS level,
            c.ac,
            ec.current_hp AS hp,
            c.hp_max AS max_hp,
            ec.initiative_roll AS initiative,
            ec.is_defeated
        FROM encounter_creatures ec
        JOIN creatures c ON c.id = ec.creature_id
        WHERE ec.encounter_id = %s
    """, (id,))
    monsters = cur.fetchall()

    # Fetch conditions
    cur.execute("""
        SELECT
            cc.encounter_adventurer_id,
            cc.encounter_creature_id,
            cond.name,
            cc.duration
        FROM combatant_conditions cc
        JOIN conditions cond ON cond.id = cc.condition_id
    """)
    conditions = cur.fetchall()

    # Attach conditions to combatants
    def attach_conditions(combatants, conditions, key):
        for c in combatants:
            c["conditions"] = []  # ALWAYS initialize

            cid = c["encounter_combatant_id"]
            for cond in conditions:
                if cond[key] is not None and cond[key] == cid:
                    c["conditions"].append({
                        "name": cond["name"],
                        "duration": cond["duration"]
                    })

    attach_conditions(pcs, conditions, 'encounter_adventurer_id')
    attach_conditions(monsters, conditions, 'encounter_creature_id')

    # Merge and sort by initiative
    combatants = pcs + monsters
    combatants.sort(key=lambda c: c.get("initiative") or 0, reverse=True)

    return {
        "round": encounter["round"],
        "currentTurnIndex": encounter["current_turn_index"],
        "combatants": combatants
    }
