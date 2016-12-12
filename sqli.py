#!/usr/bin/python

import MySQLdb
import sys
import re
import getpass

back   = 'b'
exitC  = 'e'
helpOp = 'h'
insert = 'i'
load   = 'l'
query  = 'q'

fields    = {}
fieldType = {}

def select_databases():
    """ select_databases() 

           Displays a numbered list of databases
           you select by number which DB to use.
           If you enter a 'b' character na <Exit>
           return code is returned

           Returns the selected database name or <Exit> code

    """
    try:
        cursor.execute("show databases");
        results = cursor.fetchall()
        dbNames = []
        for row in results:
            dbNames.append(row[0])
    except:
        print "Error: unable to fetch data"

    print "\nThese databases are available:\n"
    for i in xrange(len(dbNames)):
        print "(%s) %s" % (i,dbNames[i])
    print "(e) <Exit>"
    print ""

    prompt = format("Select database (0-%s): " % (len(dbNames)-1))
    sel = raw_input(prompt)
    if sel == exitC:
        return back
    else:
        sel = int(sel)

    dbNM = dbNames[sel]
    cursor.execute(format("use %s"%dbNM));
    print "Database selected:", dbNM
    return dbNM

def select_tables():
    """ select_tables()

           Called from the main control loop select_tables() displays the
           tables in the current database and provides an index (0:n-1) to
           select a table. It then propmts the user for an index or 'b' to
           return control to the main loop.

    """
    global fields
    global fieldType
    cursor.execute("show tables")
    results = cursor.fetchall()

    tableNames = []
    print "\nThese tables are available in %s: \n" % dbNM
    for i in xrange(len(results)):
        print "(%s) %s" % (i,results[i][0])
    print "(b) <Back>"
    prompt = format("\nSelect table (0-%s): " % (len(results)-1))

    sel = raw_input(prompt)
    if sel == back:
        return back
    else:
        sel = int(sel)

    table      = results[sel][0]
    print "Table selected: %s" % table

    # Describe the records in this table
    print "Table '"+table+"' has this record structure:\n"
    sql = format("describe "+table)
    cursor.execute(sql)
    results   = cursor.fetchall()
    fields    = {}
    fieldType = {}
    k         = 0
    for row in results:
        print "row: %s" % str(row)
        fields[k]    = row[0]
        fieldType[k] = row[1]
        k += 1
    return table

def query_table(table):
    """ query_table(table)

           query_table(table) is called from the main loop. The table
           parameter is provided from a call to select_tables(). Any
           single table query may be entered without specifying the table
           or database names.

    """
    print "(query_table) table: %s" % table
    while True:
        query = raw_input("\nSQL Query: ")
        if query == '':
            return back
        else:
            x = query.split(' ')
            if len(x) >= 2:
                query = x[0]+' '+x[1]+' from '+table
                for s in x[2:]:
                    query = query+' '+s
            cursor.execute(query)
            results = cursor.fetchall()
            for row in results:
                print "{0}".format(row)

def load_table(table):
    """ load_table(table)

           Called from the main control loop it prompts for a file name.
           It then reads the file and inserts a row (one for each line in the file) in the 
           specified table which is provided from a call to select_tables().

    """
    global fields
    global fieldType
    fileName = raw_input("Enter file name: ")
    f   = open(fileName,'r')
    lcnt = 0
    for line in f:
        lcnt += 1
        splitLine = line.split(',')
        newLine   = ""
        fKeys     = sorted(fields.keys())
        kLen = len(fKeys)
        sLen = len(splitLine)
        if kLen != sLen:
            print "Error, field count in files records incorrect"
            print "kLen: %s, sLen: %s" % (kLen, sLen)
            print splitLine
            print fKeys

        v = []
        for item,k in zip(splitLine,fKeys):
            p = fields[k]
            stripItem = item.strip()
            if stripItem == "":
                sv = "NULL";
            else:
                if "int" in fieldType[k]:
                    sv = int(stripItem)
                else:
                    if p in customField.keys():
                        sv = customField[p](stripItem)
                    else:
                        sv = str(stripItem)

            v.append(sv)
        sql = "insert into "+table+" values("
        for val in v:
            sql += '"'+str(val)+'"'
            sql += ','
        sql = sql[:-1]
        sql += ")"
        print "'%s'" % sql
        a = raw_input("Okay? ")
        if a != 'y':
            print "Returning"
            return

        cursor.execute(sql)
        results = cursor.fetchall()
        for line in results:
            print line

def insert_table(table):
    """ insert_table(table)

           Called from the main control loop it inserts a row in the
           specified table which is provided from a call to select_tables().
           It propmpts the user for each field value and displays the
           property of each field.

    """
    global fields
    global fieldType
    p = []
    v = []
    dateRegp = re.compile("[12][09][0-9][0-9]\-[01][0-9]\-[0-3][0-9]")
    colNames = ""
    for k in sorted(fields.keys()):
        colNames += fields[k]+','
    colNames = colNames[:-1]
    for k in sorted(fields.keys()):
        p  = fields[k]
        tp = fieldType[k]
        goodInput = False
        while not goodInput:
            nv = raw_input(" ["+tp+"] "+"\t"+p+": ")
            if "int" in tp:
                try:
                    iv = int(nv)
                    v.append(iv)
                    goodInput = True
                except ValueError:
                    print "Not Integer\n"
                    return
            elif "char" in tp:
                if p in customField.keys():
                    nv = customField[p](nv)
                else:
                    nv = str(nv)

                v.append('"'+nv+'"')
                goodInput = True
            elif "date" in tp:
                if not re.match(dateRegp,nv):
                    print "Not Correct Date format\n"
                else:
                    v.append('"'+nv+'"')
                    goodInput = True
            elif "decimal" in tp:
                try:
                    nv = float(nv)
                    v.append(nv)
                    goodInput = True
                except ValueError:
                    print "Not Floating point\n"

    sql = "insert into "+table+"("+colNames+") values("
    for val in v:
        sql += str(val)
        sql += ","
    sql = sql[:-1]
    sql += ")"
    while True:
        print "SQL to submit: %s" % sql
        ans = raw_input ("insert (y/n)? : ")
        if ans == 'y':
            cursor.execute(sql)
            break
        elif ans == 'n':
            return
        else:
            print "Enter y or n"

    results = cursor.fetchall()
    for line in results:
        print line

if __name__ == '__main__':
    ver = "2.1"
    print ver

    if len(sys.argv) != 3:
        print "Usage: %s userid hostname" % sys.argv[0]
        sys.exit()

    userName = sys.argv[1]
    hostName = sys.argv[2]
    password = getpass.getpass()
    
    # Connect to database
    db = MySQLdb.connect(hostName,userName,password)

    from customFields import *

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    while True:
        dbNM = select_databases()
        if dbNM == back:
            print "<Back> selected"
            print "Done"
            break
        else:
            while True:
                table = select_tables()
                if table == back:
                    print "<Back> selected, returning to database selection..."
                    break
                while True:
                    op = raw_input("\nOperation (i/l/q/b/h): ")
                    if op == back:
                        print "<Back> selected, returning to table selection..."
                        break
                    elif op == query:
                        while True:
                            stat = query_table(table)
                            if stat == back:
                                break
                    elif op == insert:
                        insert_table(table)
                    elif op == load:
                        load_table(table)
                    elif op == helpOp:
                        print "i - Input"
                        print "l - Load"
                        print "q - Query"
                        print "b - <Back>"
                        print "h - Help"


                        
