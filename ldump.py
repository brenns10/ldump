"""
CWRU LDAP Dumper - download lots of student/faculty data in order to import
them into CWRU Love.
"""

import collections
import csv
import ldap3
import pickle
import traceback

DEFAULT_PHOTO = 'https://placehold.it/100x100'

ADDRESS = 'ldap.case.edu'
PORT = 389
BASE = 'ou=People,o=cwru.edu,o=isp'
ATTR = ['uid', 'sn', 'givenName', 'mail', 'cwruEduPersonScopedAffiliation',
        'cwruEduPersonScopedAffiliationLastSeen']

STUDENT_QUERY = '(cwruEduPersonScopedAffiliation=student@case.edu)'
UNDERGRAD_QUERY = '(cwruEduPersonScopedAffiliation=undergrad-student@case.edu)'
GRAD_QUERY = '(cwruEduPersonScopedAffiliation=grad-student@*case.edu)'
FACULTY_QUERY = '(cwruEduPersonScopedAffiliation=faculty@case.edu)'
STAFF_QUERY = '(cwruEduPersonScopedAffiliation=staff@case.edu)'
ALUM_QUERY = '(&(cwruEduPersonScopedAffiliation=alum@case.edu)(!(cwruEduPersonScopedAffiliation=student@case.edu)))'

QUERIES = [
    ('Grad Student', GRAD_QUERY),
    ('Undergrad', UNDERGRAD_QUERY),
    ('Faculty', FACULTY_QUERY),
    ('Staff', STAFF_QUERY),
]

Entry = collections.namedtuple('Entry', ['username', 'first_name', 'last_name', 'department', 'photo_url'])


def search(c, query):
    return c.extend.standard.paged_search(BASE, query, ldap3.SUBTREE,
                                          paged_size=1000, generator=True,
                                          attributes=ATTR)


def add_results(c, department, query, entries, ids):
    print('Adding from department ' + department + '...')
    old_len = len(entries)
    count = 0
    for result in search(c, query):
        count += 1
        result = result['attributes']
        if result['uid'][0] not in ids:
            ids.add(result['uid'][0])
            entries.append(Entry(
                username=result['uid'][0],
                first_name=result['givenName'][0],
                last_name=result['sn'][0],
                department=department,
                photo_url='',
            ))
    print('Got %d results from query.' % count)
    added = len(entries) - old_len
    print('%d were newly added, %d must have been overlap' % (added, count-added))
    print('We now have %d entries in the list.' % len(entries))


def write_csv_results(entries, output='employees.csv'):
    with open(output, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('username', 'first_name', 'last_name', 'department', 'photo_url'))
        for entry in entries:
            writer.writerow(entry)


def ldump():
    """
    Searches for students, faculty, and staff, and saves them all.
    """
    c = ldap3.Connection(ldap3.Server(ADDRESS, PORT))
    c.open()
    entries = []
    ids = set()
    for dept, query, in QUERIES:
        add_results(c, dept, query, entries, ids)
    write_csv_results(entries)
    c.unbind()


if __name__ == '__main__':
    ldump()
