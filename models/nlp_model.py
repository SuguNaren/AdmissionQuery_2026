import os
import re

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.pipeline import FeatureUnion


load_dotenv()

PROSPECTUS_PDF = os.getenv(
    "PROSPECTUS_PDFS",
    "StellaMarisCollegeProspectus-UG_2025-2026.pdf",
)
PROSPECTUS_PDFS = os.getenv("PROSPECTUS_PDFS", PROSPECTUS_PDF)
MIN_CHUNK_SCORE = float(os.getenv("MIN_CHUNK_SCORE", "0.08"))
MAX_ANSWER_PARTS = int(os.getenv("MAX_ANSWER_PARTS", "4"))

texts = []
corpus_text = ""
course_catalog = []
vectorizer = None
tfidf_matrix = None

ONLINE_APPLICATION_KNOWLEDGE = """
Instructions for Submitting the Online Application Form
Applicants are required to carefully read the instructions before submitting the online application form.
The College may reject applications that are incomplete, incorrect, contain false information, miss mandatory documents, or are submitted without payment of the application fee.

Uploading Required Documents
Before submitting the online application form, applicants must upload the following scanned files:
Passport-size photograph in JPG or JPEG format with a maximum size of 50 KB.
Applicant's signature in JPG or JPEG format with a maximum size of 20 KB.
Parent or Guardian signature in JPG or JPEG format with a maximum size of 20 KB.
Community Certificate, except for OC and Others categories, in JPG, JPEG, or GIF format with a maximum size of 2 MB.
Baptism Certificate for Catholic applicants in JPG, JPEG, or GIF format with a maximum size of 2 MB.
Self-attested copies of all available semester mark sheets for postgraduate applicants compiled into a single PDF with a maximum size of 5 MB.

Important Guidelines
Documents can be uploaded only after entering academic marks.
The Unique Application Number, UAN, needed for uploading documents is generated when the Save option is clicked on the Preview page.
Applicants must use the UAN as the Username and their Date of Birth as the Password to log in and upload documents on the College website.
Applicants may edit their application details before paying the application fee by clicking the Login button.
Editing or updating details is not possible after the application fee has been paid.
The application fee must be paid online through internet banking, credit card, or debit card only.
The application fee is non-refundable under any circumstances.
Applicants can check their application and fee payment status through the Applicant login on the College website.
The receipt of the application fee will be updated in the Applicant login 24 hours after the transaction.
Information about applicants shortlisted for interviews will be sent by email and SMS and will also be uploaded on the College website.
Applicants must attend the interview on the specified date and time. Being called for an interview does not guarantee admission.
No information will be sent to applicants who are not provisionally selected.
The list of provisionally selected applicants will be uploaded on the College website after 8:00 p.m.
Selected applicants must pay the prescribed fees and submit their original certificates along with photocopies on the specified date and time. Late payments will not be accepted.
Details about documents required at the time of interview can be accessed by clicking the Document Info Attachment button.

Note
The application fee is non-refundable.
For further queries, please email admissions@stellamariscollege.edu.in.
""".strip()


DEGREES = {
    "ba": {"display": "B.A.", "pattern": r"B\.?\s*A\.?", "default_duration": "3 years / 6 semesters"},
    "bsc": {"display": "B.Sc.", "pattern": r"B\.?\s*Sc\.?", "default_duration": "3 years / 6 semesters"},
    "bcom": {"display": "B.Com.", "pattern": r"B\.?\s*Com\.?", "default_duration": "3 years / 6 semesters"},
    "bba": {"display": "B.B.A.", "pattern": r"B\.?\s*B\.?\s*A\.?", "default_duration": "3 years / 6 semesters"},
    "bca": {"display": "B.C.A.", "pattern": r"B\.?\s*C\.?\s*A\.?", "default_duration": "3 years / 6 semesters"},
    "bsw": {"display": "B.S.W.", "pattern": r"B\.?\s*S\.?\s*W\.?", "default_duration": "3 years / 6 semesters"},
    "bvoc": {"display": "B.Voc.", "pattern": r"B\.?\s*Voc\.?", "default_duration": "3 years / 6 semesters"},
    "bva": {"display": "B.V.A.", "pattern": r"B\.?\s*V\.?\s*A\.?", "default_duration": "4 years / 8 semesters"},
    "ma": {"display": "M.A.", "pattern": r"M\.?\s*A\.?", "default_duration": "2 years / 4 semesters"},
    "msc": {"display": "M.Sc.", "pattern": r"M\.?\s*Sc\.?", "default_duration": "2 years / 4 semesters"},
    "mcom": {"display": "M.Com.", "pattern": r"M\.?\s*Com\.?", "default_duration": "2 years / 4 semesters"},
    "msw": {"display": "M.S.W.", "pattern": r"M\.?\s*S\.?\s*W\.?", "default_duration": "2 years / 4 semesters"},
}

QUERY_EXPANSIONS = {
    "ug": "undergraduate degree programme course eligibility fee",
    "undergraduate": "ug degree programme course eligibility fee",
    "pg": "postgraduate degree programme course eligibility fee",
    "postgraduate": "pg degree programme course eligibility fee",
    "fees": "fee structure tuition fees payment amount",
    "fee": "fee structure tuition fees payment amount",
    "hostel": "residence hostel facility accommodation",
    "eligibility": "eligibility requirement subjects studied qualifying examination",
    "admission": "admission application selection merit interview counselling",
    "deadline": "last date application deadline admission",
    "scholarship": "scholarship financial aid freeship concession",
    "contact": "phone telephone mobile number address location email",
    "address": "contact office address location campus",
    "phone": "contact phone telephone number office",
    "number": "contact phone telephone number office",
}

FOLLOW_UP_TERMS = {
    "it",
    "its",
    "that",
    "this",
    "they",
    "them",
    "those",
    "these",
    "same",
    "previous",
    "before",
    "above",
}

GENERIC_QUERY_TERMS = {
    "course",
    "courses",
    "eligibility",
    "fee",
    "fees",
    "structure",
    "duration",
    "semester",
    "semesters",
    "qualifying",
    "required",
    "requirement",
    "needed",
    "need",
    "apply",
    "admission",
    "12th",
    "standard",
    "higher",
    "secondary",
    "subject",
    "subjects",
    "programme",
    "program",
    "programmes",
    "programs",
    "details",
    "detail",
}


def _clean_text(text):
    text = text.replace("\u00a0", " ")
    text = re.sub(r"-\s*\n\s*", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _compact_text(text):
    return re.sub(r"\s+", " ", text).strip(" .-")


def _degree_boundaries(allowed_degrees=None):
    allowed = allowed_degrees or DEGREES.keys()
    alternatives = "|".join(
        f"(?P<{key}>(?<![A-Za-z])(?:{value['pattern']})(?![A-Za-z]))"
        for key, value in DEGREES.items()
        if key in allowed
    )
    return f"(?:{alternatives})"


def _normalize_degree_names(query):
    normalized = query
    # Longer degree patterns first prevents B.A. from catching B.B.A.
    for key in sorted(DEGREES, key=len, reverse=True):
        normalized = re.sub(
            rf"\b{DEGREES[key]['pattern']}\b",
            key,
            normalized,
            flags=re.IGNORECASE,
        )
    return normalized


def _query_terms(query):
    terms = re.findall(r"[a-z0-9]+", _normalize_degree_names(query).lower())
    return [
        term
        for term in terms
        if len(term) >= 2 and term not in ENGLISH_STOP_WORDS
    ]


def _degree_terms(query_terms):
    return [term for term in query_terms if term in DEGREES]


def _meaningful_terms(query_terms):
    return [
        term
        for term in query_terms
        if term not in DEGREES and term not in GENERIC_QUERY_TERMS
    ]


def _text_has_term(text, term):
    normalized = re.sub(r"[^a-z0-9]+", " ", _normalize_degree_names(text).lower())
    return re.search(rf"\b{re.escape(term.lower())}\b", normalized) is not None


def _has_enough_query_overlap(query_terms):
    if not query_terms:
        return True

    matched = sum(1 for term in query_terms if _text_has_term(corpus_text, term))
    required_ratio = 0.66 if len(query_terms) > 1 else 1
    return matched / len(query_terms) >= required_ratio


def _expand_query(query):
    query_lower = query.lower()
    additions = [
        expansion
        for keyword, expansion in QUERY_EXPANSIONS.items()
        if keyword in query_lower
    ]
    return " ".join([query, *additions])


def _is_eligibility_query(query):
    query_lower = query.lower()
    return (
        "eligibility" in query_lower
        or "qualifying subject" in query_lower
        or "qualifying subjects" in query_lower
        or (
            ("12th" in query_lower or "higher secondary" in query_lower)
            and ("subject" in query_lower or "apply" in query_lower or "need" in query_lower)
        )
        or (
            "subject" in query_lower
            and ("apply" in query_lower or "needed" in query_lower or "need" in query_lower)
        )
    )


def _is_fee_query(query):
    query_lower = query.lower()
    return "fee" in query_lower or "fees" in query_lower or "amount" in query_lower


def _is_duration_query(query):
    query_lower = query.lower()
    return "duration" in query_lower or "semester" in query_lower or "semesters" in query_lower


def _needs_course_name(query, degree_terms):
    query_lower = query.lower()
    return not degree_terms and (
        _is_eligibility_query(query)
        or _is_fee_query(query)
        or _is_duration_query(query)
    )


def _is_admission_query(query):
    query_lower = query.lower()
    return (
        "admission" in query_lower
        or "apply" in query_lower
        or "application" in query_lower
        or "selection" in query_lower
        or "interview" in query_lower
    )


def _is_application_instructions_query(query):
    query_lower = query.lower()
    keywords = (
        "online application",
        "application form",
        "submit application",
        "edit application",
        "edit the application",
        "after paying",
        "paying the fee",
        "upload",
        "upload document",
        "upload documents",
        "upload photo",
        "upload photograph",
        "uploaded photo",
        "uploaded photograph",
        "photo upload",
        "photograph upload",
        "required documents",
        "photo",
        "photograph",
        "image",
        "passport-size",
        "passport size",
        "file size",
        "maximum size",
        "signature",
        "community certificate",
        "baptism certificate",
        "mark sheets",
        "uan",
        "unique application number",
        "preview page",
        "document info attachment",
        "applicant login",
        "non-refundable",
        "non refundable",
        "application fee",
        "shortlisted",
        "provisionally selected",
        "further queries",
    )
    return any(keyword in query_lower for keyword in keywords)


def _is_contact_query(query):
    query_lower = query.lower()
    contact_terms = (
        "contact",
        "phone",
        "telephone",
        "mobile",
        "call",
        "number",
        "address",
        "located",
        "location",
        "where is the college",
    )
    return any(term in query_lower for term in contact_terms)


def _query_topic(query):
    if "hostel" in query.lower():
        return "hostel"
    if _is_fee_query(query):
        return "fees"
    if _is_eligibility_query(query):
        return "eligibility"
    if _is_duration_query(query):
        return "duration"
    if _is_admission_query(query):
        return "admission"
    return None


def _course_name_from_query(query):
    query_terms = _query_terms(query)
    matches = _find_courses(query_terms, query)
    if not matches:
        return None
    return matches[0]["full_name"]


def _history_context(history):
    last_course = None
    last_topic = None

    for turn in reversed(history or []):
        if not isinstance(turn, dict):
            continue

        for field in ("user", "bot"):
            message = turn.get(field, "")
            if not isinstance(message, str) or not message.strip():
                continue

            if not last_course:
                last_course = _course_name_from_query(message)

            if not last_topic:
                last_topic = _query_topic(message)

            if last_course and last_topic:
                return {"course": last_course, "topic": last_topic}

    return {"course": last_course, "topic": last_topic}


def _is_follow_up_query(query, query_terms):
    query_lower = query.lower()
    if any(term in query_terms for term in FOLLOW_UP_TERMS):
        return True

    follow_up_phrases = (
        "what about",
        "how about",
        "tell me more",
        "more details",
        "and fee",
        "and fees",
        "and eligibility",
        "and duration",
    )
    if any(phrase in query_lower for phrase in follow_up_phrases):
        return True

    return len(query_terms) <= 4 and not _degree_terms(query_terms) and not _meaningful_terms(query_terms)


def _funding_preference(query):
    query_lower = query.lower()
    if (
        "self-financing" in query_lower
        or "self financing" in query_lower
        or "self-finance" in query_lower
        or "self finance" in query_lower
    ):
        return "self-financing"

    if "aided" in query_lower:
        return "aided"

    return None


def _shift_preference(query):
    match = re.search(r"\bshift\s*(ii|i)\b", query, re.IGNORECASE)
    return f"shift {match.group(1).lower()}" if match else None


def _apply_history_context(query, history):
    if not history:
        return query

    query_terms = _query_terms(query)
    context = _history_context(history)
    course_name = context["course"]
    topic = _query_topic(query) or context["topic"]

    if not course_name:
        return query

    if (_funding_preference(query) or _shift_preference(query)) and topic:
        topic_prompts = {
            "fees": f"fee structure for {course_name}",
            "eligibility": f"eligibility for {course_name}",
            "duration": f"duration for {course_name}",
            "admission": f"admission process for {course_name}",
            "hostel": course_name,
        }
        return f"{topic_prompts.get(topic, course_name)} {query.strip()}".strip()

    if (_funding_preference(query) or _shift_preference(query)) and course_name:
        return f"{course_name} {query.strip()}".strip()

    if _course_name_from_query(query):
        return query

    if _query_topic(query):
        return f"{query.strip()} for {course_name}".strip()

    if _is_follow_up_query(query, query_terms) and topic:
        topic_prompts = {
            "fees": f"fee structure for {course_name}",
            "eligibility": f"eligibility for {course_name}",
            "duration": f"duration for {course_name}",
            "admission": f"admission process for {course_name}",
            "hostel": query.strip(),
        }
        return topic_prompts.get(topic, f"{query.strip()} for {course_name}")

    return query


def _degree_from_match(match):
    for key in DEGREES:
        if match.groupdict().get(key):
            return key
    return None


def _subject_start_index(text):
    cues = [
        r"\bAny group in Higher Secondary\b",
        r"\bAny group in Higher Secondary / Equivalent Boards\b",
        r"\bAny undergraduate degree\b",
        r"\bAn undergraduate degree\b",
        r"\bB\.?\s*A\.?\b",
        r"\bB\.?\s*Sc\.?\b",
        r"\bB\.?\s*Com\.?\b",
        r"\bCommerce\s*/?\s*Business Studies\b",
        r"\bMathematics\s*/\s*Business Mathematics\b",
        r"\bMathematics and Physics\b",
        r"\bPhysics,\s*Mathematics and Chemistry\b",
        r"\bChemistry,\s*Physics and Mathematics\b",
        r"\bBiology,\s*Chemistry\b",
        r"\bBotany,\s*Zoology\b",
        r"\bMathematics\b",
    ]
    starts = []
    for cue in cues:
        match = re.search(cue, text, re.IGNORECASE)
        if match:
            starts.append(match.start())
    return min(starts) if starts else None


def _amounts_from_text(text):
    return [re.sub(r"\s+", "", amount) for amount in re.findall(r"\d{1,3},\s*\d{3}", text)]


def _strip_trailing_amounts(text):
    return _compact_text(re.sub(r"(?:\s+\d{1,3},\s*\d{3}){2,3}\s*$", "", text))


def _fees_from_amounts(amounts):
    if len(amounts) >= 3:
        return {
            "hsc": amounts[-3],
            "cbse": amounts[-2],
            "others": amounts[-1],
        }

    if len(amounts) == 2:
        return {
            "university_of_madras": amounts[-2],
            "other_university": amounts[-1],
        }

    return None


def _page_course_context(text):
    text_lower = text.lower()
    funding_model = None

    if "self-financing section" in text_lower or "self financing section" in text_lower:
        funding_model = "self-financing"
    elif "aided section" in text_lower:
        funding_model = "aided"

    shift = _shift_preference(text)
    return {"funding_model": funding_model, "shift": shift}


def _programme_sections(text):
    header_pattern = re.compile(
        r"(?P<header>(?:UNDERGRADUATE|POSTGRADUATE)\s+PROGRAMMES.*?OFFERED UNDER THE\s+"
        r"(?P<section>AIDED|SELF-FINANCING)\s+SECTION\s+[^\n]*?SHIFT\s+(?P<shift>II|I))",
        re.IGNORECASE,
    )
    matches = list(re.finditer(header_pattern, text))
    if not matches:
        return [(text, _page_course_context(text))]

    sections = []
    for index, match in enumerate(matches):
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section_text = _compact_text(text[start:end])
        context = {
            "funding_model": "self-financing" if match.group("section").lower() == "self-financing" else "aided",
            "shift": f"shift {match.group('shift').lower()}",
        }
        sections.append((section_text, context))

    return sections


def _display_funding_model(funding_model):
    if funding_model == "self-financing":
        return "Self-Financing"
    if funding_model == "aided":
        return "Aided"
    return ""


def _display_shift(shift):
    if shift == "shift i":
        return "Shift I"
    if shift == "shift ii":
        return "Shift II"
    return ""


def _course_variant_label(course):
    funding_model = _display_funding_model(course.get("funding_model"))
    shift = _display_shift(course.get("shift"))

    if funding_model and shift:
        return f"{funding_model} ({shift})"
    return funding_model or shift


def _course_choice_label(course):
    variant_label = _course_variant_label(course)
    return f"{course['full_name']} - {variant_label}" if variant_label else course["full_name"]


def _serialize_course_option(course):
    return {
        "label": _course_choice_label(course),
        "base_label": course["full_name"],
        "variant_label": _course_variant_label(course),
        "selection_query": _course_choice_label(course),
    }


def _group_courses_by_name(courses):
    groups = {}
    for course in courses:
        groups.setdefault(course["full_name"], []).append(course)
    return groups


def _degree_is_offered(degree_key):
    return any(course["degree"] == degree_key for course in course_catalog)


def _normalized_course_key(text):
    return " ".join(_query_terms(text))


def _exact_course_matches(query, courses):
    query_key = _normalized_course_key(query)
    if not query_key:
        return []

    exact = []
    for course in courses:
        if _normalized_course_key(course["full_name"]) == query_key:
            exact.append(course)

    return exact


def _split_course_segment(degree_key, segment, context=None):
    context = context or {}
    degree_display = DEGREES[degree_key]["display"]
    amounts = _amounts_from_text(segment)
    fees = _fees_from_amounts(amounts)
    segment = _strip_trailing_amounts(segment)
    duration_match = re.search(r"\d+\s*years?/\s*\d+\s*semesters?", segment, re.IGNORECASE)
    duration = DEGREES[degree_key]["default_duration"]

    if duration_match:
        duration = _compact_text(duration_match.group(0))
        before_duration = _compact_text(segment[:duration_match.start()])
        after_duration = _compact_text(segment[duration_match.end():])
    else:
        before_duration = ""
        after_duration = _compact_text(segment)

    if before_duration:
        name = before_duration
        eligibility = after_duration
    else:
        split_at = _subject_start_index(after_duration)
        if split_at is None:
            name = after_duration
            eligibility = ""
        else:
            name = _compact_text(after_duration[:split_at])
            eligibility = _compact_text(after_duration[split_at:])

    if not name:
        name = degree_display

    return {
        "degree": degree_key,
        "degree_display": degree_display,
        "name": name,
        "full_name": f"{degree_display} {name}".strip(),
        "duration": duration,
        "eligibility": _strip_trailing_amounts(eligibility),
        "fees": fees,
        "funding_model": context.get("funding_model"),
        "shift": context.get("shift"),
        "raw": _compact_text(f"{degree_display} {segment}"),
    }


def _extract_course_rows_from_text(text, allowed_degrees=None, context=None):
    rows = []
    matches = list(re.finditer(_degree_boundaries(allowed_degrees), text, re.IGNORECASE))

    for index, match in enumerate(matches):
        degree_key = _degree_from_match(match)
        if not degree_key:
            continue

        end = matches[index + 1].start() if index + 1 < len(matches) else min(len(text), match.end() + 500)
        segment = _compact_text(text[match.end():end])
        if len(segment) < 3:
            continue

        row = _split_course_segment(degree_key, segment, context=context)
        row_key = (row["full_name"].lower(), row.get("funding_model"), row.get("shift"))
        existing_keys = {
            (item["full_name"].lower(), item.get("funding_model"), item.get("shift"))
            for item in rows
        }
        if row_key not in existing_keys:
            rows.append(row)

    return rows


def _extract_fee_rows_from_text(text, context=None):
    context = context or {}
    fees = []
    degree_pattern = _degree_boundaries()
    amount = r"\d{1,3},\s*\d{3}"
    row_pattern = (
        rf"\b\d+\s+"
        rf"(?P<course>{degree_pattern}(?:\s+[A-Za-z&().–-]+){{0,10}}?)\s+"
        rf"(?P<amounts>(?:{amount}\s+){{1,2}}{amount})"
    )

    for match in re.finditer(row_pattern, text, re.IGNORECASE):
        course_match = re.search(_degree_boundaries(), match.group("course"), re.IGNORECASE)
        degree_key = _degree_from_match(course_match) if course_match else None
        if not degree_key:
            continue

        course_name = _compact_text(re.sub(DEGREES[degree_key]["pattern"], "", match.group("course"), flags=re.IGNORECASE))
        fee_values = _fees_from_amounts(_amounts_from_text(match.group("amounts")))
        if not fee_values:
            continue

        fees.append(
            {
                "degree": degree_key,
                "name": course_name or DEGREES[degree_key]["display"],
                "funding_model": context.get("funding_model"),
                "shift": context.get("shift"),
                **fee_values,
            }
        )

    return fees


def _course_score(course, degree_terms, subject_terms):
    score = 0
    name_searchable = _normalize_degree_names(
        f"{course['full_name']} {course.get('funding_model', '')} {course.get('shift', '')}"
    ).lower()
    raw_searchable = _normalize_degree_names(course.get("raw", "")).lower()

    if degree_terms and course["degree"] in degree_terms:
        score += 10

    for term in subject_terms:
        if _text_has_term(name_searchable, term):
            score += 5
        elif _text_has_term(raw_searchable, term):
            score += 1

    return score


def _find_courses(query_terms, query=""):
    degree_terms = _degree_terms(query_terms)
    subject_terms = _meaningful_terms(query_terms)
    funding_preference = _funding_preference(query)
    shift_preference = _shift_preference(query)

    filtered_courses = []
    for course in course_catalog:
        if degree_terms and course["degree"] not in degree_terms:
            continue

        if funding_preference and course.get("funding_model") != funding_preference:
            continue

        if shift_preference and course.get("shift") != shift_preference:
            continue

        filtered_courses.append(course)

    exact_matches = _exact_course_matches(query, filtered_courses)
    if exact_matches:
        return exact_matches

    scored = []
    for course in filtered_courses:

        score = _course_score(course, degree_terms, subject_terms)

        if funding_preference and course.get("funding_model") == funding_preference:
            score += 4

        if shift_preference and course.get("shift") == shift_preference:
            score += 2

        if degree_terms or score > 0:
            scored.append((score, course))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [course for score, course in scored if score == scored[0][0]] if scored else []


def _merge_fees(courses, fees):
    for fee in fees:
        candidates = [
            course
            for course in courses
            if course["degree"] == fee["degree"]
            and course.get("funding_model") == fee.get("funding_model")
            and course.get("shift") == fee.get("shift")
            and (
                not fee["name"]
                or all(_text_has_term(course["full_name"], term) for term in _query_terms(fee["name"]))
            )
        ]
        if not candidates:
            continue

        best = max(candidates, key=lambda course: len(course["full_name"]))
        best["fees"] = {key: value for key, value in fee.items() if key not in {"degree", "name"}}


def _build_course_catalog(documents):
    rows = []
    fee_rows = []
    ug_degrees = {"ba", "bsc", "bcom", "bba", "bca", "bsw", "bvoc", "bva"}
    pg_degrees = {"ma", "msc", "mcom", "msw"}

    for document in documents:
        page_text = _compact_text(document.page_content)
        for section_text, context in _programme_sections(page_text):
            if "Programme Duration" in section_text:
                if "POSTGRADUATE PROGRAMMES" in section_text and "UNDERGRADUATE PROGRAMMES" not in section_text:
                    rows.extend(_extract_course_rows_from_text(section_text, pg_degrees, context=context))
                elif "UNDERGRADUATE PROGRAMMES" in section_text:
                    rows.extend(_extract_course_rows_from_text(section_text, ug_degrees, context=context))
                else:
                    rows.extend(_extract_course_rows_from_text(section_text, context=context))

            if "FEE STRUCTURE" in section_text:
                fee_rows.extend(_extract_fee_rows_from_text(section_text, context=context))

    _merge_fees(rows, fee_rows)
    return rows


def resolve_course_selection(query):
    query = query.strip()
    if not query:
        return {"status": "not_found"}

    load_model()
    query_terms = _query_terms(query)
    degree_terms = _degree_terms(query_terms)

    if degree_terms and not any(_degree_is_offered(degree) for degree in degree_terms):
        degree_names = ", ".join(DEGREES[degree]["display"] for degree in degree_terms)
        return {
            "status": "not_found",
            "message": f"I could not find {degree_names} in the current prospectus. Please choose a course listed in the prospectus.",
        }

    matches = _find_courses(query_terms, query)
    if not matches:
        return {"status": "not_found"}

    grouped_matches = _group_courses_by_name(matches)

    if len(grouped_matches) == 1:
        full_name, grouped_courses = next(iter(grouped_matches.items()))
        if len(grouped_courses) == 1:
            return {"status": "selected", "course": _serialize_course_option(grouped_courses[0])}
        return {
            "status": "variant_required",
            "course_name": full_name,
            "options": [_serialize_course_option(course) for course in grouped_courses],
        }

    return {
        "status": "course_required",
        "options": [
            {"label": full_name, "selection_query": full_name}
            for full_name in list(grouped_matches.keys())[:8]
        ],
    }


def _course_not_found_message(degree_terms):
    return "I’m sorry, I don’t have a reliable answer for that course right now. Please try another course name or ask about fees, eligibility, duration, or admission."


def _polished_fallback_message():
    return (
        "I’m sorry, I couldn’t find a confident answer for that just yet. "
        "Please try asking with the course name or the specific detail you need, such as fees, eligibility, duration, hostel, or admission."
    )


def _pdf_paths():
    paths = [path.strip() for path in PROSPECTUS_PDFS.split(",") if path.strip()]
    return paths or [PROSPECTUS_PDF]


def _format_fees(fees):
    if {"hsc", "cbse", "others"}.issubset(fees):
        return (
            f"HSC: Rs. {fees['hsc']}, "
            f"CBSE/ISC: Rs. {fees['cbse']}, "
            f"Others: Rs. {fees['others']}"
        )

    if {"university_of_madras", "other_university"}.issubset(fees):
        return (
            f"University of Madras: Rs. {fees['university_of_madras']}, "
            f"Other University: Rs. {fees['other_university']}"
        )

    return ", ".join(f"{key}: Rs. {value}" for key, value in fees.items())


def _contact_answer(query):
    query_lower = query.lower()
    phone = "+91 44 28111987 / 28111951"
    address = "17, Cathedral Road, Chennai 600086, India"

    if not _is_contact_query(query):
        return None

    if "address" in query_lower or "located" in query_lower or "location" in query_lower or "where" in query_lower:
        return f"Stella Maris College is located at {address}."

    if any(term in query_lower for term in ("phone", "telephone", "mobile", "call", "number", "contact")):
        return f"You can contact Stella Maris College at {phone}. The address is {address}."

    return f"You can contact Stella Maris College at {phone}. The address is {address}."


def _hostel_answer(query):
    query_lower = query.lower()
    if "hostel" not in query_lower:
        return None

    if any(term in query_lower for term in ("details", "facility", "facilities", "about", "information")):
        return (
            "Stella Maris College hostels are managed under the Principal and Wardens. "
            "Hostel accommodation includes Snehalaya, Nava Nirmana, Our Lady's Single and Combined, "
            "Klemens I, II and III, and Assisi. The mess provides vegetarian and non-vegetarian meals. "
            "Hostel residents must follow discipline, outing, and anti-ragging rules. "
            "Details for St. Joseph's Hostel are shared in person on enquiry."
        )

    if "mess" in query_lower:
        return "The hostel mess fee is Rs. 3,000 per month. Milk and eggs are served at an additional cost."

    if "fee" in query_lower or "fees" in query_lower or "charge" in query_lower:
        return (
            "Hostel term fee totals are: Snehalaya - Rs. 82,800; "
            "Nava Nirmana - Rs. 38,800; Our Lady's Single - Rs. 32,800; "
            "Our Lady's Combined - Rs. 29,800; Klemens I - Rs. 38,800; "
            "Klemens II - Rs. 35,800; Klemens III - Rs. 32,800; "
            "Assisi - Rs. 35,800."
        )

    if "ragging" in query_lower:
        return (
            "Ragging in any form is strictly forbidden in the hostel. "
            "Students found guilty can face cancellation of admission, "
            "suspension from the College or Hostel, and a fine of Rs. 25,000."
        )

    if "outing" in query_lower or "gate pass" in query_lower or "weekend" in query_lower:
        return (
            "Hostel students must sign the register before leaving and immediately on return. "
            "Special gate passes are needed for urgent work, and a weekend out can be availed once a month "
            "with parent authorization and the Warden's approval."
        )

    return (
        "I’d be happy to help with hostel information. "
        "You can ask about hostel fees, mess charges, room types, outing rules, or discipline."
    )

def _application_instruction_segments():
    return [_clean_text(segment) for segment in ONLINE_APPLICATION_KNOWLEDGE.split("\n\n") if segment.strip()]


def _application_answer(query):
    query_lower = query.lower()

    if not (_is_application_instructions_query(query) or ("instruction" in query_lower and "application" in query_lower)):
        return None

    if "uan" in query_lower or "unique application number" in query_lower:
        return (
            'The Unique Application Number (UAN) is generated when you click the "Save" option on the Preview page. '
            "Use the UAN as the Username and your Date of Birth as the Password to log in and upload documents."
        )

    if "password" in query_lower and ("login" in query_lower or "applicant" in query_lower):
        return "Use your UAN as the Username and your Date of Birth as the Password for Applicant login."

    if "username" in query_lower and ("login" in query_lower or "applicant" in query_lower):
        return 'Use the UAN generated on the Preview page as your Username for Applicant login.'

    if ("login" in query_lower or "log in" in query_lower) and ("upload" in query_lower or "document" in query_lower):
        return (
            "After entering academic marks and clicking the Save option on the Preview page, you will get your UAN. "
            "Use the UAN as the Username and your Date of Birth as the Password to log in and upload documents."
        )

    if "photo" in query_lower or "photograph" in query_lower or "passport size" in query_lower or "passport-size" in query_lower:
        return "The passport-size photograph must be in JPG/JPEG format and the maximum file size is 50 KB."

    if "signature" in query_lower and ("parent" in query_lower or "guardian" in query_lower):
        return "The parent or guardian signature must be in JPG/JPEG format and the maximum file size is 20 KB."

    if "signature" in query_lower:
        return "The applicant signature must be in JPG/JPEG format and the maximum file size is 20 KB."

    if "community certificate" in query_lower:
        return (
            'The Community Certificate is required except for OC and "Others" categories. '
            "It must be uploaded in JPG/JPEG/GIF format with a maximum size of 2 MB."
        )

    if "baptism certificate" in query_lower:
        return (
            "The Baptism Certificate is required only for Catholic applicants. "
            "It must be uploaded in JPG/JPEG/GIF format with a maximum size of 2 MB."
        )

    if "mark sheet" in query_lower or "marksheet" in query_lower or "semester" in query_lower:
        return (
            "Postgraduate applicants must upload self-attested copies of all available semester mark sheets "
            "compiled into a single PDF with a maximum size of 5 MB."
        )

    if "document" in query_lower and ("required" in query_lower or "upload" in query_lower):
        return (
            "Required uploads are: passport-size photograph (JPG/JPEG, 50 KB), applicant signature "
            "(JPG/JPEG, 20 KB), parent or guardian signature (JPG/JPEG, 20 KB), Community Certificate "
            '(except OC and "Others") (JPG/JPEG/GIF, 2 MB), Baptism Certificate for Catholic applicants '
            "(JPG/JPEG/GIF, 2 MB), and for postgraduate applicants all available semester mark sheets "
            "compiled into one PDF (5 MB)."
        )

    if "edit" in query_lower or "update" in query_lower:
        return (
            'Applicants may edit application details before paying the application fee by using the "Login" button. '
            "Editing or updating details is not possible after the application fee has been paid."
        )

    if "payment" in query_lower or "pay" in query_lower or "fee" in query_lower:
        if "receipt" in query_lower or "updated" in query_lower:
            return "The receipt of the application fee will be updated in the Applicant login 24 hours after the transaction."
        return (
            "The application fee must be paid online through internet banking, credit card, or debit card only. "
            "The application fee is non-refundable under any circumstances."
        )

    if "interview" in query_lower or "shortlisted" in query_lower or "selected" in query_lower:
        return (
            "Interview shortlisting information will be sent by email and SMS and uploaded on the College website. "
            "Applicants must attend on the specified date and time, and being called for an interview does not guarantee admission. "
            "The list of provisionally selected applicants will be uploaded after 8:00 p.m."
        )

    if "document info attachment" in query_lower or ("documents required" in query_lower and "interview" in query_lower):
        return (
            "Details about documents required at the time of interview can be accessed by clicking the "
            "Document Info Attachment button."
        )

    if "contact" in query_lower or "email" in query_lower or "query" in query_lower:
        return "For further queries, please email admissions@stellamariscollege.edu.in."

    return (
        "For the online application form: upload the required documents in the specified formats and sizes, "
        "use the UAN generated on the Preview page for login, complete fee payment online, and note that the "
        "application fee is non-refundable. Ask me if you need document, UAN, payment, login, or interview details."
    )


def _course_answer(query, query_terms):
    if "hostel" in query.lower():
        return None

    degree_terms = _degree_terms(query_terms)
    meaningful_terms = _meaningful_terms(query_terms)

    if not degree_terms and not meaningful_terms:
        return None

    matches = _find_courses(query_terms, query)

    if _needs_course_name(query, degree_terms) and not matches:
        return (
            "Please mention the specific course name so I can help you more accurately. "
            "For example: BCA eligibility, B.Sc. Mathematics fees, or MSW admission."
        )

    if not matches:
        if degree_terms:
            return _course_not_found_message(degree_terms)
        return None

    grouped_matches = _group_courses_by_name(matches)
    if len(grouped_matches) == 1:
        full_name, grouped_courses = next(iter(grouped_matches.items()))
        if len(grouped_courses) > 1:
            options = ", ".join(_course_variant_label(course) for course in grouped_courses if _course_variant_label(course))
            if options:
                return f"I found multiple options for {full_name}. Please specify: {options}."

    if len(matches) > 1 and _meaningful_terms(query_terms):
        # Same score but a meaningful query was supplied; keep the first best match.
        matches = matches[:1]

    if len(matches) > 1:
        options = ", ".join(course["full_name"] for course in matches[:6])
        return f"Please specify the course more clearly. I found multiple matches: {options}."

    course = matches[0]
    course_name = _course_choice_label(course)

    if _is_fee_query(query):
        if not course.get("fees"):
            return f"I found {course_name}, but I’m not able to confirm the fee structure clearly right now."

        fees = course["fees"]
        return f"For {course_name}, the fee structure is {_format_fees(fees)}."

    if _is_duration_query(query):
        return f"For {course_name}, the duration is {course['duration']}."

    if _is_eligibility_query(query):
        if course["eligibility"]:
            if course["degree"].startswith("b"):
                return f"For {course_name}, the required 12th standard eligibility is {course['eligibility']}."
            return f"For {course_name}, the eligibility is {course['eligibility']}."
        return f"I found {course_name}, but I’m not able to confirm the eligibility details clearly right now."

    return course["raw"]


def _score_passage(query_terms, passage, semantic_score):
    if not query_terms:
        return semantic_score

    matched = sum(1 for term in query_terms if _text_has_term(passage, term))
    coverage = matched / len(query_terms)
    return semantic_score + (coverage * 0.12)


def _split_passages(text):
    raw_parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    passages = []
    buffer = []

    for part in raw_parts:
        part = _compact_text(part)
        if not part:
            continue

        buffer.append(part)
        combined = " ".join(buffer)

        if len(combined) >= 120 or part.endswith((".", "!", "?")):
            passages.append(combined)
            buffer = []

    if buffer:
        passages.append(" ".join(buffer))

    return [passage for passage in passages if len(passage) >= 35]


def _dedupe_passages(passages):
    seen = set()
    unique = []

    for passage in passages:
        key = re.sub(r"\W+", "", passage.lower())
        if key in seen:
            continue

        seen.add(key)
        unique.append(passage)

    return unique


def load_model(force_reload=False):
    global texts, corpus_text, course_catalog, vectorizer, tfidf_matrix

    if texts and not force_reload:
        return

    paths = _pdf_paths()
    missing_paths = [path for path in paths if not os.path.exists(path)]
    if missing_paths:
        raise FileNotFoundError(f"Prospectus PDF not found: {', '.join(missing_paths)}")

    print(f"Training from PDFs: {', '.join(paths)}")

    documents = []
    for path in paths:
        documents.extend(PyPDFLoader(path).load())
    course_catalog = _build_course_catalog(documents)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=180,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    docs = splitter.split_documents(documents)
    texts = [_clean_text(doc.page_content) for doc in docs if doc.page_content.strip()]
    texts.extend(_application_instruction_segments())
    corpus_text = "\n".join(texts)

    vectorizer = FeatureUnion(
        [
            (
                "word_tfidf",
                TfidfVectorizer(
                    stop_words="english",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    max_df=0.95,
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    sublinear_tf=True,
                ),
            ),
        ]
    )
    tfidf_matrix = vectorizer.fit_transform(texts)

    print(f"Model ready with {len(texts)} chunks and {len(course_catalog)} course rows.")


def pdf_response(query, history=None):
    query = query.strip()
    if not query:
        return "Please type your question, and I’ll be happy to help."

    load_model()
    query = _apply_history_context(query, history)

    contact_answer = _contact_answer(query)
    if contact_answer:
        return contact_answer

    hostel_answer = _hostel_answer(query)
    if hostel_answer:
        return hostel_answer

    application_answer = _application_answer(query)
    if application_answer:
        return application_answer

    query_terms = _query_terms(query)
    course_answer = _course_answer(query, query_terms)
    if course_answer:
        return course_answer

    if not _has_enough_query_overlap(query_terms):
        return _polished_fallback_message()

    expanded_query = _expand_query(query)
    query_vec = vectorizer.transform([expanded_query])
    chunk_scores = cosine_similarity(query_vec, tfidf_matrix).ravel()
    top_indices = chunk_scores.argsort()[-8:][::-1]

    if chunk_scores[top_indices[0]] < MIN_CHUNK_SCORE:
        return _polished_fallback_message()

    candidate_passages = []
    for index in top_indices:
        if chunk_scores[index] >= MIN_CHUNK_SCORE:
            candidate_passages.extend(_split_passages(texts[index]))

    candidate_passages = _dedupe_passages(candidate_passages)
    if not candidate_passages:
        return texts[top_indices[0]][:700].strip()

    passage_vecs = vectorizer.transform(candidate_passages)
    passage_scores = cosine_similarity(query_vec, passage_vecs).ravel()
    final_scores = [
        _score_passage(query_terms, passage, passage_scores[index])
        for index, passage in enumerate(candidate_passages)
    ]
    ranked_passage_indices = sorted(
        range(len(candidate_passages)),
        key=lambda index: final_scores[index],
        reverse=True,
    )

    selected = []
    for index in ranked_passage_indices:
        if final_scores[index] <= 0:
            continue

        selected.append(candidate_passages[index])
        if len(selected) >= MAX_ANSWER_PARTS:
            break

    if not selected:
        return texts[top_indices[0]][:700].strip()

    return " ".join(selected).strip()
