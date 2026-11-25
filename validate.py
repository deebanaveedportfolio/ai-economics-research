import numpy as np,pandas as pd,xml.etree.ElementTree as E,zipfile,re
from pathlib import Path
p=Path(__file__).parent; d=p/'inputs'
r=E.parse(d/'cps_00002.xml'); vs={v.attrib['name']:v for v in r.findall('.//{*}var')}
for k in ['EMPSTAT','EARNWEEK','WTFINL','OCC']:
 v=vs[k]; print(k,[(x.tag.split('}')[-1],(x.text or '')[:350]) for x in v if x.tag.split('}')[-1] in ['labl','txt','varFormat']]); print([(c.find('{*}catValu').text,c.find('{*}labl').text) for c in v.findall('{*}catgry')][:25])
f=d/'cps_00002.dat'; print('bytes',f.stat().st_size,'remainder',f.stat().st_size%117)
a=np.memmap(f,dtype='S117',mode='r'); totals=[]; panels=[]
for start in range(0,len(a),500000):
 b=a[start:start+500000].view('S1').reshape(-1,117); assert (b[:,116]==b'\n').all()
 def col(k):
  l=vs[k].find('{*}location').attrib; s=int(l['StartPos'])-1; e=int(l['EndPos']); q=b[:,s:e].copy().view('S'+str(e-s)).ravel(); return np.where(np.char.strip(q)==b'',b'-1',q).astype('int64')
 x=pd.DataFrame({k:col(k) for k in ['YEAR','MONTH','AGE','EMPSTAT','OCC','OCC2010','WTFINL','EARNWT','EARNWEEK']}); x['earn_positive_weight']=x.EARNWT>0; x['earn_nonmissing']=x.EARNWEEK.between(0,99999996); totals.append(x.groupby(['YEAR','MONTH']).agg(records=('AGE','size'),earn_positive_weight=('earn_positive_weight','sum'),earn_nonmissing=('earn_nonmissing','sum'))); x['group']=np.select([x.AGE.between(22,25),x.AGE.between(30,49)],['22-25','30-49'],'other'); y=x[x.group.ne('other') & x.EMPSTAT.isin([10,12]) & x.OCC.between(1,9998)]; panels.append(y.groupby(['YEAR','MONTH','OCC','group']).agg(records=('AGE','size'),weight_raw=('WTFINL','sum')))
t=pd.concat(totals).groupby(level=[0,1]).sum(); t.to_csv(p/'cps_monthly_validation.csv'); print('months',len(t),'records',t.records.sum()); print(t.groupby(level=0).sum()); panel=pd.concat(panels).groupby(level=[0,1,2,3]).sum(); panel.to_csv(p/'cps_occupation_age_month.csv'); print('panel',len(panel),panel.records.sum())
