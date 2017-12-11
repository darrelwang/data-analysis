
# coding: utf-8

# In[1]:

#!/usr/bin/env python



# In[18]:

import lxml.etree as ET
from collections import defaultdict
import matplotlib.pyplot as plt
get_ipython().magic('matplotlib inline')
import pprint
import re
import codecs
import json


# In[16]:

filename="map.osm"


# In[20]:

import re
from collections import defaultdict

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", 'Alley', 'Blvd', 'Bowery', 'Americas', 'Bushwick', 'East',
            'South','West', 'North', 'Park', 'Plaza','Broadway', 'Center', 'Floor', 'Highline', 'Level',
            'Loop', 'Unidos', 'Village', 'Way', 'Yards', 'Track', 'Terrace', 'A', 'B', 'C', 'USA', 'NY', 'Mews', 'Macdougal', 'Oval', '1',
           '10003', '1801', '1807', '27th', '29th', 'S', '42nd']

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)

    for event, el in ET.iterparse(filename, tag=['node', 'way']):
        if el.tag ==  'node': 
            for tag in el.iter('tag'):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()                
    return street_types


# In[21]:

def test():
    street_types = audit(filename)
    pprint.pprint(dict(street_types))


# In[22]:

if __name__ == '__main__':
    test()


# In[38]:

mapping = {"1B":"#1B",
           "205":"#205",
           "2E":"#2E",
           "2N":"#2N",
           "3":"#3",
           "301":"#301",
           "306":"#306",
           "400":"#400",
           "403":"#407",
           "605":"#605",
           "800a":"#800a",
           "900":"#900",
           'Ave':'Avenue',
           'Avene':'Avenue',
           "Broadway.":"Broadway",
           "M1":"#M1",
           "M204":"#M204",
           "St":"Street",
           "St.":"Street",
           "Steet":"Street",
           "ave":"Avenue",
           "avenue":"Avenue",
           "st":"Street",
           "street":"Street"}


# In[36]:

#对错误值使用mapping进行替换
def update_value(value, mapping):
    if value in mapping:
        value=mapping[value]
    else:
        last=value.split()[-1]
        if  last in mapping:
            value=value.replace(last,mapping[last])
    return value


# In[6]:

import csv
import cerberus
import schema_test


# In[7]:

NODES_PATH = r"C:\Users\wz\nodes.csv"
NODE_TAGS_PATH = r"C:\Users\wz\nodes_tags.csv"
WAYS_PATH = r"C:\Users\wz\ways.csv"
WAY_NODES_PATH = r"C:\Users\wz\ways_nodes.csv"
WAY_TAGS_PATH = r"C:\Users\wz\ways_tags.csv"


# In[8]:

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


# In[9]:

PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
SCHEMA = schema_test.schema


# In[30]:

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []
    # 获取node_attribs中的tag值
    if element.tag == 'node':
        for field in node_attr_fields:
            if field=='id' or field=='uid' or field=='changeset':
                node_attribs[field]=int(element.attrib[field])
            elif field=='lat' or field=='lon':
                node_attribs[field]=float(element.attrib[field])
            else:
                node_attribs[field]=element.attrib[field]
        #获取node嵌套文档的值        
        for elem in element.findall('tag'):
            tags_record={}
            if elem is not None:
                if problem_chars.search(elem.attrib['k']):
                    pass
                else:
                    tags_record['id']=node_attribs['id']
                    if is_street_name(elem):
                        tags_record['value']=update_value(elem.attrib['v'],mapping)
                    else:
                        tags_record['value']=elem.attrib['v']
                    if ':' in elem.attrib['k']:
                        n=elem.attrib['k'].find(':')
                        tags_record['key']=elem.attrib['k'][n+1:]
                        tags_record['type']=elem.attrib['k'][0:n]
                    else:
                        tags_record['key']=elem.attrib['k']
                        tags_record['type']=default_tag_type
                    tags.append(tags_record)
        return {'node': node_attribs, 'node_tags': tags}
    
    elif element.tag == 'way':
        #获取way_attribs中的tag值
        for field in way_attr_fields:
            if field=='id' or field=='uid' or field=='changeset':
                way_attribs[field]=int(element.attrib[field])
            else:
                way_attribs[field]=element.attrib[field]
        #获取way嵌套文档的值        
        for elem in element.findall('tag'):
            tags_record={}
            if elem is not None:
                if problem_chars.search(elem.attrib['k']):
                    pass
                else:
                    tags_record['id']=way_attribs['id']
                    if is_street_name(elem):
                        tags_record['value']=update_value(elem.attrib['v'],mapping)
                    else:
                        tags_record['value']=elem.attrib['v']
                    if ':' in elem.attrib['k']:
                        n=elem.attrib['k'].find(':')
                        tags_record['key']=elem.attrib['k'][n+1:]
                        tags_record['type']=elem.attrib['k'][0:n]
                    else:
                        tags_record['key']=elem.attrib['k']
                        tags_record['type']=default_tag_type
                    tags.append(tags_record)
        #获取way嵌套文档的node值
        count=0
        for elem in element.findall('nd'):
            node_record={}
            node_record['id']=way_attribs['id']
            node_record['node_id']=elem.attrib['ref']
            node_record['position']=count
            way_nodes.append(node_record)
            count +=1
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# In[31]:

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


# In[32]:

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))


# In[33]:

class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# In[34]:

def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file,          codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file,          codecs.open(WAYS_PATH, 'w') as ways_file,          codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file,          codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


# In[39]:

if __name__ == '__main__':
    process_map(filename, validate=True)

