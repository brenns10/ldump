ldump
====

This directory contains tools and research info about CWRU's LDAP server and the
data it contains. Of particular interest are how to get a clean, complete,
reproducible list of student ID's, names, and (maybe) how they are affiliated
with the school (i.e. Student, Faculty, or Alumni).

The simplest way thus far is to dump as much data as we can and then study it
offline. This minimizes strain on the LDAP server over time (we really don't
want to mess up things that depend on LDAP).
