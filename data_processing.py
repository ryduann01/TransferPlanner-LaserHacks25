## Defines API endpoints for data processing like discipline mapping

import re

def normalize(text):
    """Normalize a string: lowercase, remove non-alphanumerics."""
    return re.sub(r'[^a-zA-Z0-9]', '', str(text)).lower()

# Mapping from ClubData Tags to UC Majors broad_discipline for normalization purposes
tag_to_discipline = {
    "STEM": "Engineering",
    "ARTS": "Arts & Humanities",
    "HEALTH": "Social Sciences",
    "SOCIAL SCIENCE": "Social Sciences",
    "BUSINESS": "Business",
    "HUMANITIES": "Arts & Humanities",
    "RELIGIOUS": "Arts & Humanities",
    "GENERAL": "Other/Interdisciplinary",
    "LEADERSHIP": "Other/Interdisciplinary",
    "MULTICULTURAL": "Arts & Humanities",
    "LANGUAGE": "Arts & Humanities",
    "DANCE": "Arts & Humanities",
    "PSYCHOLOGY": "Social Sciences",
    "LAW": "Social Sciences",
    "EDUCATION": "Social Sciences",
    "CYBERSECURITY": "Engineering",
    "ROBOTICS": "Engineering",
    "COMPUTER SCIENCE": "Engineering",
    "ARTIFICIAL INTELLIGENCE": "Engineering",
    "ELECTRICAL ENGINEERING": "Engineering",
    "NEUROSCIENCE": "Social Sciences"
}

def assign_major_discipline(major_str):
    """
    Assigns a discipline for a given major string based on the club tag mapping.
    Uses the normalized major and checks if any normalized tag appears as a substring.
    """
    norm_major = normalize(major_str)
    if "computerscience" in norm_major or "computerengineering" in norm_major or re.search(r'\bcomputer\b', norm_major):
        return "Engineering"
    if "cyber" in norm_major or "security" in norm_major:
        return "Engineering"
    if "robotic" in norm_major:
        return "Engineering"
    if "artificialintelligence" in norm_major or "ai" in norm_major:
        return "Engineering"
    if "electrical" in norm_major or "radio" in norm_major:
        return "Engineering"
    # Check for business-related keywords:
    if "business" in norm_major or "management" in norm_major or "economics" in norm_major:
        return "Business"
    # Check for arts/humanities:
    if re.search(r'\bart\b', norm_major) or "literature" in norm_major or "history" in norm_major or "music" in norm_major or "theater" in norm_major or "humanit" in norm_major or "dance" in norm_major:
        return "Arts & Humanities"
    # Check for social sciences:
    if "socialscience" in norm_major or "sociology" in norm_major or "psychology" in norm_major or "political" in norm_major or "anthropology" in norm_major or "geography" in norm_major or "education" in norm_major or "teaching" in norm_major or "law" in norm_major or "legal" in norm_major or "neuro" in norm_major:
        return "Social Sciences"
    return "Other/Interdisciplinary"
