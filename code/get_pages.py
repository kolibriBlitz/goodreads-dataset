import requests
import pandas as pd
import time
import json
from rapidfuzz import fuzz
from pathlib import Path

# CONFIG ---------------------------------------------------
INPUT_CSV = "no_pages.csv"  # your exported missing-pages CSV
OUTPUT_FILLED = "filled_pages.csv"
OUTPUT_REVIEW = "low_confidence_review.csv"
CONFIDENCE_THRESHOLD = 75  # auto-fill threshold
SLEEP_BETWEEN_QUERIES = 0.2  # polite delay between Open Library calls
GOOGLE_API_KEY = "AIzaSyAmkyIEQpivLoLkxSEcid6bnKQDeRjT88k"  # <<< put your real key here

# Cache files ------------------------------------------------
EDITION_CACHE_FILE = "edition_pagecount_cache.json"
GB_CACHE_FILE = "google_books_cache.json"

# Load or init caches
try:
    with open(EDITION_CACHE_FILE, "r", encoding="utf-8") as f:
        edition_cache = json.load(f)
except FileNotFoundError:
    edition_cache = {}

try:
    with open(GB_CACHE_FILE, "r", encoding="utf-8") as f:
        gb_cache = json.load(f)
except FileNotFoundError:
    gb_cache = {}

def save_edition_cache():
    with open(EDITION_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(edition_cache, f)

def save_gb_cache():
    with open(GB_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(gb_cache, f)


# Helpers ---------------------------------------------------

def search_openlibrary(title, author, limit=5):
    """Search Open Library by title+author (no year filtering)."""
    q = f"{title} {author}"
    params = {"q": q, "limit": limit}
    try:
        r = requests.get("https://openlibrary.org/search.json", params=params, timeout=8)
        if r.status_code == 200:
            return r.json().get("docs", [])
    except Exception as e:
        print(f"    ! OpenLibrary search error: {e}")
    return []

def score_candidate(row_title, row_author, candidate):
    cand_title = candidate.get("title", "")
    cand_authors = candidate.get("author_name", [])
    cand_author = " ".join(cand_authors) if cand_authors else ""
    title_score = fuzz.token_set_ratio(row_title, cand_title)
    author_score = fuzz.token_set_ratio(row_author, cand_author)
    combined = 0.7 * title_score + 0.3 * author_score
    return combined, title_score, author_score

def extract_page_count(candidate):
    """Top-level Open Library hit page count, if present."""
    if candidate.get("number_of_pages_median"):
        return candidate.get("number_of_pages_median")
    if candidate.get("number_of_pages"):
        return candidate.get("number_of_pages")
    return None

def fetch_page_count_from_edition(candidate):
    """Follow edition_key(s) to get page count, with caching."""
    edition_keys = candidate.get("edition_key", [])
    if not edition_keys:
        return None
    for ek in edition_keys[:3]:  # try first few
        if ek in edition_cache:
            # cached even if None
            return edition_cache[ek]
        try:
            url = f"https://openlibrary.org/books/{ek}.json"
            r = requests.get(url, timeout=8)
            if r.status_code == 200:
                ed = r.json()
                pc = ed.get("number_of_pages")
                edition_cache[ek] = pc  # cache (could be None)
                save_edition_cache()
                if pc:
                    return pc
        except Exception as e:
            edition_cache[ek] = None
            save_edition_cache()
            print(f"    ! Edition lookup error for {ek}: {e}")
            continue
    return None

def fetch_google_books_page_count(title, author, max_results=5):
    """
    Query Google Books API, with simple fuzzy filter; returns tuple:
    (page_count, gb_title, gb_authors_str, combined_score)
    Cached by normalized key.
    """
    key = f"{title.strip().lower()}||{author.strip().lower()}"
    if key in gb_cache:
        return gb_cache[key]  # expected to be tuple or (None, None, None, 0)

    query = f"{title} {author}"
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "printType": "books",
        "key": GOOGLE_API_KEY
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            best = (None, None, None, 0)  # page_count, title, authors, score
            for item in items:
                volume = item.get("volumeInfo", {})
                page_count = volume.get("pageCount")
                gb_title = volume.get("title", "")
                authors_list = volume.get("authors", [])
                gb_authors = " ".join(authors_list) if authors_list else ""
                # fuzzy scoring similar weights
                score = 0.7 * fuzz.token_set_ratio(title, gb_title) + 0.3 * fuzz.token_set_ratio(author, gb_authors)
                if page_count and score > best[3]:
                    best = (page_count, gb_title, gb_authors, score)
            gb_cache[key] = best
            save_gb_cache()
            return best
    except Exception as e:
        print(f"    ! Google Books lookup error: {e}")
    gb_cache[key] = (None, None, None, 0)
    save_gb_cache()
    return (None, None, None, 0)


# Main ------------------------------------------------------

def main():
    df = pd.read_csv(INPUT_CSV, dtype=str)
    df = df.rename(columns={
        "original_title": "Title",
        "author": "Author",
        "original_publication_year": "Year",  # kept for reference
        "num_pages": "Length"
    })
    df["Length"] = df["Length"].fillna("0")
    results = []
    review_rows = []

    print(f"Starting fill loop over {len(df)} rows")
    for idx, row in df.iterrows():
        title = row.get("Title", "") or ""
        author = row.get("Author", "") or ""
        print(f"Processing index {idx}: {title} by {author}")

        best_match = None
        best_score = -1
        best_page_count = None
        title_score = author_score = 0
        source_label = "None"

        # 1. Open Library search
        print("  → querying OpenLibrary...")
        candidates = search_openlibrary(title, author)
        print(f"  ← got {len(candidates)} candidate(s), evaluating...")

        for cand in candidates:
            combined, t_score, a_score = score_candidate(title, author, cand)
            if combined > best_score:
                best_score = combined
                title_score = t_score
                author_score = a_score

                # try top-level hit
                page_count = extract_page_count(cand)

                # fallback to edition if missing
                if page_count is None:
                    print("    → no page count on search hit; trying edition lookup")
                    page_count = fetch_page_count_from_edition(cand)
                    if page_count:
                        print(f"    ← recovered page count {page_count} from OpenLibrary edition")

                best_match = cand
                best_page_count = page_count
                source_label = "OpenLibrary"

        # 2. If still no page count, try Google Books fallback
        if not best_page_count:
            print("    → trying Google Books fallback")
            gb_pages, gb_title, gb_authors, gb_score = fetch_google_books_page_count(title, author)
            if gb_pages:
                best_page_count = gb_pages
                # craft a synthetic match for consistent output structure
                best_match = {"title": gb_title, "author_name": [gb_authors]}
                # merge confidence: take the higher of existing best_score and google's
                best_score = max(best_score, gb_score)
                title_score = fuzz.token_set_ratio(title, gb_title)
                author_score = fuzz.token_set_ratio(author, gb_authors)
                source_label = "GoogleBooks"
                print(f"    ← recovered {gb_pages} pages via Google Books (score {gb_score:.1f})")

        # Decide fill vs review
        if best_page_count and best_score >= CONFIDENCE_THRESHOLD:
            filled_length = int(best_page_count)
            df.at[idx, "Length"] = filled_length
            results.append({
                **row.to_dict(),
                "Filled_Length": filled_length,
                "Confidence": round(best_score, 1),
                "Title_Score": title_score,
                "Author_Score": author_score,
                "Source": source_label,
                "OL_Title": best_match.get("title", "") if best_match else "",
                "OL_Author": " | ".join(best_match.get("author_name", [])) if best_match else "",
                "Used_Edition_Fallback": source_label == "OpenLibrary" and extract_page_count(best_match) is None
            })
        else:
            candidate_info = best_match or {}
            review_rows.append({
                **row.to_dict(),
                "Best_Approx_Page_Count": best_page_count,
                "Best_Confidence": round(best_score, 1) if best_score >= 0 else None,
                "Title_Score": title_score,
                "Author_Score": author_score,
                "OL_Title": candidate_info.get("title", ""),
                "OL_Author": " | ".join(candidate_info.get("author_name", [])) if candidate_info else "",
                "Source": source_label,
                "Used_Edition_Fallback": source_label == "OpenLibrary" and extract_page_count(candidate_info) is None
            })

        time.sleep(SLEEP_BETWEEN_QUERIES)

    # Save outputs
    if results:
        pd.DataFrame(results).to_csv(OUTPUT_FILLED, index=False)
        print(f"Auto-filled {len(results)} rows written to {OUTPUT_FILLED}")
    else:
        print("No confident automatic fills.")

    if review_rows:
        pd.DataFrame(review_rows).to_csv(OUTPUT_REVIEW, index=False)
        print(f"{len(review_rows)} rows needing review written to {OUTPUT_REVIEW}")
    else:
        print("No rows requiring manual review.")

    df.to_csv("merged_with_attempts.csv", index=False)
    print("Full attempt data saved to merged_with_attempts.csv")


if __name__ == "__main__":
    main()
