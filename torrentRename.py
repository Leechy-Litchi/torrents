import torrent_parser as tp
import os
import shutil
import re
import time
import sqlite3

class Classifier:
    def __init__(self,path) -> None:
        self.path = path

    def compare(self,pattern):
        global name
        if re.search(pattern,name):
            return True
        return False

    def classify(self):
        with open("patterns/"+self.path,"r") as patterns:
            for pattern in patterns.readlines():
                if self.compare(pattern):
                    return self.path.split(".")[0]
        return ""

def formatSize(length):
    size=["B","KB","MB","GB","TB","PB"]
    num = int(length)
    for i in range(len(size)):
        if num/1024>1:
            num/=1024
            continue
        else:
            num = str(num)[:6]+size[i]
            return num

def getMetadata(torrent):
    global name
    try:
        metadata = tp.parse_torrent_file(torrent)
        name = metadata['info']['name']
        length = 0
        for i in metadata['info']:
                if "length"==i:
                    length+=metadata['info'][i]
                elif "files"==i:
                    for j in metadata['info']['files']:
                        length+=j['length']
        if len(name)==0:
            return None
        if type(name)==bytes:
            return None
        magnet= 'magnet:?'\
            + 'xt=urn:btih:' + torrent.split("/")[-1].split(".")[0]\
            + '&dn=' + name \
            + '&xl=' + str(length)
            # + '&tr=' + metadata['announce']\ 
    except tp.InvalidTorrentDataException:
        return None
    return magnet

def main():
    os.chdir(ROOT)
    if os.path.exists("patterns")==False:
        os.mkdir("patterns")
    conn = sqlite3.connect("filelists.sqlite")
    conn.execute("create table if not exists magnets (name text unique,type text,magnet text unique,length text)")

    global magnet
    classifiers = []
    for i in os.listdir("patterns"):
        classifiers.append(Classifier(i))

    insertlist = []
    # otherlist = []
    while 1:
        for i,j,k in os.walk("temp"):
            if len(j)>0:
                continue
            for l in k:
                torrent = i+"/"+l
                magnet = getMetadata(torrent)
                if magnet:
                    filetype = ""
                    for classifier in classifiers:
                        type_ = classifier.classify()
                        if type_!="":
                            filetype += type_+" "
                    if len(filetype)>0:
                        filetype = filetype[:-1]
                        length = magnet.split("&xl=")[1]
                        length = formatSize(length)
                        insertlist.append((name,filetype,magnet,length))
                    # else:
                    #     otherlist.append((name,"Other",magnet))
                        # res = conn.execute("select * from magnets")
                        # print(res.fetchall())
                        # conn.close()                        
        # for root,dirs,files in os.walk("temp"):
        #     for dir in dirs:
        #         try:
        #             shutil.rmtree("temp/"+dir)
        #         except:
        #             pass
        #     break
        conn.executemany("insert or ignore into magnets values (?, ?, ?, ?)",insertlist)
        # conn.executemany("insert or ignore into magnets values (?, ?, ?,?)",otherlist)
        conn.commit()
        time.sleep(10*60)
    # if len(os.listdir("."))>18:
    #     os.system("bash ./autoupdate.sh")




ROOT = os.path.expanduser('~')+"/torrents"
if __name__=='__main__':
    main()       
