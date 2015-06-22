import boto
import boto3
import datetime
import operator
from tabulate import tabulate

ec2 = boto.connect_ec2()
cw = boto3.client('cloudwatch', 'us-east-1')

def ec2_search(environment, action):
        reservations = ec2.get_all_instances()
        listed_data = []
        listed_data = [i for r in reservations for i in r.instances
            if i.tags and 'Environment' in i.tags
                and environment in i.tags['Environment']
                and 'Name' in i.tags and 'comm' in i.tags['Name']]
        if action == 'get_data':
            cpudict = {}
            new_list = []
            for i in listed_data:
                if i.state == 'running' or i.state == 'terminated':
                    cpu = cw.get_metric_statistics(
                            Period = 60,
                            StartTime = datetime.datetime.utcnow() - datetime.timedelta(seconds=600),
                            EndTime = datetime.datetime.utcnow(),
                            MetricName = 'CPUUtilization',
                            Namespace = 'AWS/EC2',
                            Statistics = ['Average'],
                            Dimensions= [{'Name': 'InstanceId', 'Value': i.id}]
                            )
                    if round(cpu['Datapoints'][0]['Average'],1) < 10.0:
                        i.cpu = round(cpu['Datapoints'][0]['Average'],2)
                        i.name = i.tags['Name']
                        new_list.append(i)
                    else:
                        i.cpu = round(cpu['Datapoints'][0]['Average'],1)
                        i.name = i.tags['Name']
                        new_list.append(i)
                else:
                    # Fake the data if the instances is stopped or terminated
                    i.cpu= 0.0
                    i.name = i.tags['Name']
                    new_list.append(i)
                                #   {u'Datapoints': [{u'Timestamp':
                                #     'date',
                                #    u'Average': 0.0, u'Unit': 'Percent'}],
                                #    u'Label': 'CPUUtilization'}
            #try:
            new_list.sort(key=operator.attrgetter('cpu'))
            #except:
            #    new_list.sort(key=operator.attrgetter('cpu'))
            return len(new_list), new_list
        else:
            return len(listed_data)


mylength, mylist = ec2_search('staging','get_data')

table = []

for i in mylist:
	table.append([i.name,i.cpu, i.tags['Environment']])

print tabulate(table, headers = ['Name', 'CPU', 'Environment'])



