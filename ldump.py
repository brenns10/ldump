"""
CWRU LDAP Dumper - download lots of student/faculty data in order to import
them into CWRU Love.
"""

import csv
import ldap3
import pickle
import traceback

DEFAULT_PHOTO = 'https://placehold.it/100x100'

ADDRESS = 'ldap.case.edu'
PORT = 389
BASE = 'ou=People,o=cwru.edu,o=isp'
ATTR = ldap3.ALL_ATTRIBUTES


def ldump():
    """
    Performs a search for every uid. The search is paged (receiving 1000
    results per page). An output file is written every 1000 results:
    attributes.1000.pkl, attributes.2000.pkl, etc. These need to be combined
    afterwards for analysis.
    """
    search = '(uid=*)'
    c = ldap3.Connection(ldap3.Server(ADDRESS, PORT))
    c.open()
    gen = c.extend.standard.paged_search(BASE, search, ldap3.SUBTREE,
                                         paged_size=1000, generator=True,
                                         attributes=ATTR)
    count = 0
    chunk = []
    for entry in gen:
        count += 1
        chunk.append(entry['attributes'])

        if count % 1000 == 0:
            print('count=%d' % count)
            with open('attributes.%d.pkl' % count, 'wb') as pklfile:
                pickle.dump(chunk, pklfile)
            chunk = []
    c.unbind()


def combine(maximum=278000):
    """
    Combine the files produced by ldump into a single one. The major
    performance barrier here is memory, and so we do a lot of explicit deleting
    so that we don't run out.
    """
    all_attributes = []
    for count in range(1000, maximum + 1, 1000):
        name = 'attributes.%d.pkl' % count
        with open(name, 'rb') as pklfile:
            chunk = pickle.load(pklfile)
        all_attributes_new = chunk + all_attributes
        del chunk
        del all_attributes
        all_attributes = all_attributes_new
        print(name)
    return all_attributes


def tocsv(fn='attributes.pkl', out='employees.csv'):
    """
    (deprecated) Take a combined pickle file and create a CSV for import into
    Love. This produces *a lot* of data, and so the resulting CSV was too big
    to import. More sophisticated filtering and experimentation can be found in
    Students.ipynb.
    """
    with open(fn, 'rb') as f:
        attribs = pickle.load(f)
    with open(out, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['username', 'first_name', 'last_name', 'department', 'photo_url'])
        for entry in attribs:
            try:
                username = entry['uid'][0]
                first_name = entry['givenName'][0]
                last_name = entry['sn'][0]
                department = ''
                affil = entry.get('cwruEduPersonScopedAffiliation')
                if 'student@case.edu' in affil:
                    department = 'Student'
                elif 'faculty@case.edu' in affil:
                    department = 'Faculty'
                elif 'alum@case.edu' in affil:
                    department = 'Alumni'
                writer.writerow((username, first_name, last_name, department, DEFAULT_PHOTO))
            except Exception as e:
                traceback.print_exc()
                print(entry)


if __name__ == '__main__':
    ldump()
