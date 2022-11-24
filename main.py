import azure.persons as persons # import sqlite.persons as persons
import azure.events as events # import sqlite.events as events
import azure.persons_metric as p_m # import sqlite.persons_metric as p_m
import azure.urls as urls # import sqlite.urls as urls
import pyodbc
#import sqlite3

cnxn = pyodbc.connect("""Driver={ODBC Driver 13 for SQL Server};
                        Server=tcp:prenaissance.database.windows.net,1433;
                        Database=customerpp;Uid=alex;Pwd=Test1234;Encrypt=yes;
                        TrustServerCertificate=no;Connection Timeout=30;""")


#cnxn = sqlite3.connect("customerpp.db") #// this line is needed if you want to create sqllite3 database
#cnxn.execute("PRAGMA foreign_keys = 1") #// this line is needed if you want to create sqllite3 database

# do not execute this python file in order not to modify the database
# but if you do execute this  file make sure the table you insert is emptied in order to avoid dublicate information and unique constraint failure
# also note that order of execution maters

#persons.create_persons_table(connection=cnxn)
#persons.insert_persons_table(connection=cnxn, path='Input_Records-rk946c2nlklj4dcwnhqm.json')
#events.create_events_table(connection=cnxn)
#events.insert_events_table(connection=cnxn, path='Input_Records-rk946c2nlklj4dcwnhqm.json')
#p_m.create_persons_metric_table(cnxn)
#p_m.insert_persons_metric_table(cnxn)


#urls.create_urls_table(cnxn)
#urls.insert_urls_table(cnxn)
