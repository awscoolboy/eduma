import sqlite3

class Lesson():
    def __init__(self, title, code, duration):
        self.title = title
        self.code = code
        self.duration = duration



class Course:
    def __init__(self,plid):
        self.plid = plid
        self.titile = ''
        self.count = -1
        self.last_index = -1


class Databse():
    
    def __init__(self, dbname="eduma.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)
        self.createTable()

    def createTable(self):
        courseTable = "CREATE TABLE IF NOT EXISTS course(_id INTEGER PRIMARY KEY AUTOINCREMENT,plid TEXT,title TEXT,count iINTEGER,last_index INTEGER)"
        courseidx = "CREATE INDEX IF NOT EXISTS course_index ON course (plid ASC)" 
        self.conn.execute(courseTable)
        self.conn.execute(courseTable)
        self.conn.commit

    def addCourse(self, course):
        stmt = "INSERT INTO course (plid,title,count,last_index) VALUES (?,?,?,?)"
        args = (str(course.plid),str(course.title),str(course.count),str(course.last_index),)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def getCourse(self, plid):
        stmt = "SELECT * FROM course WHERE plid = (?) LIMIT 1"
        args = (plid,)
        return self.conn.execute(stmt) 

    


# import sqlalchemy
# from sqlalchemy import Table, Column, Integer, ForeignKey, String,Boolean
# from sqlalchemy.orm import relationship
# from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy import create_engine



# Base = declarative_base()



# class Course(Base):
#     __tablename__ = 'course'
#     id = Column(Integer, primary_key=True)
#     lessons = relationship("Lessons", back_populates="course")
#     playlistid = Column(String)
#     title = Column(String)
#     lesson_count = Column(String)
#     last_added_lesson = Integer
#     completed = Column(Boolean)

#     def __repr__(self):
#         return "<Course(title='%s', playlist='%s', lessoncount='%s', complted='%s')>" % (
#                                 self.title, self.playlistid, self.lesson_count,self.completed)


# class Lessons(Base):
#     __tablename__ = 'lessons'
#     id = Column(Integer, primary_key=True)
#     parent_id = Column(Integer, ForeignKey('course.id'))
#     parent = relationship("course", back_populates="lessons")
#     posation = Column(Integer)
#     title = Column(String)
#     embed = Column(String)
#     time = Column(String)

#     def __repr__(self):
#         return "<Lesson(title='%s', posation='%s', emebd='%s')>" % (
#                                 self.title, self.posation, self.embed)






   