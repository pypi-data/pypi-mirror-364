import logging
import re
import unicodedata
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor, as_completed

from metaphone import doublemetaphone
try:
    import jellyfish
    _have_jaro = True
except ImportError:
    _have_jaro = False

try:
    import Levenshtein
    _have_lev = True
except ImportError:
    _have_lev = False


from canonmap.services.db_mysql.adapters.connection import ConnectionManager
from canonmap.services.db_mysql.schemas import MatchEntityRequest

logger = logging.getLogger(__name__)


class MatcherManager:
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    def match(self, request: MatchEntityRequest, top_n=20, weights=None) -> list[tuple[str, float]]:
        def _normalize(s: str) -> str:
            s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
            s = re.sub(r"[^\w\s]", " ", s)
            return re.sub(r"\s+", " ", s).strip().lower()

        def _trigram_similarity(a: str, b: str) -> float:
            def grams(s):
                return {s[i:i+3] for i in range(len(s)-2)}
            A, B = grams(a), grams(b)
            if not A or not B:
                return 0.0
            return len(A & B) / len(A | B)

        def _block_by_phonetic(conn, entity_name: str, table_name: str, field_name: str) -> set:
            p1, p2 = doublemetaphone(entity_name)
            search_code = p1 or p2
            if not search_code:
                return set()
            sql = f"""SELECT DISTINCT `{field_name}` AS name
                    FROM `{table_name}`
                    WHERE `__{field_name}_phonetic__` = %s"""
            with conn.cursor() as cur:
                cur.execute(sql, (search_code,))
                return {r[0] for r in cur.fetchall()}

        def _block_by_soundex(conn, entity_name: str, table_name: str, field_name: str) -> set:
            sql = f"""SELECT DISTINCT `{field_name}` AS name
                    FROM `{table_name}`
                    WHERE `__{field_name}_soundex__` = SOUNDEX(%s)"""
            with conn.cursor() as cur:
                cur.execute(sql, (entity_name,))
                return {r[0] for r in cur.fetchall()}

        def _block_by_initialism(conn, entity_name: str, table_name: str, field_name: str) -> set:
            if not entity_name:
                return set()
            entity_clean = entity_name.strip().upper()
            if (entity_clean.isalpha() and 
                len(entity_clean) <= 6 and 
                len(entity_clean) >= 2 and
                ' ' not in entity_clean):
                search_initialism = entity_clean
            else:
                parts = re.findall(r"[A-Za-z]+", entity_name)
                search_initialism = "".join(p[0].upper() for p in parts) if parts else None
            if not search_initialism:
                return set()
            sql = f"""SELECT DISTINCT `{field_name}` AS name
                    FROM `{table_name}`
                    WHERE `__{field_name}_initialism__` = %s"""
            with conn.cursor() as cur:
                cur.execute(sql, (search_initialism,))
                return {r[0] for r in cur.fetchall()}

        def _block_by_exact_match(conn, entity_name: str, table_name: str, field_name: str) -> set:
            if not entity_name:
                return set()
            search_term = entity_name.strip().lower()
            sql = f"""SELECT DISTINCT `{field_name}` AS name
                    FROM `{table_name}`
                    WHERE LOWER(TRIM(`{field_name}`)) LIKE %s"""
            with conn.cursor() as cur:
                cur.execute(sql, (f"%{search_term}%",))
                return {r[0] for r in cur.fetchall()}

        default_weights = {
            "exact": 6.0,
            "levenshtein": 1.0,
            "jaro": 1.2,
            "token": 2.0,
            "trigram": 1.0,
            "phonetic": 1.0,
            "initialism": 0.5,
            "multi_bonus": 1.0,
        }
        weights = weights or default_weights

        normalized_entity_name = _normalize(request.entity_name)
        candidates = set()
        conn = self.connection_manager.conn or self.connection_manager.connect()
        for field in request.select_fields:
            candidates = candidates.union(_block_by_phonetic(conn, normalized_entity_name, field.table_name, field.field_name))
            candidates = candidates.union(_block_by_soundex(conn, normalized_entity_name, field.table_name, field.field_name))
            candidates = candidates.union(_block_by_initialism(conn, normalized_entity_name, field.table_name, field.field_name))
            candidates = candidates.union(_block_by_exact_match(conn, normalized_entity_name, field.table_name, field.field_name))

        def _score_candidate(normalized_entity_name: str, candidate_name: str) -> dict:
            cand_norm = _normalize(candidate_name)
            tokens = normalized_entity_name.split()
            first, last = tokens[0], tokens[-1] if tokens else ("", "")
            # exact
            exact = 1.0 if cand_norm == normalized_entity_name else 0.0
            # Levenshtein
            if _have_lev:
                lev_full = Levenshtein.ratio(normalized_entity_name, cand_norm)
                lev_last = Levenshtein.ratio(last, _normalize(candidate_name.split()[-1])) if last else 0.0
            else:
                lev_full = SequenceMatcher(None, normalized_entity_name, cand_norm).ratio()
                lev_last = SequenceMatcher(None, last, _normalize(candidate_name.split()[-1])).ratio() if last else 0.0
            levenshtein = 0.3 * lev_full + 0.7 * lev_last
            # Jaro–Winkler
            if _have_jaro:
                jaro = jellyfish.jaro_winkler_similarity(normalized_entity_name, cand_norm)
            else:
                jaro = levenshtein
            # Token overlap (first vs last)
            tok_first = float(first in cand_norm)
            tok_last = float(last in cand_norm)
            token = 0.3 * tok_first + 0.7 * tok_last
            # Trigram
            tri = _trigram_similarity(normalized_entity_name, cand_norm)
            # Phonetic - recompute from candidate name
            p1, p2 = doublemetaphone(cand_norm)
            last_phonetic = doublemetaphone(last)[0] if last else ""
            phon = float(last_phonetic in (p1, p2)) if last_phonetic else 0.0
            # Initialism - recompute from candidate name
            init = "".join(tok[0] for tok in cand_norm.split() if tok)
            query_init = "".join(tok[0] for tok in normalized_entity_name.split() if tok)
            init_score = float(init == query_init) if query_init else 0.0
            
            return {
                "exact": exact,
                "levenshtein": levenshtein,
                "jaro": jaro,
                "token": token,
                "trigram": tri,
                "phonetic": phon,
                "initialism": init_score,
            }

        # Score in parallel
        signatures = []
        with ThreadPoolExecutor() as ex:
            futures = {ex.submit(_score_candidate, normalized_entity_name, candidate_name): candidate_name for candidate_name in candidates}
            for future in as_completed(futures):
                candidate_name = futures[future]
                signature = future.result()
                signatures.append((candidate_name, signature))

        # Combine + rank
        ranked = []
        for candidate_name, signature in signatures:
            total = sum(signature[k] * weights[k] for k in signature)
            multi = sum(1 for k in ("levenshtein","token","phonetic","initialism") if signature[k] > 0)
            total += max(0, multi - 1) * weights["multi_bonus"]
            ranked.append((candidate_name, total))

        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked[:top_n]
    
