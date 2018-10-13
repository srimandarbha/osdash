#!/usr/bin/env python
from __future__ import division
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from keystoneauth1 import loading
from keystoneauth1 import session
from cinderclient import client as cclient
from novaclient import client as nclient
from datetime import datetime
from sqlalchemy import *
from settings import *
import re

db = create_engine(SQLALCHEMY_DATABASE_URI)
metadata = MetaData(db)

#openstack section
nova_servers_list={}
loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url='https://Ostk-keystone.hq.bn-corp.com:5000/v3', username='cloudadmin', password='zooch9sie2Coth5O', project_id='a02f8855389746aeb9be47ba75a72049', user_domain_name='admin_domain')
sess = session.Session(auth=auth)
nova = nclient.Client(2.53, session=sess)
nova_hyp=nova.hypervisor_stats.statistics()

#quotas
get_quotas_dict={}
project_id_dict={'admin_domain': 'a02f8855389746aeb9be47ba75a72049'}
for project_key,project_val in project_id_dict.iteritems():
    project_dict=nova.quotas.get(project_val).to_dict()
    get_quotas_dict[project_key]=dict(instances=project_dict['instances'], cores=project_dict['cores'], fixed_ips=project_dict['fixed_ips'], floating_ips=project_dict['floating_ips'], ram=project_dict['ram'], security_group_rules=project_dict['security_group_rules'], security_groups=project_dict['security_groups'], server_group_members=project_dict['server_group_members'], server_groups=project_dict['server_groups'])

nova_list=nova.servers.list()
for i in nova_list:
    name=i.name
    serv_stat=nova.servers.diagnostics(i)[1]
    nova_servers_list[name]={}
    nova_servers_list[name]['id']=i.id
    if i.networks:
        for key,value in i.networks.iteritems():
            networks_val = key
            ips_val = ','.join(value)
    nova_servers_list[name]['networks']=networks_val
    nova_servers_list[name]['ips']=ips_val
    nova_servers_list[name]['state']=i.status
    sg_list=[]
    if i.security_groups:
        for sg in i.security_groups:
            sg_list.append(sg['name'])
    nova_servers_list[name]['security_groups']=','.join(sg_list)
    get_cpu=re.compile('cpu')
    cpu_count=len(get_cpu.findall(''.join(serv_stat)))
    memory_total=serv_stat['memory']/1024/1024
    nova_servers_list[name]['memory_used']=0
    if serv_stat.has_key('memory-unused'):
        nova_servers_list[name]['memory_used']=serv_stat['memory-unused']/1024/1024
    text=str(' '.join(serv_stat.keys()))
    try:
        if_rx = re.search('.*(tap.*_rx).*', text).group(1)
        if_tx = re.search('.*(tap.*_tx).*', text).group(1)
        cpu_count = len(re.findall('cpu',text))
    except AttributeError:
        if_rx = 0
        if_tx = 0
    nova_servers_list[name]['cpu_count']=cpu_count
    nova_servers_list[name]['memory_total']=memory_total
    nova_servers_list[name]['memory_free']=memory_total-nova_servers_list[name]['memory_used']
    nova_servers_list[name]['memory_free_percentage']=nova_servers_list[name]['memory_free']/ nova_servers_list[name]['memory_total']*100
    nova_servers_list[name]['if_rx']=serv_stat[if_rx]
    nova_servers_list[name]['if_tx']=serv_stat[if_tx]

vm_stats = Table('vm_stats', metadata,
    Column('id', Integer, primary_key=True),
    Column('time', Time),
    Column('date', Date),
    Column('vm_data', JSON),
)

if not db.dialect.has_table(db, 'vm_stats'):
    vm_stats.create()

i = vm_stats.insert()
i.execute(time=datetime.now().strftime('%H:%M:%S'),date=datetime.now().strftime('%Y-%m-%d'),vm_data=nova_servers_list)
    
cinder = cclient.Client(3.1, session=sess)
cinder_list_tot=cinder.volumes.list()
cinder_list_avail=cinder.volumes.list(search_opts={'status':'available'})

cinder_stats = Table('cinder_stats', metadata,
    Column('id', Integer, primary_key=True),
    Column('time', Time),
    Column('date', Date),
    Column('cinder_data', JSON),
    Column('total_vols', Integer),
    Column('avail_vols', Integer),
)

if not db.dialect.has_table(db, 'cinder_stats'):
    cinder_stats.create()

cinder_vols_dict={}
cinder_vols_dict['inuse']={}
cinder_vols_dict['available']={}
for vol in cinder_list_tot:
    cur_vol=vol.to_dict()
    if cur_vol['status'] == 'available':
        cinder_vols_dict['available'][cur_vol['id']]={'size': cur_vol['size'], 'image_name': cur_vol['volume_image_metadata']['image_name']}
    elif cur_vol['status'] == 'in-use':
        cinder_vols_dict['inuse'][cur_vol['id']]={'size': cur_vol['size'], 'image_name': cur_vol['volume_image_metadata']['image_name']}
    else:
       pass
i = cinder_stats.insert()
i.execute(time=datetime.now().strftime('%H:%M:%S'),date=datetime.now().strftime('%Y-%m-%d'),cinder_data=cinder_vols_dict,total_vols=int(len(cinder_vols_dict['available'])+len(cinder_vols_dict['inuse'])),avail_vols=len(cinder_vols_dict['available']))

hypstats = Table('hypstats', metadata,
    Column('id', Integer, primary_key=True),
    Column('time', Time),
    Column('date', Date),
    Column('hyp_count', Integer),
    Column('running_vms',Integer),
    Column('vcpus', Integer),
    Column('vcpus_used', Integer),
    Column('vcpus_free', Integer),
    Column('memory', Integer),
    Column('memory_used',Integer),
    Column('memory_free',Integer),
    Column('total_disk', Integer),
    Column('disk_used',Integer),
    Column('disk_free',Integer),
    Column('quotas',JSON),
)

if not db.dialect.has_table(db, 'hypstats'):
    hypstats.create()

hyp_serv_stats = Table('hyp_serv_stats', metadata,
    Column('id', Integer, primary_key=True),
    Column('time', Time),
    Column('date', Date),
    Column('hypervisor_data', JSON),
)

if not db.dialect.has_table(db, 'hyp_serv_stats'):
    hyp_serv_stats.create()

i = hypstats.insert()
nova_hyp_dict=nova_hyp.to_dict()
i.execute(time=datetime.now().strftime('%H:%M:%S'),date=datetime.now().strftime('%Y-%m-%d'),hyp_count=nova_hyp_dict['count'], running_vms=nova_hyp_dict['running_vms'],vcpus=nova_hyp_dict['vcpus'],vcpus_used=nova_hyp_dict['vcpus_used'],vcpus_free=int(nova_hyp_dict['vcpus'] - nova_hyp_dict['vcpus_used']),memory=nova_hyp_dict['memory_mb']/1024,memory_used=nova_hyp_dict['memory_mb_used']/1024,memory_free=int(nova_hyp_dict['memory_mb'] - nova_hyp_dict['memory_mb_used'])/1024,total_disk=nova_hyp_dict['local_gb'],disk_used=nova_hyp_dict['local_gb_used'],disk_free=int(nova_hyp_dict['local_gb'] - nova_hyp_dict['local_gb_used']),quotas=get_quotas_dict)

os_hypvsr_dict={}
nova_hyp_list=nova.hypervisors.findall()
for hypervisor in nova_hyp_list:
     hypvsr=hypervisor.to_dict() 
     os_hypvsr_dict[hypvsr['hypervisor_hostname']]=dict(state=hypvsr['state'],status=hypvsr['status'], running_vms=hypvsr['running_vms'],vcpus=hypvsr['vcpus'],vcpus_used=hypvsr['vcpus_used'],vcpus_free=int(hypvsr['vcpus'] - hypvsr['vcpus_used']),memory=hypvsr['memory_mb']/1024,memory_used=hypvsr['memory_mb_used']/1024,memory_free=int(hypvsr['memory_mb'] - hypvsr['memory_mb_used'])/1024,total_disk=hypvsr['local_gb'],disk_used=hypvsr['local_gb_used'],disk_free=int(hypvsr['local_gb'] - hypvsr['local_gb_used']))
i = hyp_serv_stats.insert()
i.execute(time=datetime.now().strftime('%H:%M:%S'),date=datetime.now().strftime('%Y-%m-%d'),hypervisor_data=os_hypvsr_dict)
