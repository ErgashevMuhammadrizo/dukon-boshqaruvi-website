import json
from pathlib import Path
from django import template
register = template.Library()
CATALOG = json.loads((Path(__file__).resolve().parents[1] / 'translations.json').read_text())
@register.simple_tag(takes_context=True)
def t(context, key):
    row = CATALOG[str(key)]
    return row.get(context.get('language', 'uz'), row['uz'])
