"""
services/latex_generator.py
----------------------------
Converts raw resume text into an Overleaf-compatible LaTeX document.

Section detection uses common resume headings:
  EXPERIENCE / WORK EXPERIENCE / EMPLOYMENT
  EDUCATION
  SKILLS / TECHNICAL SKILLS / CORE COMPETENCIES
  PROJECTS
  CERTIFICATIONS / CERTIFICATES
  SUMMARY / PROFILE / OBJECTIVE
  AWARDS / ACHIEVEMENTS

The output uses a clean moderncv-style layout that compiles
without errors on Overleaf with the default pdflatex engine.
"""

import re
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Section heading patterns
# ---------------------------------------------------------------------------

SECTION_PATTERNS = [
    (re.compile(r'^\s*(PROFESSIONAL\s+SUMMARY|SUMMARY|PROFILE|OBJECTIVE)\s*$', re.I), 'summary'),
    (re.compile(r'^\s*(WORK\s+EXPERIENCE|PROFESSIONAL\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT)\s*$', re.I), 'experience'),
    (re.compile(r'^\s*(EDUCATION|ACADEMIC\s+BACKGROUND)\s*$', re.I), 'education'),
    (re.compile(r'^\s*(TECHNICAL\s+SKILLS|CORE\s+COMPETENCIES|SKILLS)\s*$', re.I), 'skills'),
    (re.compile(r'^\s*(PROJECTS|KEY\s+PROJECTS)\s*$', re.I), 'projects'),
    (re.compile(r'^\s*(CERTIFICATIONS?|CERTIFICATES?)\s*$', re.I), 'certifications'),
    (re.compile(r'^\s*(AWARDS?|ACHIEVEMENTS?|HONORS?)\s*$', re.I), 'awards'),
]


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&',  r'\&'),
        ('%',  r'\%'),
        ('$',  r'\$'),
        ('#',  r'\#'),
        ('^',  r'\^{}'),
        ('_',  r'\_'),
        ('{',  r'\{'),
        ('}',  r'\}'),
        ('~',  r'\textasciitilde{}'),
        ('<',  r'\textless{}'),
        ('>',  r'\textgreater{}'),
    ]
    for char, escaped in replacements:
        text = text.replace(char, escaped)
    return text


def _detect_section(line: str):
    """Return section key if line is a section heading, else None."""
    for pattern, key in SECTION_PATTERNS:
        if pattern.match(line):
            return key
    return None


def _parse_header(lines: List[str]) -> Tuple[str, str, str, str, List[str]]:
    """
    Extract name, email, phone, location from the first few lines.
    Returns (name, email, phone, location, remaining_lines).
    """
    name = ''
    email = ''
    phone = ''
    location = ''
    remaining_start = 0

    email_re = re.compile(r'[\w.\-+]+@[\w.\-]+\.\w+')
    phone_re = re.compile(r'[\+\d][\d\s\-\(\)\.]{7,}')

    for i, line in enumerate(lines[:8]):
        stripped = line.strip()
        if not stripped:
            continue
        if not name:
            # First non-empty line is the name
            name = stripped
            remaining_start = i + 1
            continue
        email_match = email_re.search(stripped)
        phone_match = phone_re.search(stripped)
        if email_match and not email:
            email = email_match.group(0)
        if phone_match and not phone:
            phone = phone_match.group(0).strip()
        if i <= 4:
            remaining_start = i + 1

    return name, email, phone, location, lines[remaining_start:]


def _lines_to_items(lines: List[str]) -> str:
    """Convert a list of text lines to LaTeX itemize or plain paragraphs."""
    items = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Lines starting with bullet markers
        stripped = re.sub(r'^[\-\*\u2022\u2023]\s*', '', stripped)
        if stripped:
            items.append(_escape_latex(stripped))

    if not items:
        return ''

    result = '\\begin{itemize}[leftmargin=*,topsep=2pt,itemsep=1pt]\n'
    for item in items:
        result += f'  \\item {item}\n'
    result += '\\end{itemize}\n'
    return result


def generate_latex(raw_text: str, resume_title: str = 'Resume') -> str:
    """
    Convert raw resume text to a full Overleaf-compatible LaTeX document.
    Returns the complete .tex file content as a string.
    """
    if not raw_text or not raw_text.strip():
        return _empty_latex_template(resume_title)

    lines = raw_text.split('\n')

    # Parse header (name + contact info)
    name, email, phone, location, body_lines = _parse_header(lines)
    if not name:
        name = resume_title

    # Split body into sections
    sections = {}
    current_section = 'preamble'
    sections[current_section] = []

    for line in body_lines:
        sec = _detect_section(line)
        if sec:
            current_section = sec
            sections[current_section] = []
        else:
            sections.setdefault(current_section, []).append(line)

    return _build_latex(name, email, phone, sections)


def _build_latex(name: str, email: str, phone: str, sections: dict) -> str:
    name_esc   = _escape_latex(name)
    email_esc  = _escape_latex(email)
    phone_esc  = _escape_latex(phone)

    contact_parts = []
    if email_esc:
        contact_parts.append(f'\\href{{mailto:{email_esc}}}{{{email_esc}}}')
    if phone_esc:
        contact_parts.append(phone_esc)
    contact_line = ' $\\vert$ '.join(contact_parts)

    body = ''

    # Summary section
    if 'summary' in sections:
        content = ' '.join(l.strip() for l in sections['summary'] if l.strip())
        if content:
            body += _section_block('Summary', _escape_latex(content) + '\n\n')

    # Experience section
    if 'experience' in sections:
        body += _section_block('Experience', _lines_to_items(sections['experience']))

    # Education section
    if 'education' in sections:
        body += _section_block('Education', _lines_to_items(sections['education']))

    # Skills section
    if 'skills' in sections:
        skill_lines = [l.strip() for l in sections['skills'] if l.strip()]
        skill_text  = ', '.join(_escape_latex(s) for s in skill_lines)
        if skill_text:
            body += _section_block('Skills', skill_text + '\n\n')

    # Projects section
    if 'projects' in sections:
        body += _section_block('Projects', _lines_to_items(sections['projects']))

    # Certifications section
    if 'certifications' in sections:
        body += _section_block('Certifications', _lines_to_items(sections['certifications']))

    # Awards section
    if 'awards' in sections:
        body += _section_block('Awards', _lines_to_items(sections['awards']))

    # Any remaining unlabelled preamble content
    if 'preamble' in sections:
        preamble_text = ' '.join(l.strip() for l in sections['preamble'] if l.strip())
        if preamble_text:
            body = _section_block('Profile', _escape_latex(preamble_text) + '\n\n') + body

    return f"""% ============================================================
% Overleaf-Compatible Resume Template
% Generated by ResumeAI Screener
% Compile with: pdflatex (Overleaf default)
% ============================================================

\\documentclass[11pt,a4paper]{{article}}

\\usepackage[a4paper, top=20mm, bottom=20mm, left=20mm, right=20mm]{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{hyperref}}
\\usepackage{{titlesec}}
\\usepackage{{parskip}}
\\usepackage{{fontenc}}
\\usepackage{{inputenc}}

% Section formatting
\\titleformat{{\\section}}{{\\large\\bfseries}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing*{{\\section}}{{0pt}}{{8pt}}{{4pt}}

% Remove page number
\\pagestyle{{empty}}

\\begin{{document}}

% ---- Header ----
\\begin{{center}}
  {{\\LARGE \\textbf{{{name_esc}}}}} \\\\[4pt]
  {contact_line}
\\end{{center}}

\\vspace{{4pt}}

% ---- Body ----
{body}
\\end{{document}}
"""


def _section_block(title: str, content: str) -> str:
    if not content or not content.strip():
        return ''
    return f'\\section{{{title}}}\n{content}\n'


def _empty_latex_template(title: str) -> str:
    return f"""% Empty resume template — add content in the editor first.
\\documentclass[11pt,a4paper]{{article}}
\\usepackage[a4paper, margin=20mm]{{geometry}}
\\pagestyle{{empty}}
\\begin{{document}}
\\begin{{center}}{{\\LARGE \\textbf{{{_escape_latex(title)}}}}}\\end{{center}}
\\end{{document}}
"""
