def norm(s): return ' '.join(str(s or '').lower().split())
def handle_natural_intent_v108_122(user_message):
    t=norm(user_message)
    if t in {'v122 status','mega status','evolution status'}:
        import seed_v108_122_systems as s; print(s.status()); return 'handled'
    if t in {'proactive tick','seed check in'}:
        import seed_proactive_rhythm_v108 as p; print(p.tick()); return 'handled'
    return None
