# scripts/pipeline.py
from typing import List, Dict, Any
from .utils import normalize_text
from .sandhi_rules import gen_candidates
import os, re
from pathlib import Path

VIRAMA = '\u094D'  # ्
ANUSVARA = '\u0902'  # ं
VISARGA = '\u0903'  # ः
CHANDRABINDU = '\u0901'  # ँ

MATRAS = set(list('ािीुूृेैोौ'))  # dependent vowels
CONSONANTS = set(chr(c) for c in range(0x0915, 0x093A))
INDEP_VOWELS = set(chr(c) for c in range(0x0905, 0x0915))
COMBINING = {ANUSVARA, VISARGA, CHANDRABINDU}
LONG_VOWELS = set(list('ाीूेैोौ'))


def is_consonant(ch: str) -> bool:
    return ch in CONSONANTS

def is_matra(ch: str) -> bool:
    return ch in MATRAS

def is_indep_vowel(ch: str) -> bool:
    return ch in INDEP_VOWELS

def _load_lexicon(path: str = "data/lexicon.txt"):
    p = Path(path)
    if not p.exists():
        return set()
    with p.open("r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}

def syllabify_devanagari(line: str) -> List[str]:
    line = line.strip()
    sylls = []
    i = 0
    n = len(line)
    while i < n:
        if line[i].isspace():
            i += 1
            continue
        buf = ''
        # onset consonant cluster (with virama)
        if is_consonant(line[i]):
            while i < n and is_consonant(line[i]):
                buf += line[i]
                i += 1
                if i < n and line[i] == VIRAMA:
                    buf += line[i]; i += 1; continue
                else:
                    break
            # attach matra if present
            if i < n and is_matra(line[i]):
                buf += line[i]; i += 1
        elif is_indep_vowel(line[i]):
            buf += line[i]; i += 1
            if i < n and line[i] in COMBINING:
                buf += line[i]; i += 1
        else:
            buf += line[i]; i += 1
        # trailing anusvara/visarga etc
        if i < n and line[i] in COMBINING:
            buf += line[i]; i += 1
        if buf:
            sylls.append(buf)
    return sylls


def silver_label_syllable(syll: str):
    """Return (label, confidence, reason)"""
    # deterministic high-confidence rules
    if any(ch in syll for ch in COMBINING):
        return ('G', 0.95, 'anusvara/visarga/chandrabindu present (rule)')
    if any(ch in syll for ch in LONG_VOWELS):
        return ('G', 0.95, 'long vowel matra/indep vowel (rule)')
    if VIRAMA in syll:  # conjunct => heavy
        return ('G', 0.9, 'consonant conjunct / halant (rule)')
    # default
    return ('L', 0.95, 'short vowel / open syllable (rule)')


# Expanded meter templates (classical meters + common templates)
# Each entry: 'Name': {'total': total_syllables, 'padas': [pada1_len, pada2_len, ...] or None}
METER_TEMPLATES = {
    'Gayatri': {'total': 24, 'padas': [8, 8, 8]},
    'Anushtubh': {'total': 32, 'padas': [8, 8, 8, 8]},     # common śloka (śloka/pada = 8)
    'Tristubh': {'total': 44, 'padas': [11, 11, 11, 11]},
    'Jagati': {'total': 48, 'padas': [12, 12, 12, 12]},
    # Additional classical meters (typical totals & pada-splits)
    'Pankti': {'total': 25, 'padas': [5, 5, 5, 5, 5]},            # 5x5 (Pankti)
    'Vasantatilaka': {'total': 56, 'padas': [14, 14, 14, 14]},   # 4x14
    'Mandakranta': {'total': 68, 'padas': [17, 17, 17, 17]},     # 4x17
    'ShardulaVikridita': {'total': 76, 'padas': [19, 19, 19, 19]}, # 4x19 (Śārdūlavikrīḍita)
    # Upajati/other mixed forms can be added as custom templates
}

def _chunk_syllables_into_padas(syllables: List[str], padas: List[int]) -> List[List[str]]:
    """
    Conservative chunking: attempt to split the syllable list into the given pada lengths.
    If total lengths don't match, returns an empty list.
    """
    total_expected = sum(padas)
    if len(syllables) != total_expected:
        return []
    out = []
    i = 0
    for plen in padas:
        out.append(syllables[i:i+plen])
        i += plen
    return out


def match_chanda(syllables: List[str], labels: List[str], top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Improved chanda matcher with stricter scoring:
      - Strong preference for exact total-syllable match (bonus).
      - If template has padas and totals match exactly, reward per-pada agreement strongly.
      - Penalize total mismatches more sharply (nonlinear).
      - Guru agreement remains a secondary signal.
    """
    results = []
    total = len(syllables)
    guru_frac = labels.count('G') / max(1, len(labels))

    for name, tpl in METER_TEMPLATES.items():
        expected_total = tpl['total']

        # normalized absolute difference
        total_diff = abs(total - expected_total) / max(expected_total, total)

        # make mismatch penalty nonlinear to prefer exact matches strongly
        # small diffs are penalized a bit more (power 1.5)
        total_score = max(0.0, 1.0 - (total_diff ** 1.5))

        # give an explicit bonus for exact total match
        exact_total_bonus = 0.12 if total == expected_total else 0.0
        total_score = min(1.0, total_score + exact_total_bonus)

        # pada matching: stronger handling
        pada_score = 0.0
        pada_details = None
        padas = tpl.get('padas')
        if padas:
            if total == sum(padas):
                # exact pada alignment possible -> compute guru fraction per pada
                parts = _chunk_syllables_into_padas(syllables, padas)
                per_pada = []
                for idx, part in enumerate(parts):
                    start = sum(padas[:idx])
                    end = start + len(part)
                    p_guru_frac = sum(1 for s_lab in labels[start:end] if s_lab == 'G') / max(1, len(part))
                    per_pada.append({'pada_index': idx+1, 'length': len(part), 'guru_frac': p_guru_frac})
                avg_p_guru = sum(p['guru_frac'] for p in per_pada) / max(1, len(per_pada))

                # pada_score combines structural match (perfect lengths) + guru agreement per pada
                # we reward if average pada guru_frac is close to expected_guru_frac
                expected_guru_frac = min(0.6, expected_total/100.0 + 0.4)
                guru_agreement = 1.0 - min(1.0, abs(avg_p_guru - expected_guru_frac))
                # give larger weight to pada structural match + guru agreement
                pada_score = 0.9 * 1.0 + 0.1 * guru_agreement
                pada_details = per_pada
            else:
                # totals don't match -> penalty proportional to mismatch
                mismatch_frac = abs(total - sum(padas)) / max(sum(padas), total)
                pada_score = max(0.0, 0.25 * (1.0 - mismatch_frac))
                pada_details = {'note': 'total mismatch, no direct pada split', 'mismatch_frac': mismatch_frac}
        else:
            # no pada info -> neutral small value
            pada_score = 0.4
            pada_details = None

        # guru expectation for whole line (secondary signal)
        expected_guru_frac_whole = min(0.6, expected_total/100.0 + 0.4)
        guru_score = 1.0 - min(1.0, abs(guru_frac - expected_guru_frac_whole))

        # final combination: strong weight to total & pada (when exact), then guru
        # if exact total & padas matched, pada_score gets large influence
        if padas and total == sum(padas):
            combined = 0.70 * total_score + 0.20 * pada_score + 0.10 * guru_score
        else:
            combined = 0.80 * total_score + 0.10 * pada_score + 0.10 * guru_score

        results.append({
            'meter': name,
            'score': combined,
            'details': {
                'total': total,
                'expected_total': expected_total,
                'total_score': total_score,
                'exact_total_bonus': exact_total_bonus,
                'guru_frac': guru_frac,
                'expected_guru_frac_whole': expected_guru_frac_whole,
                'guru_score': guru_score,
                'pada_score': pada_score,
                'pada_details': pada_details
            }
        })

    # sort and return top_k
    results.sort(key=lambda x: x['score'], reverse=True)
    return results[:top_k]

def infer_line(line: str, use_sandhi=True) -> Dict[str, Any]:
    line = normalize_text(line)
    raw_cands = gen_candidates(line) if use_sandhi else [line]
    cand_results = []

    # load lexicon (optional)
    LEX = _load_lexicon("data/lexicon.txt")

    # helper: compute meter similarity bonus for a candidate
    def meter_match_bonus(sylls: List[str]) -> float:
        n = len(sylls)
        # if exact match to any template total -> big bonus
        for tpl in METER_TEMPLATES.values():
            if n == tpl['total']:
                return 0.30  # strong bonus for exact total match
        # otherwise small graded score: max(0, 0.2 - normalized_diff)
        best = 0.0
        for tpl in METER_TEMPLATES.values():
            expected = tpl['total']
            diff_frac = abs(n - expected) / max(n, expected)
            score = max(0.0, 0.20 * (1.0 - diff_frac))  # smaller bonus for near matches
            if score > best:
                best = score
        return best

    # process each candidate (support both string and dict shapes)
    for raw in raw_cands:
        if isinstance(raw, dict):
            cand_text = raw.get('cand', '') or raw.get('candidate', '')
            meta_rules = raw.get('rules', [])
            meta_score = raw.get('score', None)
        else:
            cand_text = raw
            meta_rules = []
            meta_score = None

        sylls = syllabify_devanagari(cand_text)
        silver = [silver_label_syllable(s) for s in sylls]
        labels = [lab for lab, conf, reason in silver]
        confidences = [conf for lab, conf, reason in silver]
        reasons = [reason for lab, conf, reason in silver]

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        # isolated independent-vowel penalty (strong)
        iso_vowels = sum(1 for s in sylls if len(s) == 1 and s in INDEP_VOWELS)
        iso_frac = iso_vowels / max(1, len(sylls))

        # lexicon overlap: fraction of whitespace-tokens in LEX (if LEX exists)
        tokens = [t for t in re.split(r'\s+', cand_text) if t]
        lex_found = 0
        if tokens and LEX:
            lex_found = sum(1 for t in tokens if t in LEX)
        lex_score = (lex_found / len(tokens)) if tokens else 0.0

        # meter-aware bonus
        m_bonus = meter_match_bonus(sylls)

        # combined score (tunable weights)
        # note: iso_frac is penalized strongly to avoid candidates with 'अ','अ' insertions
        combined_score = (0.55 * avg_conf) + (0.15 * lex_score) + m_bonus - (0.9 * iso_frac)

        # if gen_candidates produced its own score, slightly factor it in (small weight)
        if meta_score is not None:
            combined_score = 0.9 * combined_score + 0.1 * float(meta_score)

        cand_results.append({
            'candidate': cand_text,
            'syllables': sylls,
            'silver_labels': labels,
            'silver_conf': confidences,
            'silver_reasons': reasons,
            'meta_rules': meta_rules,
            'meta_score': meta_score,
            'avg_conf': avg_conf,
            'lex_score': lex_score,
            'iso_frac': iso_frac,
            'meter_bonus': m_bonus,
            'combined_score': combined_score
        })

    # choose best candidate by combined_score (fall back to avg_conf)
    best = max(cand_results, key=lambda c: c.get('combined_score', c.get('avg_conf', 0.0)))
    return {
        'line': line,
        'candidates': cand_results,
        'chosen_candidate': best,
        'top_chanda': match_chanda(best['syllables'], best['silver_labels'])
    }
# ---------- end replacement ----------