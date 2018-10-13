from bs4 import BeautifulSoup 
from app import app
from flask import render_template
from collections import OrderedDict
from app.db import Hypstats, Hyp_serv_stats,Cinder_stats, Vm_stats
import requests
import settings

@app.route('/', methods=['GET'])
def index():
    hypstats_result=Hypstats.query.get_or_404(Hypstats.query.count())
    hyp_serv_stats_result=Hyp_serv_stats.query.get_or_404(Hyp_serv_stats.query.count())
    cinder_stats_result=Cinder_stats.query.get_or_404(Cinder_stats.query.count())
    vm_stats_result=Vm_stats.query.get_or_404(Vm_stats.query.count())
    return render_template("index.html", hypstats_result=hypstats_result, hyp_serv_stats_result=hyp_serv_stats_result, cinder_stats_result=cinder_stats_result,vm_stats_result=vm_stats_result,nagios_alert=nagios_check(),memory_stats=get_memory_util(vm_stats_result))

def nagios_check():
    alerts_dict={}
    page = requests.get("http://nagiosro:eim7ca1He4he@10.243.8.62/nagios3/cgi-bin/status.cgi?host=all&servicestatustypes=16&hoststatustypes=15")
    soup = BeautifulSoup(page.content, 'html.parser')
    ok_stats=soup.find('td',attrs={'class':'serviceTotalsOK'})
    unknown_stats=soup.find('td',attrs={'class':'serviceTotalsUNKNOWN'})
    warn_stats=soup.find('td',attrs={'class':'serviceTotalsWARNING'})
    crit_stats=soup.find('td',attrs={'class':'serviceTotalsCRITICAL'})
    if unknown_stats != None:
        alerts_dict['unknown']={}
        alerts_dict['unknown']['count']=unknown_stats.text
        alerts_dict['unknown']['url']='status.cgi?host=all&servicestatustypes=8&hoststatustypes=15'
        alerts_dict['unknown']['label']='pficon-warning-triangle-o'
    elif warn_stats != None:
        alerts_dict['warning']={}
        alerts_dict['warning']['count']=warn_stats.text
        alerts_dict['warning']['url']='status.cgi?host=all&servicestatustypes=4&hoststatustypes=15'
        alerts_dict['warning']['label']='pficon-warning-triangle-o'
    elif crit_stats != None:
        alerts_dict['critical']={}
        alerts_dict['critical']['count']=crit_stats.text
        alerts_dict['critical']['url']='status.cgi?host=all&servicestatustypes=16&hoststatustypes=15'
        alerts_dict['critical']['label']='pficon-error-circle-o'
    else:
        alerts_dict['ok']={}
        alerts_dict['ok']=ok_stats.text
        alerts_dict['ok']['label']='"pficon pficon-ok'
    return alerts_dict 

def sort_mem(mem_dict):
    per_list=[]
    for m in mem_dict.values():
        per_list.append(m['memory_free_percentage'])
    per_list.sort(reverse=True)
    fin_per_list=OrderedDict()
    for i in per_list:
        for m,n in mem_dict.iteritems():
            if i == n['memory_free_percentage']:
                fin_per_list[m]=i
    return fin_per_list

def get_memory_util(m):
    if m.vm_data:
        memory_stats=sort_mem(m.vm_data)
    return memory_stats
