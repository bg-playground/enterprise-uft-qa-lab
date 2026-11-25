"""Validate offline evidence structure and internal consistency, not server ingestion."""
def validate(payload):
    rows=payload['cases']
    summary=payload['finish']['summary']
    allowed=('passed','failed','skipped')
    ids=set()
    for row in rows:
        external_id=row['external_id']
        if not isinstance(external_id,str) or not external_id.strip() or external_id in ids:
            raise ValueError('invalid or duplicate external_id')
        ids.add(external_id)
        if row['outcome'] not in allowed or type(row['duration_ms']) is not int or row['duration_ms']<0:
            raise ValueError('invalid case outcome or duration')
        if not row['title'] or not all(isinstance(x,str) and x.strip() for x in row['requirement_external_ids']):
            raise ValueError('invalid title or requirement reference')
        if row['auto_register_requirements'] is not False:
            raise ValueError('registration must remain disabled')
    counts={k:sum(row['outcome']==k for row in rows) for k in allowed}
    if summary!={'total':len(rows),**counts}:
        raise ValueError('summary mismatch')
    if payload['finish']['status']=='passed' and (not counts['passed'] or counts['failed']):
        raise ValueError('invalid passing status')
    if payload['finish']['status'] not in ('passed','failed','aborted'):
        raise ValueError('invalid terminal status')
    if not payload['session']['runner']:
        raise ValueError('runner identity missing')
