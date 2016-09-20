#!/usr/bin/python

def isbnFunc ( nv ):
    sv = str(nv)
    if len(sv) != 13 and len(sv) != 17:
        print "ISBN field must have 13 or 17 digits"
        print "Field will be NULL"
        return ""

    nv = sv[0:3]+'-'+sv[3]+'-'+sv[4:7]+'-'+sv[7:12]+'-'+sv[12]
    return nv

customField = {'ISBN': isbnFunc }
