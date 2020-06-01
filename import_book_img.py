import csv
import os
import requests
from xml.etree import ElementTree
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("postgres://zonlblmamoyibe:6a0a05b3e1d75d8eeb66e87d4413441cecc9c74243ffe878db9aadb05f9dddaa@ec2-54-211-210-149.compute-1.amazonaws.com:5432/dd840rgbb924lt")
db = scoped_session(sessionmaker(bind = engine))

def main():
    all = db.execute("select * from books").fetchall()
    images = {}
    cnt = 0;
    for e in all:
        cnt = cnt +1
        query ="https://www.goodreads.com/book/isbn/ISBN?format=xml"
        query = query.replace("ISBN",e[0])
        res = requests.get(query, params={"key":"otbDB4eqXRlXE2RQeAA"})
        string_xml = res.content
        tree = ElementTree.fromstring(string_xml)
        img = tree.findall('book/image_url')[0].text
        db.execute("insert into images values (:isbn, :url)", {"isbn":e[0] , "url":img})
        print(cnt, e[0], img)

    db.commit()
        # images[e[0]] = img
    # f = open("books.csv")
    # reader = csv.reader(f)
    # for isbn, title, author, year in reader:
    #     db.execute("INSERT INTO books (isbn, title, author, year) values (:isbn, :title, :author, :year)",
    #     {"isbn":isbn, "title":title, "author":author, "year":year})
    #     print(isbn,title,author,year)
    # db.commit()
if __name__ == "__main__":
    main()
