#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import webbrowser
import codecs
from os.path import expanduser, dirname, realpath

# Basic file info
home = expanduser("~")
sqlite_file = home + '/Library/Containers/com.culturedcode.ThingsMac/Data/Library/Application Support/Cultured Code/Things/Things.sqlite3'
fout = dirname(realpath(__file__)) + '/kanban.html'

mstr1 = []
mstr2 = []

def create_connection(db_file):
    conn = sqlite3.connect(sqlite_file)
    return conn    
    
def select_all_tasks(conn):
    cur = conn.cursor()

    #This will get all area names and UUID 
    cur.execute("SELECT uuid, title FROM TMArea")
    rowArea = cur.fetchall()
    nbArea=len(rowArea)

    #This will get all active project as long as they have due date
    cur.execute("SELECT uuid, title, date(dueDate, 'unixepoch'), area FROM TMTask WHERE type = 1 AND status = 0 AND dueDate != 0 ORDER BY dueDate" )
    rowProj = cur.fetchall()
    nbProj=len(rowProj)

    #This will get all active project that do not have a due date
    cur.execute("SELECT uuid, title, area FROM TMTask WHERE type = 1 AND (status = 0 AND dueDate IS NULL) ORDER BY area" )
    rowProj2 = cur.fetchall()
    nbProj2=len(rowProj2)

    #Extracting the # of active tasks for all projects
    cur.execute("SELECT uuid, title, project, area FROM TMTask WHERE type = 0" )
    rowTask = cur.fetchall()
    nbTask=len(rowTask)

    #print('Nb Areas:',nbArea, '  Nb Projects:',nbProj, nbProj2, '  Nb Tasks:',nbTask)
    
    #Extracting the # of active (i.e. excluding completed) tasks for specific projects with existing due date
    ip=0
    itot=0
    for row in rowProj:
        getID=rowProj[ip][0]
        cur.execute("SELECT uuid, title, date(dueDate, 'unixepoch') FROM TMTask WHERE status = 0 AND project = '%s'" % getID)
        icount = cur.fetchall()
        ic=len(icount)
        #concatenate the task count back into the tuple containing all previous information
        rowProj[ip] += (ic,)
        itot=itot+ic
        mstr1.append("""<div id="box1">"""+ "<a href="+"things:///show?id="+rowProj[ip][0]+">"+rowProj[ip][1]+"</a>"+"   ("+str(rowProj[ip][4])+")   "+"""<span style="float:right;">"""+str(rowProj[ip][2])+"</span></div>")
        ip=ip+1

     #Extracting the # of active (i.e. excluding completed) tasks for the rest of the projects
    ip=0
    for row in rowProj2:
        getID=rowProj2[ip][0]
        cur.execute("SELECT uuid, title, date(dueDate, 'unixepoch') FROM TMTask WHERE status = 0 AND project = '%s'" % getID)
        icount = cur.fetchall()
        ic=len(icount)
        #concatenate the task count back into the tuple containing all previous information
        rowProj2[ip] += (ic,)
        itot=itot+ic
        if ic==0:
            mstr2.append("""<div id="box3">"""+ "<a href="+"things:///show?id="+rowProj2[ip][0]+">"+rowProj2[ip][1]+"</a>"+"   ("+str(rowProj2[ip][3])+")   "+"</div>")
        else:
            mstr2.append("""<div id="box4">"""+ "<a href="+"things:///show?id="+rowProj2[ip][0]+">"+rowProj2[ip][1]+"</a>"+"   ("+str(rowProj2[ip][3])+")   "+"</div>")
        ip=ip+1
   
    #Create the HTML file on the fly
    f = codecs.open(fout,'w','utf-8')

    message = """<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" href="3col.css">
        </head>

        <body>

        <div id="head">Things 3 - Project-Level Kanban View</div>
        <div id="foot"><br />Copyright &copy;2018 Luc Beaulieu</div>
        
        <div id="left1">
        <div class="inner">
        <h2>Upcoming Projects</h2>"""

    f.write(message)

    # time to fill first column of our Kanban Board
    ip=0
    for row in rowProj: 
        f.write(mstr1[ip])
        ip=ip+1

    # time to fill second column of our Kanban Board
    message = """ 
       </div>
        </div>
        <div id="left2">
        <div class="inner">
        <h2>No active tasks</h2>"""

    f.write(message)

    ip=0
    for row in rowProj2: 
        if rowProj2[ip][3]==0:
            f.write(mstr2[ip])
        ip=ip+1      

# time to fill third column of our Kanban Board
    message = """ 
       </div>
        </div>
        <div id="left3">
        <div class="inner">
        <h2>Other Projects</h2>"""
    f.write(message)

    ip=0
    for row in rowProj2: 
        if rowProj2[ip][3]!=0:
            f.write(mstr2[ip])
        ip=ip+1   

# let's close the whole thing
    message = """
        </div> </div>
        </body>
        </html>"""

    f.write(message)
    f.close()

  

def main():
   
# create a database connection
    conn = create_connection(sqlite_file)
    with conn:
        select_all_tasks(conn)
    
    #Change path to reflect file location and displauy the results
    filename = 'file://'+fout
    webbrowser.open_new_tab(filename)

if __name__ == '__main__':
    main()