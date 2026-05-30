"""
services/naming.py
------------------
Auto-generates filenames for resumes and JDs when the user
leaves the name field blank.

Resume names:  pythonresume01, javaresume02, fullstackresume03
JD names:      pythonjd01, javajd02, fullstackjd03
"""

import re
from typing import List


ROLE_MAP = [
    (['python', 'django', 'flask', 'fastapi'],                 'python'),
    (['java', 'spring', 'maven', 'hibernate'],                 'java'),
    (['javascript', 'typescript', 'react', 'angular', 'vue',
      'node', 'nodejs'],                                        'javascript'),
    (['fullstack', 'full stack', 'full-stack'],                'fullstack'),
    (['data science', 'data scientist', 'machine learning',
      'pandas', 'tensorflow', 'pytorch'],                      'datascience'),
    (['data analyst', 'tableau', 'power bi'],                  'dataanalyst'),
    (['devops', 'docker', 'kubernetes', 'terraform'],          'devops'),
    (['aws', 'azure', 'gcp', 'cloud'],                        'cloud'),
    (['golang', 'go developer'],                               'golang'),
    (['kotlin', 'android'],                                    'android'),
    (['ios', 'swift'],                                         'ios'),
    (['php', 'laravel'],                                       'php'),
    (['ruby', 'rails'],                                        'ruby'),
    (['scala', 'spark', 'hadoop'],                            'bigdata'),
    (['mobile', 'flutter', 'react native'],                   'mobile'),
    (['backend', 'back end', 'back-end'],                     'backend'),
    (['frontend', 'front end', 'front-end'],                  'frontend'),
]


def detect_role(title='', skills=None, raw_text='', role_hint=''):
    if role_hint and role_hint.strip():
        cleaned = role_hint.lower().strip()
        for keywords, slug in ROLE_MAP:
            if any(k in cleaned for k in keywords):
                return slug
        return _sanitize_slug(cleaned)[:12] or 'general'

    corpus = ' '.join([
        title.lower(),
        ' '.join((skills or [])).lower(),
        raw_text.lower()[:300],
    ])

    for keywords, slug in ROLE_MAP:
        if any(kw in corpus for kw in keywords):
            return slug

    return 'general'


def generate_resume_name(user, title='', skills=None, raw_text='', role_hint=''):
    from resumes.models import Resume
    role = detect_role(title=title, skills=skills or [], raw_text=raw_text, role_hint=role_hint)
    base = f'{role}resume'
    existing = list(Resume.objects.filter(user=user).values_list('title', flat=True))
    return _next_available_name(base, existing)


def generate_jd_name(user, title='', skills=None, raw_text='', role_hint=''):
    from jobs.models import JobDescription
    role = detect_role(title=title, skills=skills or [], raw_text=raw_text, role_hint=role_hint)
    base = f'{role}jd'
    existing = list(JobDescription.objects.filter(user=user).values_list('title', flat=True))
    return _next_available_name(base, existing)


def sanitize_name(name):
    if not name:
        return ''
    name = name.strip()
    name = re.sub(r'[^\w\s\-\.]', '', name)
    name = re.sub(r'\s{2,}', ' ', name)
    return name[:100]


def preview_resume_filename(title='', skills=None, role_hint=''):
    if title and title.strip():
        return sanitize_name(title.strip())
    role = detect_role(title='', skills=skills or [], role_hint=role_hint)
    return f'{role}resume01'


def preview_jd_filename(title='', skills=None, role_hint=''):
    if title and title.strip():
        return sanitize_name(title.strip())
    role = detect_role(title='', skills=skills or [], role_hint=role_hint)
    return f'{role}jd01'


def _sanitize_slug(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def _next_available_name(base, existing_names):
    existing_lower = {n.lower() for n in existing_names}
    for i in range(1, 200):
        candidate = f'{base}{i:02d}'
        if candidate not in existing_lower:
            return candidate
    import time
    return f'{base}{int(time.time()) % 10000}'
