from pathlib import Path
import pandas as pd,numpy as np,zipfile,re,statsmodels.formula.api as smf
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,brier_score_loss,silhouette_score
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
P=Path(__file__).resolve().parent; D=P/'inputs'
h=pd.read_csv(D/'hotel_booking.csv',usecols=['is_canceled','lead_time','hotel','arrival_date_year','arrival_date_month','stays_in_weekend_nights','stays_in_week_nights','adults','children','babies','market_segment','customer_type','is_repeated_guest','previous_cancellations','previous_bookings_not_canceled'])
y=h.pop('is_canceled'); n=['lead_time','stays_in_weekend_nights','stays_in_week_nights','adults','children','babies','is_repeated_guest','previous_cancellations','previous_bookings_not_canceled']; c=['hotel','market_segment','customer_type','arrival_date_month']; tr,te=train_test_split(np.arange(len(h)),test_size=.2,random_state=42,stratify=y)
pre=ColumnTransformer([('num',make_pipeline(SimpleImputer(strategy='median'),StandardScaler()),n),('cat',OneHotEncoder(handle_unknown='ignore'),c)])
m=make_pipeline(pre,LogisticRegression(max_iter=1000));m.fit(h.iloc[tr],y.iloc[tr]); p=m.predict_proba(h.iloc[te])[:,1]
print('HOTEL',len(h),y.mean(),len(te),roc_auc_score(y.iloc[te],p),brier_score_loss(y.iloc[te],p))
cols=['lead_time','stays_in_weekend_nights','stays_in_week_nights','adults','children','babies']; X=make_pipeline(SimpleImputer(strategy='median'),StandardScaler()).fit_transform(h[cols]); rng=np.random.default_rng(42); ix=rng.choice(len(h),3000,replace=False); scores={}; models={}
for k in range(2,7):
 km=KMeans(n_clusters=k,n_init=10,random_state=42).fit(X[tr]);scores[k]=silhouette_score(X[ix],km.predict(X[ix]));models[k]=km
k=max(scores,key=scores.get); labels=models[k].predict(X); print('SILHOUETTE',scores); seg=h[cols].assign(cluster=labels,canceled=y).groupby('cluster').agg(['mean','size']);seg.to_csv(P/'hotel_segments.csv'); print(seg.to_string());
# Occupational learning proxy: importance of updating and using relevant knowledge, and training and teaching others.
z=zipfile.ZipFile(D/'db_31_0_mysql.zip')
def rows(prefix):
 f=next(x for x in z.namelist() if '/'+prefix in x);return z.read(f).decode().splitlines()
for l in rows('01_content'):
 if 'Updating and Using Relevant Knowledge' in l or 'Training and Teaching Others' in l:print(l[:350])
a=[]
for l in rows('28_work'):
 m=re.search(r"VALUES \('([^']+)', '([^']+)', 'IM', ([\d.]+),",l)
 if m:a.append(m.groups())
a=pd.DataFrame(a,columns=['onet','element','importance']);a.importance=a.importance.astype(float);a['occ_code']=a.onet.str[:7];w=a.groupby(['occ_code','element']).importance.mean().unstack(); print(w.columns.tolist())
e=pd.read_csv(D/'job_exposure.csv'); t=pd.read_csv(D/'task_penetration.csv');print('EXPOSURE',e.describe().to_string(), 'TASK',t.penetration.describe().to_string())
# exact normalized task text match, exclude conflicting duplicates
norm=lambda s: ' '.join(s.casefold().split())
t['key']=t.task.map(norm); tt=t.groupby('key').penetration.agg(['mean','nunique']);tt=tt[tt['nunique']==1]; a=[]
for l in rows('26_task'):
 m=re.search(r"VALUES \('([^']+)', (\d+), '((?:''|[^'])*)',",l)
 if m:a.append((m[1][:7],m[2],norm(m[3].replace("''","'"))))
a=pd.DataFrame(a,columns=['occ_code','task_id','key']);a=a.join(tt['mean'].rename('penetration'),on='key');print('MATCH',len(a),a.penetration.notna().sum());a.groupby('occ_code').penetration.agg(['mean','count','size']).to_csv(P/'task_match.csv');
