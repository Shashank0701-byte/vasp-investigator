"""Reports are rendered exclusively from stored structured evidence."""


def report(case):
    a = case["analysis"]
    m = a["metrics"]
    lines = [
        f"# Investigation {case['id']}",
        "",
        case["title"],
        "",
        f"- Evidence mode: {a['mode'].upper()}",
        f"- Target: {a['target']}",
        f"- Network: {a['chain']}",
        f"- Created: {case['created_at']}",
        f"- Evidence digest (SHA-256): {case['evidence_digest']}",
        f"- Model version: {a['model_version']}",
        f"- Period: {a['period']['start']} to {a['period']['end']}",
        "",
        "## Fund flow",
        f"Gross outgoing valued transfers: ${m['outgoing_usd']:,.2f}.",
        f"Modelled value reaching VASP endpoints: ${m['attributed_usd']:,.2f}.",
        f"Unresolved or boundary-stopped value: ${m['unresolved_usd']:,.2f}.",
        f"Valuation coverage: {m['valuation_coverage']}% of outgoing transfers.",
        f"Graph: {len(a['graph']['nodes'])} nodes; {len(a['graph']['edges'])} transfers; tracing limit {a['max_hops']} hops.",
        "",
        "## Ranked VASP candidates",
    ]
    for c in a["candidates"]:
        lines += [
            f"### {c['entity']} — {c['score']}/100 attribution confidence",
            f"Modelled exposure: ${c['traced_usd']:,.2f} ({c['value_share']}% of valued gross outflow).",
            f"Supporting paths: {c['path_count']}; edge-disjoint support: {c['independent_paths']}; shortest/median distance: {c['shortest_hops']}/{c['median_hops']} hops.",
            f"Evidence quality cap: {c['quality_cap']}/100.",
        ]
        lines += [
            f"- {k}: {v['value']}/100 × {v['weight']} = {v['points']} points"
            for k, v in c["components"].items()
        ]
        lines += [
            f"- Label inference: {label['address']} → {label['entity']}; {label['strength']}; source: {label['source']}; observed {label['observed_at']}"
            for label in c["labels"]
        ]
        lines += [f"- Supporting path: {' → '.join(p)}" for p in c["paths"]]
    if not a["candidates"]:
        lines += ["No supported VASP candidate was found in the supplied evidence."]
    lines += ["", f"## Risk indicators — {a['risk']['score']}/100"]
    for r in a["risk"]["factors"]:
        lines += [
            f"- {r['name']} (+{r['points']}): {r['explanation']}",
            f"  Evidence: {', '.join(r['evidence_ids'])}",
        ]
    lines += ["", "## Suggested routing"]
    if a["mode"] == "demo":
        lines += [
            "Demonstration only. Do not send any disclosure or freezing request based on synthetic evidence."
        ]
    elif a["candidates"]:
        lines += [
            f"Review {a['candidates'][0]['entity']} as the first potential service contact. Independently validate labels, evidence and the appropriate authorized contact before considering a request. No request has been generated or sent."
        ]
    else:
        lines += ["Insufficient evidence to suggest a VASP contact."]
    lines += ["", "## Transaction evidence"]
    for t in a["transactions"]:
        lines += [
            f"- {t['id']} | {t['timestamp']} | {t['from_address']} → {t['to_address']} | {t['amount']} {t['asset']} | block {t['block_number']} | source: {t['source']}"
        ]
    lines += ["", "## Limitations and uncertainty"] + [
        f"- {s}" for s in a["limitations"]
    ]
    return "\n".join(lines) + "\n"
