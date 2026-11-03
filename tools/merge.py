import json, re, sys, collections

CATS = [
    ("hot", "요즘 이슈", "", ["hot"]),
    ("food", "음식", "🍜", ["food"]),
    ("love", "연애·관계", "💘", ["love_general", "love_spicy"]),
    ("fantasy", "초능력·상상", "🦸", ["fantasy"]),
    ("daily", "일상·습관", "🛋️", ["daily"]),
    ("gross", "극한·더러움", "🤢", ["gross"]),
    ("money", "돈·현실", "💸", ["money"]),
    ("work", "학교·직장", "🏫", ["work"]),
]

def norm(s):
    return re.sub(r"[\s\W_]+", "", s)

def grams(s):
    s = norm(s)
    return {s[i:i+2] for i in range(len(s) - 1)} or {s}

def jacc(x, y):
    return len(x & y) / max(1, len(x | y))

out_q, cats, report = [], [], []
for cid, name, emoji, files in CATS:
    items = []
    for f in files:
        try:
            items += json.load(open(f"data/{f}.json", encoding="utf-8"))
        except FileNotFoundError:
            report.append(f"MISSING {f}")
    kept, keys, gs = [], set(), []
    dropped = 0
    for it in items:
        a, b = str(it.get("a", "")).strip(), str(it.get("b", "")).strip()
        lv = int(it.get("level", 1)) if str(it.get("level", 1)).isdigit() else 1
        lv = min(3, max(1, lv))
        if not a or not b or norm(a) == norm(b) or len(a) > 60 or len(b) > 60:
            dropped += 1; continue
        k = tuple(sorted((norm(a), norm(b))))
        if k in keys:
            dropped += 1; continue
        g = grams(a + "|" + b); g2 = grams(b + "|" + a)
        if any(jacc(g, h) >= 0.75 or jacc(g2, h) >= 0.75 for h in gs):
            dropped += 1; continue
        keys.add(k); gs.append(g)
        kept.append((str(it.get("sub", "기타")).strip()[:16] or "기타", a, b, lv))
    for i, (sub, a, b, lv) in enumerate(kept, 1):
        out_q.append([f"{cid}-{i:04d}", cid, sub, a, b, lv])
    lvc = collections.Counter(x[3] for x in kept)
    cats.append({"id": cid, "name": name, "emoji": emoji})
    report.append(f"{name}: {len(items)} -> {len(kept)} (drop {dropped}) levels {dict(sorted(lvc.items()))}")

json.dump({"cats": cats, "q": out_q}, open("questions.json", "w", encoding="utf-8"),
          ensure_ascii=False, separators=(",", ":"))
print("\n".join(report)); print("TOTAL", len(out_q))
