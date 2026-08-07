import json

def sync_links(wf):
    """Sync links array ↔ node port link references.
    
    After modifying a workflow JSON, call this to ensure every link in the
    global `links` array has corresponding port-level references:
    - source_node.outputs[from_slot].links contains link_id
    - target_node.inputs[to_slot].link == link_id
    """
    nodes = {n['id']: n for n in wf['nodes']}
    
    # 1. Clear all existing port link references
    for n in wf['nodes']:
        for inp in n.get('inputs', []):
            if 'link' in inp:
                inp['link'] = None
        for out in n.get('outputs', []):
            if 'links' in out:
                out['links'] = []
    
    # 2. Re-apply from links array
    for l in wf['links']:
        lid, fn, fs, tn, ts, typ = l
        src = nodes.get(fn)
        dst = nodes.get(tn)
        if not src or not dst:
            continue
        if fs < len(src.get('outputs', [])):
            out_port = src['outputs'][fs]
            if 'links' not in out_port:
                out_port['links'] = []
            if lid not in out_port['links']:
                out_port['links'].append(lid)
        if ts < len(dst.get('inputs', [])):
            dst['inputs'][ts]['link'] = lid
    
    return wf


def validate_links(wf):
    """Validate all links reference existing nodes and valid slot indices."""
    nodes = {n['id']: n for n in wf['nodes']}
    errors = []
    for l in wf['links']:
        lid, fn, fs, tn, ts, typ = l
        if fn not in nodes:
            errors.append(f"link {lid}: from node {fn} not found")
            continue
        if tn not in nodes:
            errors.append(f"link {lid}: to node {tn} not found")
            continue
        fn_out = len(nodes[fn].get('outputs', []))
        tn_in = len(nodes[tn].get('inputs', []))
        if fs >= fn_out:
            errors.append(f"link {lid}: {fn}({nodes[fn]['type']}) slot {fs} >= {fn_out} outputs")
        if ts >= tn_in:
            errors.append(f"link {lid}: {tn}({nodes[tn]['type']}) slot {ts} >= {tn_in} inputs")
    return errors


if __name__ == '__main__':
    import sys
    for path in sys.argv[1:]:
        with open(path, encoding='utf-8') as f:
            wf = json.load(f)
        print(f"Processing: {path} ({len(wf['nodes'])} nodes, {len(wf['links'])} links)")
        wf = sync_links(wf)
        errors = validate_links(wf)
        if errors:
            print("ERRORS:")
            for e in errors:
                print(f"  {e}")
        else:
            print("  OK")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(wf, f, ensure_ascii=False, indent=2)
