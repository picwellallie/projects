import boto
ec2 = boto.connect_ec2()
key_pair = ec2.create_key_pair('ec2-sample-key')  # only needs to be done once
key_pair.save('/Users/patrick/.ssh')
reservation = ec2.run_instances(image_id='ami-bb709dd2', key_name='ec2-sample-key')

# Wait a minute or two while it boots
for r in ec2.get_all_instances():
    if r.id == reservation.id:
        break
print r.instances[0].public_dns_name  # output: ec2-184-73-24-97.compute-1.amazonaws.com



def vpc_data_sg(vpc):
    f = 0
    snets = []
    # global f
    overall = []
    for i,z in enumerate(ec2.get_all_zones()):
        s = subnets_in_zone_vpc(z.name,vpc)
        if len(s) > 0:
            overall.append([str(z.name)])
            if f == 0:
                f = s
                print f
                snets = f
            else:
                snets = map(changezone,f)
        #print z.name + ": ", len(snets), snets
            for j,s in enumerate(snets, start =1):     
                overall[i].append([str(s.tags['Name'])])
                instnamelist = map(instance_name_sg, instances_in_subnet(s.id))
                overall[i][j].append(instnamelist)
                
    return overall