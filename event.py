from pathlib import Path
import pandas as pd,numpy as np,statsmodels.api as sm
import matplotlib.pyplot as plt
P=Path(__file__).parent
q=pd.read_csv(P/'panel.csv'); q['year']=pd.to_datetime(q.date).dt.year; q['bin']=np.where(q.date<'2022-12-01',q.year.astype(str),np.where(q.date<'2023-01-01','2022 Dec',q.year.astype(str))); bins=sorted(set(q.bin)-{'2022'}); X=pd.DataFrame({f'{b}:{k}':(q.bin==b)*v for b in bins for k,v in [('exposure',q.exposure),('learning',q.learning),('interaction',q.exposure*q.learning)]}); X['y']=q.share
# Alternating projections for unbalanced two-way fixed effects.
for i in range(100):
 old=X.to_numpy().copy()
 for g in [q.OCC,q.period]: X-=X.groupby(g).transform('mean')
 if np.max(np.abs(X.to_numpy()-old))<1e-10:break
m=sm.OLS(X.pop('y'),X).fit(cov_type='cluster',cov_kwds={'groups':q.OCC}); r=pd.DataFrame({'estimate':m.params,'lower':m.conf_int()[0],'upper':m.conf_int()[1],'p':m.pvalues});r=r.loc[[b+':interaction' for b in bins]];r.to_csv(P/'event.csv'); print(r)
plt.figure(figsize=(7,3.5)); plt.errorbar(bins,r.estimate,yerr=[r.estimate-r.lower,r.upper-r.estimate],fmt='o');plt.axhline(0,ls='--');plt.ylabel('Interaction (percentage points)');plt.xticks(rotation=25);plt.tight_layout();plt.savefig(P/'event.png',dpi=160)
