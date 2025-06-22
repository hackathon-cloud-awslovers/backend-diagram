import json
import re
import zlib
import base64
import requests

PLANTUML_SERVER = 'http://www.plantuml.com/plantuml/png/'

# ---- DSL Parser ----
def parse_entities(dsl: str):
    pattern = r"(\w+):\s*\{([^}]*)\}"
    matches = re.findall(pattern, dsl, re.MULTILINE | re.DOTALL)
    entities = []
    for name, body in matches:
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        shape = None
        fields = []
        for line in lines:
            if line.startswith('shape:'):
                shape = line.split(':', 1)[1].strip()
            else:
                m = re.match(r"(\w+):\s*(\w+)(?:\s*\{constraint:\s*(\w+)\})?", line)
                if m:
                    fname, ftype, constraint = m.groups()
                    fields.append({'name': fname, 'type': ftype, 'constraint': constraint})
        entities.append({'name': name, 'shape': shape, 'fields': fields})
    return entities


def parse_relations(dsl: str):
    rel_pattern = r"(\w+)\.(\w+)\s*->\s*(\w+)\.(\w+)"
    matches = re.findall(rel_pattern, dsl)
    relations = []
    for left_ent, left_field, right_ent, right_field in matches:
        relations.append({
            'left_entity': left_ent,
            'left_field': left_field,
            'right_entity': right_ent,
            'right_field': right_field
        })
    return relations

# ---- PlantUML encoding ----
def plantuml_encode(text: str) -> str:
    data = zlib.compress(text.encode('utf-8'))[2:-4]
    def encode6bit(b):
        if b < 10: return chr(48 + b)
        b -= 10
        if b < 26: return chr(65 + b)
        b -= 26
        if b < 26: return chr(97 + b)
        b -= 26
        if b == 0: return '-'
        if b == 1: return '_'
        return '?'
    def append3bytes(b1, b2, b3):
        c1 = b1 >> 2
        c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
        c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
        c4 = b3 & 0x3F
        return ''.join([encode6bit(c1), encode6bit(c2), encode6bit(c3), encode6bit(c4)])
    encoded = ''
    for i in range(0, len(data), 3):
        b1 = data[i]
        b2 = data[i+1] if i+1 < len(data) else 0
        b3 = data[i+2] if i+2 < len(data) else 0
        encoded += append3bytes(b1, b2, b3)
    return encoded

# ---- Lambda handler ----
def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        dsl = body.get('dsl', '')
        # Parse DSL
        entities = parse_entities(dsl)
        relations = parse_relations(dsl)
        # Build PlantUML
        lines = ['@startuml']
        for ent in entities:
            lines.append(f"entity {ent['name']} {{")
            for f in ent['fields']:
                prefix = '*' if f.get('constraint') == 'primary_key' else ''
                lines.append(f"  {prefix}{f['name']} : {f['type']}")
            lines.append('}\n')
        for rel in relations:
            lines.append(f"{rel['left_entity']}::{rel['left_field']} --> {rel['right_entity']}::{rel['right_field']}")
        lines.append('@enduml')
        puml = '\n'.join(lines)
        # Encode and fetch PNG
        encoded = plantuml_encode(puml)
        url = PLANTUML_SERVER + encoded
        resp = requests.get(url)
        resp.raise_for_status()
        png_b64 = base64.b64encode(resp.content).decode('utf-8')
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'pngBase64': png_b64})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
