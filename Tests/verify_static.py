"""Artifact verification and fixture evaluation. Does not execute UiPath/VB."""
from pathlib import Path
import xml.etree.ElementTree as E
import json,zipfile,re
P=Path(__file__).resolve().parents[1]
X='{http://schemas.microsoft.com/winfx/2006/xaml}'
A='{http://schemas.microsoft.com/netfx/2009/xaml/activities}'
U='{http://schemas.uipath.com/workflow/activities}'
N={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def xlsx(file):
 with zipfile.ZipFile(file) as z:
  for n in z.namelist():
   if n.endswith('.xml') or n.endswith('.rels'):E.fromstring(z.read(n))
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(n.itertext()) for n in E.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',N)]
  workbook=E.fromstring(z.read('xl/workbook.xml'))
  first=workbook.find('s:sheets/s:sheet',N)
  rid=first.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']
  rel=next(e for e in E.fromstring(z.read('xl/_rels/workbook.xml.rels')) if e.attrib['Id']==rid)
  target=rel.attrib['Target'];path=target.lstrip('/') if target.startswith('/') else 'xl/'+target
  rows=[]
  for r in E.fromstring(z.read(path)).findall('s:sheetData/s:row',N):
   vals={}
   for c in r.findall('s:c',N):
    col=re.match(r'[A-Z]+',c.attrib['r'])[0];index=0
    for ch in col:index=index*26+ord(ch)-64
    if c.attrib.get('t')=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//s:t',N))
    else:
     v=c.find('s:v',N);v=v.text if v is not None else ''
     if c.attrib.get('t')=='s':v=shared[int(v)]
    vals[index-1]=v
   rows.append([vals.get(i,'') for i in range(max(vals,default=-1)+1)])
  headers=rows[0];data=[dict(zip(headers,r+['']*(len(headers)-len(r)))) for r in rows[1:] if any(r)]
  return headers,data
required=['Main','ReadGmail','ClassifyComplaint','DeterminePriority','FindDepartment','GenerateResponse','RouteComplaint','LogComplaint','GeneratePriorityReport','HandleExceptions']
files={f.stem:f for f in P.rglob('*.xaml')}
assert all(n in files for n in required)
contracts={}
for name,f in files.items():
 tree=E.parse(f);root=tree.getroot()
 members=root.find(X+'Members')
 contracts[name]={e.attrib['Name']:e.attrib['Type'] for e in members}
for name,f in files.items():
 for node in E.parse(f).iter(U+'InvokeWorkflowFile'):
  target=node.attrib['DisplayName']
  if target=='Run sample controller':target='Main'
  assert target in files,(name,target)
  assert target+'.xaml' in node.attrib['WorkflowFileName']
  args=node.find(U+'InvokeWorkflowFile.Arguments')
  got={a.attrib[X+'Key']:a.tag.split('}')[-1]+'('+a.attrib[X+'TypeArguments']+')' for a in args}
  assert got==contracts[target],(name,target,got,contracts[target])
rheaders,routes=xlsx(P/'Data/Routing.xlsx')
assert rheaders==['Organization','Category','Department','DepartmentEmail','EscalationEmail','Active']
assert len(routes)==56
assert len({(r['Organization'],r['Category']) for r in routes})==56
companies={r['Organization'] for r in routes}
assert companies=={'Flipkart','Amazon','Samsung','Airtel','Jio','Swiggy','Zomato','Meesho'}
assert all(not r['DepartmentEmail'] and not r['EscalationEmail'] and r['Active'] in ('0','FALSE','false') for r in routes)
fheaders,faq=xlsx(P/'Data/FAQ_KnowledgeBase.xlsx')
assert fheaders==['Organization','Category','FAQQuestion','ApprovedResponse','EscalationRequired'] and len(faq)==56
mandatory=['TicketID','GmailMessageID','ReceivedDate','CustomerEmail','Subject','ComplaintText','Organization','Category','Sentiment','Priority','Confidence','Department','DepartmentEmail','SuggestedResponse','Status','ForwardedDate','ErrorMessage']
for n in ['Complaints_Log','Priority_Report']:
 headers,data=xlsx(P/f'Data/{n}.xlsx');assert headers[:17]==mandatory and len(data)==0
_,testcases=xlsx(P/'Data/TestCases.xlsx');assert len(testcases)==24
classcode=next(E.parse(files['ClassifyComplaint']).iter(U+'InvokeCode')).attrib['Code']
patterns=re.findall(r'\{"([^"\n]+)", New String\(\)\{([^}]+)\}\}',classcode)
keywords={k:re.findall(r'"([^"]+)"',v) for k,v in patterns}
assert len(keywords)==6
samples=json.loads((P/'Data/SampleEmails.json').read_text())
def classify(row):
 text=re.sub(r'\s+',' ',row['Subject']+' '+row['ComplaintText']).lower()
 found=[c for c in companies if re.search(r'(?<!\w)'+re.escape(c)+r'(?!\w)',text,re.I)]
 org=found[0] if len(found)==1 else 'Unknown'
 scores={}
 for cat,words in keywords.items():
  score=0
  for k in words:
   suffix='' if ' ' in k else '(?:s|ed|ing)?'
   if re.search(r'(?<!\w)'+re.escape(k)+suffix+r'(?!\w)',text):score+=4 if ' ' in k else 1 if k in ['order','package','not working'] else 3
  scores[cat]=score
 rank=sorted(scores.items(),key=lambda kv:(-kv[1],kv[0]))
 cat='General' if rank[0][1]==0 else rank[0][0]
 manual=len(found)!=1 or rank[0][1]==0 or rank[0][1]==rank[1][1] or not row['ComplaintText'].strip()
 route=[r for r in routes if r['Organization']==org and r['Category']==cat]
 department=route[0]['Department'] if len(route)==1 else 'Manual Review'
 return org,cat,department,manual
expect=[('Flipkart','Order/Delivery','Order Support'),('Samsung','Warranty','Warranty and Service'),('Amazon','Refund','Payments and Refunds'),('Airtel','Technical','Technical Support'),('Unknown','Returns','Manual Review')]
for row,e in zip(samples[:5],expect):assert classify(row)[:3]==e,(row,classify(row),e)
assert classify(samples[9])[3] and classify(samples[10])[3] and classify(samples[12])[3]
assert len({r['GmailMessageID'] for r in samples})==13
assert all(r['CustomerEmail']=='customer@example.invalid' for r in samples)
sendcode=next(E.parse(files['SendGmail']).iter(U+'InvokeCode')).attrib['Code']
assert 'If in_SendEnabled Then Throw' in sendcode
assert json.loads((P/'Config/AuthorizedRecipients.json').read_text())==[]
assert not (P/'Config/SenderBound.flag').exists()
assert not (P/'Config/SendApproval.json').exists()
print(f'PASS: {len(files)} XAML structures, exact invoke argument contracts, five XLSX schemas, 56 routes/FAQs, 24 cases, five demo fixtures, ambiguous fixtures and disabled sender guards. UiPath/VB runtime NOT executed.')
