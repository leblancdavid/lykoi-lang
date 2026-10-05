"""Reviewed synthetic observer; receives opening evidence, never sealed content."""
from pathlib import Path
import json


def observe(context):
    inputs = context['selection']
    row = json.loads(Path(inputs['opening_result']).read_bytes())
    return {'successful': row['state'] == 'OPENED' and row['accepted'] is True and
            row['opening_count'] == 1 and row['commitment'] == inputs['commitment'],
            'opening_count': row['opening_count'], 'commitment': row['commitment']}
