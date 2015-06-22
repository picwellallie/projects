from flask import Flask, render_template, redirect, url_for, flash, make_response, session
import boto
import boto3
import datetime
import operator
from tabulate import tabulate


app = Flask(__name__)
vpca = boto.connect_vpc()
ec2 = boto.connect_ec2()
cw = boto3.client('cloudwatch', 'us-east-1')


zonea = "us-east-1a"
zoneb = "us-east-1b"
zoned = "us-east-1d"
zonee = "us-east-1e"


# PRINT #######################################################################
#! List all the VPCs
def list_vpcs():
    vpclist = vpca.get_all_vpcs()
    print vpclist, len(vpclist)


#! List the availability zones with the current region
def list_zones():
    zones = ec2.get_all_zones()
    print zones   


#! List the subnets
def list_subnets():
    snets = vpca.get_all_subnets()
    print snets, len(snets)


#! List the security groups the EC2 is a part of
def list_security_groups(ec2):
    sg = ec2.groups
    for g in sg:
         print g.name

################################################################################
def find_used_zones():
    zlist = [find_subnets(zonea), find_subnets(zoneb), find_subnets(zonec),
    find_subnets(zoned)]
    for z in zlist:
        if len(z) == 0: zlist.remove(z)
    return zlist


def find_subnets_in_zones():
    return [find_subnets(zonea), find_subnets(zoneb), find_subnets(zoned),
    find_subnets(zonee)]

#! returns lists containing availability zones w/subnets, instances
def get_all_data():
    return find_subnets_in_zones() 

################################################################################

#! Return the subnets in the vpc and zone
def subnets_in_zone_vpc(zone, vpc):
    return vpca.get_all_subnets(filters = {"availabilityZone" : zone, "vpc-id" : vpc})

#! Return the subnets in the zone
def subnets_in_zone(zone):
    return vpca.get_all_subnets(filters = {"availabilityZone" : zone})


# ! Return the instances in a subnet
def instances_in_subnet(snet):
    return ec2.get_only_instances(filters = {"subnet-id" : snet})

# def instances_in_subnet(snetname):
#     return ec2.get_only_instances(filters = {"tag:key=value" : })

#print ec2.get_only_instances()[0].tags

def sg_name(sg):
    return str(sg.name)

def instance_name(inst):
    return [str(inst.tags['Name'])]
    

def instance_name_sg(inst):
    try:
        return [str(inst.tags['Name']), map(sg_name, inst.groups)]
    except:    
        return ['No Name', map(sg_name, inst.groups)]

#! Return the all the data about one vpc in format (this is without security 
#  groups) : 
def vpc_data(vpc):
    overall = []
    for i,z in enumerate(ec2.get_all_zones()):
        overall.append([str(z.name)])
        snets = subnets_in_zone_vpc(z.name,vpc)
        #print z.name + ": ", len(snets), snets
        for j,s in enumerate(snets, start =1):   
            #print str(s.tags['Name'])    
            overall[i].append([str(s.tags['Name'])])
            instnamelist = map(instance_name, instances_in_subnet(s.id))
            overall[i][j].append(instnamelist)
    return list(filter((lambda x: len(x) > 1),overall))

def fix_subnet_order(data):
    az2newlyordered = [data[1][0]]
    for x in range(1, len(data[0])):
        matchthis = data[0][x][0].replace("az1", "az2")
        for y in range(1, len(data[1])):
            if data[1][y][0] == matchthis:
                az2newlyordered.append(data[1][y])
    data[1] = az2newlyordered
    return data

def vpc_data_sg_order(vpc):
    overall = []
    f = []
    for i,z in enumerate(ec2.get_all_zones()):
        overall.append([str(z.name)])
        snets = subnets_in_zone_vpc(z.name,vpc)
        #print z.name + ": ", len(snets), snets
        for j,s in enumerate(snets, start = 1):     
            overall[i].append([str(s.tags['Name'])])
            instnamelist = map(instance_name_sg, instances_in_subnet(s.id))
            overall[i][j].append(instnamelist)
    overall = list(filter((lambda x: len(x) > 1), overall))
    return fix_subnet_order(overall)

#! Same as vpc_data but also has security group relations
def vpc_data_sg(vpc):
    overall = []
    f = []
    for i,z in enumerate(ec2.get_all_zones()):
        overall.append([str(z.name)])
        snets = subnets_in_zone_vpc(z.name,vpc)
        #print z.name + ": ", len(snets), snets
        for j,s in enumerate(snets, start =1):     
            overall[i].append([str(s.tags['Name'])])
            instnamelist = map(instance_name_sg, instances_in_subnet(s.id))
            overall[i][j].append(instnamelist)
    return list(filter((lambda x: len(x) > 1),overall))
    # print overall
    # return fix_subnet_order(overall)

# def vpc_data_sg(vpc):
#     overall = []
#     f = []
#     for i,z in enumerate(ec2.get_all_zones()):
#         snets = subnets_in_zone_vpc(z.name,vpc)
#         if len(snets) > 0:
#             overall.append([str(z.name)])
#         #print z.name + ": ", len(snets), snets
#         for j,s in enumerate(snets, start =1):     
#             overall[0].append([str(s.tags['Name'])])
#             overall[0].append([str(s.tags['Name'])])
#             instnamelist = map(instance_name_sg, instances_in_subnet(s.id))
#             overall[0][j].append(instnamelist)
#     return list(filter((lambda x: len(x) > 1),overall))

vpc_data_sg("vpc-8ada78ef")


# print subnets_in_zone_vpc(zoneb, "vpc-1d39cf78")
# print subnets_in_zone(zoneb)

################################################################################
#TESTING



def find_subnets(vpc):
    return vpca.get_all_subnets(filters = {"vpc-id" : vpc})




#print find_subnets("vpc-1d39cf78")
#print zones_in_vpc("available")
#print instances_in_subnet("subnet-65e7233c")[0].tags



#TAGS
def instances():
    return ec2.get_only_instances(filters = {"instance-id" : "i-93f55c72"})


#print instances()[0].tags
# {u'Availability Zone': u'us-east-1d', u'elasticbeanstalk:environment-id': u'e-dkiwqfqktn', 
# u'elasticbeanstalk:environment-name': u'predictions-staging', u'aws:cloudformation:logical-id': 
# u'AWSEBAutoScalingGroup', u'aws:cloudformation:stack-id': 
# u'arn:aws:cloudformation:us-east-1:999892920914:stack/awseb-e-dkiwqfqktn-stack/6c173f00-69d9-11e4-8bf6-50e24162947c', 
# u'Environment': u'staging-vpc', u'aws:cloudformation:stack-name': u'awseb-e-dkiwqfqktn-stack',
# u'Purpose': u'sliders', u'aws:autoscaling:groupName': u'awseb-e-dkiwqfqktn-stack-AWSEBAutoScalingGroup-E3D0MLXAU1EM', 
# u'Name': u'predictions-staging'}

mlst = ["hi", ["a","b","c"]]
slst = ["asdf", "fghi"]
lst = [1,2,3]

@app.route('/')
def default():
    return render_template('test.html')

@app.route('/databricks')
def databricks():
    return render_template('mvp.html', data = vpc_data_sg_order("vpc-6d5fd208"))

@app.route('/staging')
def staging():
    return render_template('mvp.html', data = vpc_data_sg_order("vpc-1d39cf78"))

@app.route('/uat')
def uat():
    return render_template('mvp.html', data = vpc_data_sg_order("vpc-ba0cc7df"))

@app.route('/production')
def production():
    return render_template('mvp.html', data = vpc_data_sg_order("vpc-8ada78ef"))


# [VPC:vpc-6d5fd208; databricks, VPC:vpc-1d39cf78; staging, VPC:vpc-ba0cc7df; uat, VPC:vpc-8ada78ef; production] 


    
if __name__ == '__main__':
    app.run(debug = True)