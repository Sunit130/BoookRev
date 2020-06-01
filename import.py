import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://gthzhakymtgjpp:767df28fa13331d5b7eaecc2e1a0b9190b2343e6cece43a492b455022587e7d7@ec2-34-198-243-120.compute-1.amazonaws.com:5432/ddjdjstcm6pd0q")
db = scoped_session(sessionmaker(bind = engine))

def main():
    # all = db.execute("select * from books").fetchall()
    # print(all)
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) values (:isbn, :title, :author, :year)",
        {"isbn":isbn, "title":title, "author":author, "year":year})
        print(isbn,title,author,year)
    db.commit()
if __name__ == "__main__":
    main()
