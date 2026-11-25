from pathlib import Path
import pandas as pd,numpy as np,re,zipfile,statsmodels.formula.api as smf
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent; D=O/'inputs'
x=pd.read_excel(D/'2018-occupation-code-list-and-crosswalk(1).xlsx',sheet_name=1,header=None)
e=pd.read_csv(D/'job_exposure.csv'); z=zipfile.ZipFile(D/'db_31_0_mysql.zip'); a=[]
for l in z.read(next(n for n in z.namelist() if '/28_work_activities' in n)).decode().splitlines():
 m=re.search(r"VALUES \('([^']+)', '(4.A.2.b.3|4.A.4.b.3)', 'IM', ([\d.]+),",l)
 if m:a.append((m[1][:7],m[2],float(m[3])))
w=pd.DataFrame(a,columns=['occ_code','element','score']).groupby(['occ_code','element']).score.mean().unstack().reset_index(); w.columns=['occ_code','knowledge','teaching']; e=e.merge(w)
# Strict exact detailed SOC mappings only; avoid ambiguous broad categories.
m=[]
for _,r in x.iterrows():
 if re.fullmatch(r'\d{4}',str(r[2])) and re.fullmatch(r'\d{2}-\d{4}',str(r[3])) and not str(r[3]).endswith('0'):m.append((int(r[2]),r[3]))
m=pd.DataFrame(m,columns=['OCC','occ_code']).drop_duplicates(); m=m[~m.OCC.duplicated(False)].merge(e); m.to_csv(O/'mapping.csv',index=False)
p=pd.read_csv(O/'cps_occupation_age_month.csv'); p=p[p.YEAR>=2020]; p['date']=pd.to_datetime(dict(year=p.YEAR,month=p.MONTH,day=1)); q=p.pivot_table(index=['OCC','date'],columns='group',values='weight_raw',aggfunc='sum',fill_value=0).reset_index(); q=q.merge(m); q['total']=q['22-25']+q['30-49']; q=q[q.total>0]; q['share']=100*q['22-25']/q.total; q['period']=q.date.dt.strftime('%Y-%m'); q['post']=(q.date>='2022-12-01').astype(int); q['exposure']=q.observed_exposure*10; q['learning']=(q.knowledge-m.knowledge.mean())/m.knowledge.std(); q['teach']=(q.teaching-m.teaching.mean())/m.teaching.std(); q['weight']=q.groupby('OCC').total.transform('mean'); q.to_csv(O/'panel.csv',index=False)
res=[]
for label,df,l,weighted in [('Primary',q,'learning',False),('Weighted',q,'learning',True),('Teaching proxy',q,'teach',False),('Exclude 2020',q[q.date>='2021-01-01'],'learning',False),('Pre-period placebo',q[q.date<'2022-12-01'].assign(post=lambda x:(x.date>='2021-07-01').astype(int)),'learning',False)]:
 f=f'share ~ C(OCC)+C(period)+post:exposure+post:{l}+post:exposure:{l}'; model=smf.wls(f,df,weights=df.weight if weighted else np.ones(len(df))).fit(cov_type='cluster',cov_kwds={'groups':df.OCC}); k=f'post:exposure:{l}'; lo,hi=model.conf_int().loc[k]; res.append([label,len(df),df.OCC.nunique(),model.params[k],lo,hi,model.pvalues[k]])
r=pd.DataFrame(res,columns=['specification','cells','occupations','coefficient_pp','lower','upper','p']);r.to_csv(O/'results.csv',index=False); print(r.to_string(index=False)); print('coverage',q.total.sum()/p.weight_raw.sum(), 'dates',q.date.nunique(), 'mapped',len(m));
plt.figure(figsize=(8,3.5)); y=np.arange(len(r));plt.errorbar(r.coefficient_pp,y,xerr=[r.coefficient_pp-r.lower,r.upper-r.coefficient_pp],fmt='o');plt.axvline(0,ls='--');plt.yticks(y,r.specification);plt.gca().invert_yaxis();plt.xlabel('Interaction estimate (percentage points), 95% CI');plt.tight_layout();plt.savefig(O/'estimates.png',dpi=180)
