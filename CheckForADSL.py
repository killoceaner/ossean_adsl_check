__author__ = 'houxiang'

from xml.dom import minidom
import  time
import MySQLdb
import  logging
import commands

#for log
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#init mysql connection
#for run
"""
sourceDB={'host':"192.168.80.104","user":"influx","passwd":"influx1234","port":3306,"extractDB":"extract_result","crawlerDB":"pages"}
targetDB={'host':"192.168.80.130","user":"trustie","passwd":"1234","port":3306,"database":"ossean_production"}
"""
#for test

sourceDB={"host":'localhost',"user":'root',"passwd":'root',"port":3306,"extractDB":'test',"crawlerDB":"pages"}
targetDB={"host":'localhost',"user":'root',"passwd":'root',"port":3306,"database":'test_db'}

conn = MySQLdb.connect(host=sourceDB["host"],user=sourceDB["user"],passwd=sourceDB["passwd"],port=sourceDB["port"])


def sql_handler(sql):
    cur = conn.cursor()
    conn.select_db(sourceDB["crawlerDB"])
    count = cur.execute(sql)
    if count == 1:
        result = cur.fetchone()
        conn.commit()
    #print count
    #print result
    return result

def close():
    conn.close()

def xml_to_string(filename='config.xml'):
    doc = minidom.parse(filename)
    return doc.toxml('UTF-8')

def get_attrvalue(node,attrname):
    return node.getAttribute(attrname)if node else''

def get_xmlnode(node,name):
    return node.getElementsByTagName(name) if node else[]

def get_nodevalue(node,index=0):
    return node.childNodes[index].nodeValue if node else''

def get_xml_data(filename='config.xml'):
    doc = minidom.parse(filename)
    root = doc.documentElement

    site_nodes = get_xmlnode(root ,"site")

    #print site_nodes

    site_list={}
    for node in site_nodes:
        node_name = get_xmlnode(node, 'tablename')
        node_value = get_xmlnode(node,"value")
        node_sql = get_xmlnode(node , "sql")
        #print node_name , node_value , node_sql

        site_name = get_nodevalue(node_name[0]).encode('utf-8','ignore')
        site_value = get_nodevalue(node_value[0]).encode('utf-8','ignore')
        site_sql = get_nodevalue(node_sql[0]).encode('utf-8','ignore')

        entry = [site_value , site_sql]
        site_list[site_name] = entry

    #print site_list
    return site_list

def adsl_reboot():
    (status, output) = commands.getstatusoutput('pppoe-stop')
    (status, output) = commands.getstatusoutput('pppoe-start')


def check_loop():
    site_list = get_xml_data();
    flag = False
    for name , info in site_list.items():
        sql = info[1]
        value = info[0]
        ans = sql_handler(sql)
        logger.info("the site : "+name+" stop for: "+str(ans[0]))
        if ans > value:
            flag = True


def timer():
    while True:
        check_loop()
        time.sleep()

if __name__ == '__main__':
    #xml_to_string()

    check_loop()
    close()