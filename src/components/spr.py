"""

"""

import numpy as np
import sqlite3 as sqlite
import sys
import math

class SQLiteSPR:
    """
    """
    def __init__(self):
        return
    
    def reset(self,class_names):
        self.class_names = class_names
        self.n_classes = len(class_names)
        self.sql_column_class_names = (", %s"*self.n_classes) % class_names
        self.sql_column_class_placeholders = ", '%f' "*self.n_classes 
        
        class_prob_fields = (
                (", `%s` NUMERIC"*self.n_classes)
                % class_names
        )
        
        sql = """
        BEGIN TRANSACTION;
        
        /* =========================================================
        	Input Video Reader
           =========================================================
        */
        DROP TABLE IF EXISTS `videos`;
        CREATE TABLE IF NOT EXISTS `videos` (
        	`pk`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        	`filename`	TEXT,
        	'width' INTEGER,
        	'height' INTEGER,
        	'total_frames' INTEGER,
        	'fps' NUMERIC,
        	`ts` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        
        
        /* =========================================================
        	Video Motion Estimator
           =========================================================
        */
        DROP TABLE IF EXISTS `frames`;
        CREATE TABLE IF NOT EXISTS `frames` (
        	`pk`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        	`fk_video`	INTEGER NOT NULL,
        	`number`	INTEGER,
        	`est_x_offset`	INTEGER,
        	`est_y_offset`	INTEGER
        );
        COMMIT;
        
        
        /* =========================================================
        	CNN Patches
           =========================================================
        */
        DROP TABLE IF EXISTS `patches`;
        CREATE TABLE IF NOT EXISTS `patches` (
        	`pk`	INTEGER PRIMARY KEY AUTOINCREMENT,
        	`fk_frame`	INTEGER NOT NULL,
        	`x0`	INTEGER,
        	`y0`	INTEGER,
        	`x1`	INTEGER,
        	`y1`	INTEGER,
        	`xc`	INTEGER,
        	`yc`	INTEGER
          %s
        );
        """ % class_prob_fields        
        self.conn.executescript(sql)
        
        return
    
    def open(self,filename):
        self.conn = sqlite.connect(filename, isolation_level=None)
        self.conn.execute('pragma journal_mode=wal')
        
    def close(self):
        self.conn.close()
        
    def add_video(self, filename,width, height, total_frames, fps):
        sql = "INSERT INTO videos(filename,width,height,total_frames,fps) VALUES ('%s','%d', '%d', '%d', '%f')" % (filename, width, height, total_frames, fps)
        self.conn.execute(sql)        
        data = self.conn.execute("SELECT last_insert_rowid()")
        pk = data.fetchone()[0]
        return pk
        
    def add_frame(self, fk_video, number, est_x_offset, est_y_offset):
        sql = (
                "INSERT INTO frames(fk_video, number, est_x_offset, est_y_offset)"
                "VALUES ('%d','%d','%d','%d' )" 
                % (fk_video, number, est_x_offset, est_y_offset)
              )
        self.conn.execute(sql)        
        data = self.conn.execute("SELECT last_insert_rowid()")
        pk = data.fetchone()[0]
        return pk    
    
    def add_patch(self, fk_frame, x0, y0, x1, y1, probabilities ):
        xc = (x0+x1)/2
        yc = (y0+y1)/2
        sql = (
                "INSERT INTO patches(fk_frame, x0, y0, x1, y1, xc, yc"
                                     "%s) "
                "VALUES ('%d','%d','%d','%d','%d','%d','%d'%s )" 
                % (self.sql_column_class_names,
                   fk_frame, x0, y0, x1, y1, xc, yc, 
                   self.sql_column_class_placeholders)
              )
        sql = sql % probabilities
        self.conn.execute(sql)        
        #data = self.conn.execute("SELECT last_insert_rowid()")
        #pk = data.fetchone()[0]
        #return pk 


class SQLiteSPRReader:

    def __init__(self):
        return

    def open(self,filename):
        self.conn = sqlite.connect(filename, isolation_level=None)
        self.conn.execute('pragma journal_mode=wal')
        self.conn.execute('pragma query_only = ON;')

    def get_estimated_offset_for_frame(self,frame_index):       
        sql = "select est_x_offset,est_y_offset from frames where number = %d" % frame_index
        cursor = self.conn.execute(sql)     
        return cursor.fetchone()

    def get_cracks(self,frame_index):
        patches = []
        sql = """select x0,y0,x1,y1,no_crack_prob,crack_prob from patches
                 join frames on patches.fk_frame = frames.pk
                 where frames.number = %d and crack_prob>0.5""" % frame_index
        cursor = self.conn.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            patches.append(row)
        return patches

    def get_cracks_nb(self,x0,y0,threeshold):
        patches = []
        sql = """select x_abs,y_abs,sum_crack_prob,sum_no_crack_prob from clusters 
                 where (x_abs >= %d) and (x_abs<(%d+400))
                 and (y_abs >= %d) and (y_abs<(%d+200))""" % (x0,x0,y0,y0)
        cursor = self.conn.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            xc = row[0]-x0
            yc = row[1]-y0
            log_crack_prob = row[2]
            log_no_crack_prob = row[3]
            if log_no_crack_prob > 0:
                theta = log_crack_prob/log_no_crack_prob
                if ( theta >= threeshold):
                    patches.append( (xc,yc,log_crack_prob,log_no_crack_prob,theta) )
            else:
                patches.append( (xc,yc,log_crack_prob,log_no_crack_prob,10000000000) )
        return patches                 

    def get_frame_with_next_crack(self,start_frame):
        sql = """select frames.number from patches
                 join frames on patches.fk_frame = frames.pk
                 where frames.number> %d and crack_prob > 0.5 LIMIT 1""" % start_frame
        cursor = self.conn.execute(sql)     
        return cursor.fetchone()

    def close(self):
        self.conn.close()        