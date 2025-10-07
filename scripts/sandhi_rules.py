# scripts/sandhi_rules.py
"""
Enhanced reverse-sandhi candidate generator.

This is a pragmatic, engineer-friendly reverse-sandhi implementation that covers
the common Sanskrit sandhi patterns (vowel sandhi, visarga, anusvara, simple
consonant assimilation) and produces scored candidate decompositions.

It's intentionally conservative: each rule is applied only where it is plausibly
triggered, and the number of output candidates is limited. Use a lexicon (data/lexicon.txt)
to improve ranking — a small lexicon dramatically improves output quality.

Functions:
- gen_candidates(line, k=8, lexicon_path=None, allow_aggressive=False)
    returns a list of dicts: {'cand': candidate_text, 'score': numeric, 'rules': [applied_rules]}
"""
import re
from typing import List, Dict, Tuple
from math import exp
from pathlib import Path

# Helper: load lexicon (one token per line). Returns set of strings.
def load_lexicon(path: str = "data/lexicon.txt"):
    p = Path(path)
    if not p.exists():
        return set()
    with p.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

# Default small lexicon to bootstrap (you can expand data/lexicon.txt later)
DEFAULT_LEXICON = {
    'राम', 'रामः', 'रामो', 'सीता', 'सीतायै', 'सीताम्', 'कृष्ण', 'कृष्णः', 'गुरु',
    'शिष्य', 'विद्या', 'धर्म', 'धर्मः', 'सत्यम्', 'अहम्', 'पाण्डव', 'हनुमान', 'लङ्का',
    'अर्जुन', 'भीम', 'गद', 'वेद', 'ज्ञान', 'शिव', 'शिवः', 'लोका', 'सुख', 'बलवान्',
    'अस्ति', 'गच्छति', 'व्रज', 'गगन', 'सागर', 'नम:"'  # last entry placeholder
}

# --- RULES (reverse mappings)
# Each rule is (pattern, replacement(s), rule_name, score_penalty)
# pattern is a regex matched against the whole line (or part), replacement(s) produce candidate string(s).
# For reverse-sandhi we look for the *merged* form and produce split forms.

# Utility to produce multiple replacements for a single match.
def apply_subs_once(text: str, subs: List[Tuple[str,str]]) -> List[Tuple[str,List[str]]]:
    """Apply each regex sub once (global) and return list of (candidate, [rule_names])"""
    out = []
    for pat, repl, name in subs:
        if re.search(pat, text):
            cand = re.sub(pat, repl, text)
            out.append((cand, [name]))
    return out

# Core reverse-sandhi transformations (conservative)
# NOTE: these are intentionally not exhaustive; they cover the most common merges.
REVERSE_RULES = [
    # VOWEL SAVARNA-DIRGHA: ā (ा) from a + a  => split ā -> अ + अ
    (r'ा', r'अअ', 'savarṇa-dīrgha'),
    # GUṆA/VYAR: e (े) commonly from a + i  OR from ai (but conservatively split to अ+इ)
    (r'े', r'अइ', 'a+i -> e (guṇa/saṃyoga reverse)'),
    # o (ो) commonly from a + u
    (r'ो', r'अउ', 'a+u -> o'),
    # ī/ū (ी/ू) could be from i+i or u+u (rare) — conservative: split to इइ/उउ
    (r'ी', r'इइ', 'ī -> i+i (conservative)'),
    (r'ू', r'उउ', 'ū -> u+u (conservative)'),
    # visarga-based: place spaces around visarga to separate words (helps syllabify)
    (r'ः', r' ः ', 'visarga-space'),
    # anusvāra spacing: keeps nasal explicit for later mapping
    (r'ं', r' ं ', 'anusvara-space'),
    # avagraha: replace avagraha with space (split words)
    (r'ऽ', r' ', 'avagraha-split'),
    # common contraction: "न्" + "द" -> "न्द" etc. (simple conservative approach: space double consonants)
    # We'll split obvious doubled consonants by inserting a space between repeating consonants
    (r'([क-ह])\1', r'\1 \1', 'double-consonant-split'),
    # Long vowel fallback: replace 'ौ' and 'ै' into possible splits (au, ai)
    (r'ौ', r'अउ', 'au -> a+u (reverse)'),
    (r'ै', r'अइ', 'ai -> a+i (reverse)'),
]

# More advanced patterns (context-aware) as functions.
def reverse_vowel_sandhi_variants(text: str) -> List[Tuple[str,str]]:
    """
    Generate several plausible reverse-splits for vowel sandhi occurrences.
    Returns list of (candidate_text, rule_name).
    """
    variants = []
    # e -> a + i  OR -> a + ī (both plausible). We include both with slightly different names.
    if 'े' in text:
        variants.append((text.replace('े', 'अइ'), 'e->a+i'))
        variants.append((text.replace('े', 'अी'), 'e->a+ī'))
    if 'ो' in text:
        variants.append((text.replace('ो', 'अउ'), 'o->a+u'))
        variants.append((text.replace('ो', 'अू'), 'o->a+ū'))
    if 'ौ' in text:
        variants.append((text.replace('ौ', 'अउ'), 'au->a+u'))
    if 'ै' in text:
        variants.append((text.replace('ै', 'अइ'), 'ai->a+i'))
    # Long A broken into a+a
    if 'ा' in text:
        variants.append((text.replace('ा', 'अअ'), 'ā->a+a'))
    return variants

def reverse_visarga_variants(text: str) -> List[Tuple[str,str]]:
    """
    Attempt conservative visarga reversals:
    - If word contains 'ः' (visarga), try leaving it and try replacing neighboring consonant patterns.
    - If final char is a dental or sibilant, consider inserting visarga before it etc.
    """
    variants = []
    # simply space around visarga done elsewhere; also try replacing 'ः' with 'स' or 'श' or 'त' where sensible
    if 'ः' in text:
        # insert space done earlier; also try replacing visarga with 'स् ' at end of a token
        variants.append((text.replace('ः', 'स् '), 'visarga->s + space (conservative)'))
        variants.append((text.replace('ः', 'त् '), 'visarga->t + space (conservative)'))
    return variants

def reverse_anusvara_variants(text: str) -> List[Tuple[str,str]]:
    """
    Expand anusvara (ं) into probable nasal consonants depending on context; conservative set:
    - before velars -> ङ् (ṅ)
    - before palatals -> ञ् (ñ)
    - before retroflex -> ण् (ṇ)
    - before dentals -> न् (n)
    - before labials -> म् (m)
    We'll implement a heuristic based on next character if present.
    """
    variants = []
    # find pattern: something like 'XंY' or 'ंY' and expand
    for m in re.finditer(r'ं(?=\s*.)', text):
        idx = m.start()
        # next char (if any)
        nxt = text[idx+1] if idx+1 < len(text) else ''
        # map groups (rough)
        if nxt in 'कखगघङ':
            variants.append((text[:idx] + 'ङ्' + text[idx+1:], 'anusvara->ṅ (velar)'))
        elif nxt in 'चछजझञ':
            variants.append((text[:idx] + 'ञ्' + text[idx+1:], 'anusvara->ñ (palatal)'))
        elif nxt in 'टठडढण':
            variants.append((text[:idx] + 'ण्' + text[idx+1:], 'anusvara->ṇ (retroflex)'))
        elif nxt in 'तथदधन':
            variants.append((text[:idx] + 'न्' + text[idx+1:], 'anusvara->n (dental)'))
        elif nxt in 'पफबभम':
            variants.append((text[:idx] + 'म्' + text[idx+1:], 'anusvara->m (labial)'))
        else:
            # general split: replace ं with ' ' + 'ं' (spacing) to separate words
            variants.append((text.replace('ं', ' ं '), 'anusvara->space'))
    return variants

# Conservative consonant-sandhi reverse heuristics: split common conjunct merges
def reverse_consonant_sandhi(text: str) -> List[Tuple[str,str]]:
    variants = []
    # common merging: t + r -> tr (no change) — skip
    # handle cases where visarga transformed to s/ś/t etc. -> we try to re-insert visarga if plausible
    # Also try splitting obvious conjunct clusters by inserting space before last consonant cluster
    # e.g., 'व्रज' might be 'व्र ज' or 'व रज' — both are possibilities but we prefer word-boundary insertion.
    # We'll conservative insert a space before consonant clusters of length >=2
    for m in re.finditer(r'([क-ह]{2,})', text):
        span = m.span()
        i = span[0]
        # insert a space before the conjunct (if not at start)
        if i > 0:
            cand = text[:i] + ' ' + text[i:]
            variants.append((cand, 'consonant-cluster-split'))
    return variants

# Compose all rule applications (one-step expansions)
def _one_step_candidates(text: str, lexicon:set) -> List[Dict]:
    """
    Apply each reverse rule once (single-step) and return scored candidates.
    We create candidates from:
      - direct regex replacements (REVERSE_RULES)
      - vowel/visarga/anusvara specific variants
      - consonant-cluster splits
    """
    out = []
    seen = set()

    # apply simple regex rules
    subs = [(pat, repl, name) for (pat, repl, name) in REVERSE_RULES]
    for pat, repl, name in subs:
        if re.search(pat, text):
            cand = re.sub(pat, repl, text)
            if cand not in seen:
                seen.add(cand)
                score = _baseline_score(text, cand, name, lexicon)
                out.append({'cand': cand, 'score': score, 'rules': [name]})

    # vowel sandhi variants
    for cand, rn in reverse_vowel_sandhi_variants(text):
        if cand not in seen:
            seen.add(cand)
            score = _baseline_score(text, cand, rn, lexicon)
            out.append({'cand': cand, 'score': score, 'rules': [rn]})

    # visarga variants
    for cand, rn in reverse_visarga_variants(text):
        if cand not in seen:
            seen.add(cand)
            score = _baseline_score(text, cand, rn, lexicon)
            out.append({'cand': cand, 'score': score, 'rules': [rn]})

    # anusvara variants
    for cand, rn in reverse_anusvara_variants(text):
        if cand not in seen:
            seen.add(cand)
            score = _baseline_score(text, cand, rn, lexicon)
            out.append({'cand': cand, 'score': score, 'rules': [rn]})

    # consonant cluster splits
    for cand, rn in reverse_consonant_sandhi(text):
        if cand not in seen:
            seen.add(cand)
            score = _baseline_score(text, cand, rn, lexicon)
            out.append({'cand': cand, 'score': score, 'rules': [rn]})

    return out

# Scoring heuristics
def _baseline_score(orig: str, cand: str, rule_name: str, lexicon:set) -> float:
    """
    Compute a simple score for candidate plausibility:
     - start from 1.0
     - penalize number of inserted independent vowels (makes candidate unlikely)
     - reward lexicon overlap (fraction of whitespace-separated tokens found in lexicon)
     - penalize very long change (Levenshtein distance / char difference)
     - small negative per applied rule for complexity
    """
    score = 1.0

    # penalize isolated independent vowels (नकार्य splits)
    iso_vowels = len([t for t in re.split(r'\s+', cand) if len(t)==1 and re.match(r'[\u0905-\u0914]', t)])
    score -= 0.25 * iso_vowels

    # lexicon reward: fraction of tokens in lexicon
    tokens = [t for t in re.split(r'\s+', cand) if t]
    if tokens:
        found = sum(1 for t in tokens if t in lexicon)
        frac = found / len(tokens)
        score += 0.7 * frac  # reward matches strongly

    # small penalty for large edit distance (approx via char diff)
    diff = abs(len(cand) - len(orig))
    score -= 0.02 * diff

    # penalize applying "aggressive" rules by default
    if 'ai->' in rule_name or 'a+u' in rule_name or 'ū' in rule_name:
        score -= 0.1

    # rule-name tiny penalty
    if rule_name:
        score -= 0.03

    # clip
    if score < -2.0: score = -2.0
    if score > 2.0: score = 2.0
    return float(score)

# Main generator
def gen_candidates(line: str, k: int = 8, lexicon_path: str = None, allow_aggressive: bool = False) -> List[Dict]:
    """
    Generate up to `k` candidate reverse-sandhi decompositions for `line`.
    Returns list of dicts: {'cand': text, 'score':score, 'rules':[...]} sorted by score desc.

    Parameters:
      - line: input string (merged form)
      - k: max candidates to return
      - lexicon_path: optional path to lexicon file (one token per line)
      - allow_aggressive: if True, also include aggressive vowel splits (may create noise)
    """
    line = line.strip()
    lexicon = set(DEFAULT_LEXICON)
    if lexicon_path:
        lexicon |= load_lexicon(lexicon_path)

    # start with original (score baseline)
    candidates = [{'cand': line, 'score': _baseline_score(line, line, 'identity', lexicon), 'rules': ['identity']}]

    # one-step candidates
    one_step = _one_step_candidates(line, lexicon)
    candidates.extend(one_step)

    # if aggressive allowed, add extra vowel-splits (may explode)
    if allow_aggressive:
        # further split e -> a+i and maybe ai -> a+i etc.
        if 'े' in line:
            candidates.append({'cand': line.replace('े', 'अइ'), 'score': _baseline_score(line, line.replace('े','अइ'), 'aggr-e->a+i', lexicon), 'rules':['aggr-e->a+i']})
        if 'ो' in line:
            candidates.append({'cand': line.replace('ो', 'अउ'), 'score': _baseline_score(line, line.replace('ो','अउ'), 'aggr-o->a+u', lexicon), 'rules':['aggr-o->a+u']})

    # Expand multi-step by trying one-step on each of one_step results (controlled, not exhaustive)
    expanded = []
    for item in one_step:
        sub_candidates = _one_step_candidates(item['cand'], lexicon)
        for s in sub_candidates:
            # combine rule names
            combined_rules = item['rules'] + s['rules']
            combined_score = (item['score'] + s['score']) / 2.0  # simple average
            expanded.append({'cand': s['cand'], 'score': combined_score, 'rules': combined_rules})
    candidates.extend(expanded)

    # dedupe by cand text, keep best score
    best = {}
    for c in candidates:
        txt = re.sub(r'\s+', ' ', c['cand'].strip())
        if txt not in best or c['score'] > best[txt]['score']:
            best[txt] = {'cand': txt, 'score': c['score'], 'rules': c.get('rules', [])}

    # sort by score descending
    result = sorted(best.values(), key=lambda x: x['score'], reverse=True)

    # heuristics: prefer candidates with more tokens (word splits) moderately
    def token_boost(x):
        toks = [t for t in re.split(r'\s+', x['cand']) if t]
        return len(toks) * 0.01
    for r in result:
        r['score'] += token_boost(r)

    return result[:k]

# quick CLI test if run directly
if __name__ == "__main__":
    examples = [
        "रामोऽस्ति बलवान्",
        "कर्मण्येवाधिकारस्ते",
        "सर्वे भवन्तु सुखिनः",
        "सह नाववतु"
    ]
    lex = None
    for e in examples:
        print("INPUT:", e)
        for c in gen_candidates(e, k=6, lexicon_path=None, allow_aggressive=False):
            print(f"  {c['score']:+0.3f} {c['cand']}  rules={c['rules']}")
        print()
