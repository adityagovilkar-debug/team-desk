/* Invented sample data for the Team Desk mockups — no real names, tickets or numbers.
   Dates are relative to today, so the mockup always reads as "this week". Loaded before
   the app script; called once the app has booted (it uses the app's date helpers). */
window.MOCK=function(){
  const A=n=>addDays(n),MIN=60000;
  const at=(days,hh,mm)=>new Date(A(days)+"T"+String(hh).padStart(2,"0")+":"+String(mm||0).padStart(2,"0")+":00").getTime();
  const dow=new Date().getDay();
  const people=[
    {id:"p1",name:"Ravi Kumar",team:"portal",role:"ABAP developer"},
    {id:"p2",name:"Meera Iyer",team:"portal",role:"Fiori developer"},
    {id:"p3",name:"Sandeep Rao",team:"portal",role:"Workflow"},
    {id:"p4",name:"Tom Becker",team:"pnc",role:"Analyst"},
    {id:"p5",name:"Anita Desai",team:"pnc",role:"Basis"},
    {id:"p6",name:"Priya Nair",team:"pnc",role:"Payroll"}];
  const epics=[
    {id:"e1",name:"Payroll portal refresh",code:"PPR",health:"amber",teams:["portal"],owner:"Me",targetDate:A(40),
      headline:{text:"Payslip layout is the long pole — UAT moves to the week of the 18th.",on:A(-5)}},
    {id:"e2",name:"Leave approvals rework",code:"LAR",health:"green",teams:["portal","pnc"],owner:"Me",targetDate:A(70),
      headline:{text:"On track for the January drop.",on:A(-9)}}];
  const T=(o)=>Object.assign({source:"JIRA",priority:"P3",tags:[],assignees:[],updates:[],promises:[],hurdles:[],subtasks:[],
    raisedDate:A(-30),createdAt:at(-30,10),updatedAt:at(-5,11)},o);
  const tickets=[
    T({id:"t1",ticketId:"PRJ4101",team:"portal",title:"SSO timeout on the portal login",myStatus:"progress",assignees:["p1"],epicId:"e1",priority:"P1",
      updates:[{ts:at(-12,11,20),text:"Reproduced — the certificate chain on QA is incomplete.",syncId:"s-p0"},
               {ts:at(-5,11,8),text:"Cert chain fixed in QA; Production change planned for Thursday.",syncId:"s-p1"},
               {ts:Date.now()-9*MIN,text:"Production change done Thursday night, monitoring since — no timeouts.",syncId:"s-live"}],
      hurdles:[{id:"h1",text:"SSO test user locked",kind:"access",raisedOn:A(-12),owner:"AD team",resolvedOn:A(-5),resolution:"Unlocked by AD",clearedSyncId:"s-p1"}],
      promises:[{eta:A(-3),givenOn:A(-12)}]}),
    T({id:"t2",ticketId:"PRJ4102",team:"portal",title:"Payslip PDF misaligned for part-time staff",myStatus:"progress",assignees:["p2"],epicId:"e1",priority:"P2",
      updates:[{ts:at(-12,11,25),text:"Layout fix in progress — Adobe form, three fields shift.",syncId:"s-p0"},
               {ts:at(-5,11,12),text:"Layout fix in test; two more fields to align. New date given.",syncId:"s-p1"}],
      promises:[{eta:A(-9),givenOn:A(-20)},{eta:A(-2),givenOn:A(-12),syncId:"s-p0"},{eta:A(3),givenOn:A(-5),syncId:"s-p1"}]}),
    T({id:"t3",ticketId:"INC4107",team:"portal",title:"Leave balance off by one day after carry-over",myStatus:"review",assignees:["p1"],epicId:"e2",
      updates:[{ts:at(-5,11,16),text:"Fix deployed to QA, user testing this week.",syncId:"s-p1"}],promises:[{eta:A(2),givenOn:A(-12)}]}),
    T({id:"t4",ticketId:"PRJ4110",team:"portal",title:"Mass upload of benefits enrolments",myStatus:"blocked",assignees:["p3"],
      updates:[{ts:at(-5,11,20),text:"Code is ready; stuck until the transport is in QA.",syncId:"s-p1"}],
      hurdles:[{id:"h2",text:"Waiting on Basis to import the transport to QA",kind:"dependency",raisedOn:A(-5),owner:"Basis team",syncId:"s-p1"}],
      promises:[{eta:A(-1),givenOn:A(-15)}]}),
    T({id:"t5",ticketId:"INC4112",team:"portal",title:"Workflow stuck at the second approver",myStatus:"progress",assignees:["p2"],epicId:"e2",priority:"P2",
      updates:[{ts:at(-5,11,24),text:"Found the agent-determination rule; fixing.",syncId:"s-p1"}],
      promises:[{eta:A(6),givenOn:A(-5),syncId:"s-p1"}]}),
    T({id:"t6",ticketId:"PRJ4118",team:"portal",title:"Travel expense rounding on foreign currency",myStatus:"new",createdAt:at(-3,15),raisedDate:A(-3)}),
    T({id:"t7",ticketId:"INC4120",team:"portal",title:"Org chart not refreshing overnight",myStatus:"progress",assignees:["p3"],
      updates:[{ts:at(-5,11,28),text:"Job is failing silently at 01:00.",syncId:"s-p1"},
               {ts:Date.now()-5*MIN,text:"Job moved to 02:00 after the payroll run; they'll confirm tomorrow.",syncId:"s-live"}],
      promises:[{eta:A(1),givenOn:A(0),syncId:"s-live"}]}),
    T({id:"t8",ticketId:"PRJ4125",team:"portal",title:"Tax form translation for German employees",myStatus:"review",assignees:["p1"],epicId:"e1",theirStatus:"Resolved",
      updates:[{ts:at(-9,16),text:"Translations delivered for review."}]}),
    T({id:"t9",ticketId:"INC4099",team:"portal",title:"Duplicate IDoc on new hire",myStatus:"done",closedDate:A(-5),assignees:["p3"],
      updates:[{ts:at(-5,11,30),text:"Closed — duplicate check added to the inbound function.",syncId:"s-p1"}]}),
    T({id:"t10",ticketId:"PRJ4130",team:"portal",title:"Cost-centre derivation for contractors",myStatus:"progress",assignees:["p2"],
      updates:[{ts:at(-20,10),text:"Waiting for the finance mapping table."}]}),
    T({id:"t11",ticketId:"PRJ4131",team:"portal",title:"Portal search slow for large teams",myStatus:"new",priority:"P4",createdAt:at(-1,9),raisedDate:A(-1)}),
    T({id:"t12",ticketId:"INC2201",team:"pnc",title:"Bank details validation rejects IBANs with spaces",myStatus:"progress",assignees:["p4"],
      updates:[{ts:at(-6,15),text:"Regex fix written, in code review.",syncId:"s-c1"}],promises:[{eta:A(4),givenOn:A(-6),syncId:"s-c1"}]}),
    T({id:"t13",ticketId:"PRJ2205",team:"pnc",title:"Role for HR business partners",myStatus:"review",assignees:["p5"],epicId:"e2",
      updates:[{ts:at(-6,15,10),text:"Role built; testing with two HRBPs.",syncId:"s-c1"}]}),
    T({id:"t14",ticketId:"INC2210",team:"pnc",title:"Payroll posting job delayed on Mondays",myStatus:"blocked",assignees:["p6"],
      hurdles:[{id:"h3",text:"Needs a change window from the infrastructure team",kind:"environment",raisedOn:A(-6),owner:"Infra"}],
      updates:[{ts:at(-6,15,20),text:"Root cause is the backup overlapping the job.",syncId:"s-c1"}]}),
    T({id:"t15",ticketId:"PRJ2212",team:"pnc",title:"Leave approval reminder emails",myStatus:"new",epicId:"e2",createdAt:at(-2,12),raisedDate:A(-2)})];
  const syncs=[
    {id:"s-live",team:"portal",date:A(0),title:"Portal sync — "+fmtDate(A(0)),attendees:"Ravi, Meera, Sandeep, me",
      startedAt:Date.now()-14*MIN,covered:[{ticketId:"t1",done:true},{ticketId:"t7",done:true}],points:[],actions:[],createdAt:Date.now()-14*MIN},
    {id:"s-p1",team:"portal",date:A(-5),title:"Portal sync — "+fmtDate(A(-5)),attendees:"Ravi, Meera, Sandeep, me",closed:true,
      startedAt:at(-5,11,0),closedAt:at(-5,11,38),createdAt:at(-5,11,0),
      covered:["t1","t2","t3","t4","t5","t7","t9"].map(id=>({ticketId:id,done:true})),
      points:[{text:"They asked for UAT dates for the payslip change",by:"Meera"}],
      actions:[{id:"a1",text:"PRJ4110 — chase Basis for the QA import",owner:"Me",due:A(0),carry:true,fromSyncId:"s-p1"},
               {id:"a2",text:"Confirm the December freeze dates with Basis",owner:"Meera",due:A(-1),carry:true,fromSyncId:"s-p1"},
               {id:"a3",text:"Share the SSO error log",owner:"Ravi",done:true,resolution:"Sent — the root cause was the cert chain",fromSyncId:"s-p1"}],
      recap:{status:[{id:"t3",from:"progress",to:"review"},{id:"t4",from:"progress",to:"blocked"}],
        etas:[{id:"t2",eta:A(3),prev:A(-2),slip:true},{id:"t5",eta:A(6),prev:"",slip:false}],
        hRaised:[{id:"t4",text:"Waiting on Basis to import the transport to QA"}],hCleared:[{id:"t1",text:"SSO test user locked"}],
        closed:["t9"],added:[]}},
    {id:"s-p0",team:"portal",date:A(-12),title:"Portal sync — "+fmtDate(A(-12)),closed:true,createdAt:at(-12,11),
      covered:[{ticketId:"t1",done:true},{ticketId:"t2",done:true}],points:[],actions:[]},
    {id:"s-c1",team:"pnc",date:A(-6),title:"P&C IT sync — "+fmtDate(A(-6)),closed:true,startedAt:at(-6,15),closedAt:at(-6,15,25),createdAt:at(-6,15),
      covered:["t12","t13","t14"].map(id=>({ticketId:id,done:true})),points:[],actions:[]}];
  const rollcalls=[
    {id:"rc-p0",team:"portal",date:A(-12),syncId:"s-p0",recorded:true,createdAt:at(-12,11,2),
      demands:{counts:[{status:"In progress",n:7},{status:"In validation",n:3},{status:"Blocked",n:1}]},
      incidents:{counts:[{status:"Open",n:3},{status:"In progress",n:2},{status:"Awaiting closure",n:1}]}},
    {id:"rc-p1",team:"portal",date:A(-5),syncId:"s-p1",recorded:true,createdAt:at(-5,11,2),
      demands:{counts:[{status:"In progress",n:7},{status:"In validation",n:3},{status:"Blocked",n:2}],closed:"1",added:"2"},
      incidents:{counts:[{status:"Open",n:4},{status:"In progress",n:2},{status:"Awaiting closure",n:1}],closed:"2",added:"3",
        items:[{id:"i1",text:"Payroll posting job failed twice — rerun by hand"},
               {id:"i2",text:"SSO certificate expiry warning on QA"},
               {id:"i3",text:"Leave balance batch slow on Monday morning"},
               {id:"i4",text:"Two users locked out after a password reset"}]},
      note:"Both payroll ones are probably the same root cause, they think."}];
  const mentions=[
    {id:"m1",team:"portal",title:"Portal down for 20 minutes on Tuesday morning",area:"Portal",mentionedOn:A(-16),status:"open",syncId:"s-p0"},
    {id:"m2",team:"portal",title:"Benefits page showing last year's plans",area:"Benefits",mentionedOn:A(-5),status:"open",syncId:"s-p1"}];
  return {version:typeof DATA_VERSION!=="undefined"?DATA_VERSION:1,
    settings:{teams:[{id:"portal",name:"Portal",mode:"managed",outsourced:true,vendorName:"Acme IT"},{id:"pnc",name:"P&C IT",mode:"managed"}],
      syncDays:{portal:[dow,(dow+2)%7],pnc:[(dow+1)%7]},autosave:true,encryption:false},
    tickets,people,epics,syncs,rollcalls,mentions,meetings:[],contacts:[],patterns:[],incidents:[],forecasts:[],
    agenda:[{id:"ag1",team:"portal",text:"Boss asked: who signs off the payslip layout?"}],
    decisions:[{id:"d1",date:A(-5),text:"UAT for the payslip change runs in the week of the 18th",by:"Meera",syncId:"s-p1",epicId:"e1"}],
    risks:[{id:"r1",title:"Vendor's payroll specialist leaves in December",severity:"high",status:"open",owner:"Me",raisedOn:A(-30),reviewOn:A(-1),
      mitigation:"Ask for a handover plan and a named backup"}],
    approvals:[{id:"ap1",team:"portal",kind:"prod",ticketId:"t1",title:"Move the SSO certificate fix to Production",requestedOn:A(-1),status:"pending"}],
    capacity:[{team:"portal",quarter:curQuarter(),hours:600}],
    efforts:[{team:"portal",ticketId:"t2",month:curMonth(),hours:42,approved:true},{team:"portal",ticketId:"t4",month:curMonth(),hours:30,approved:false}]};
};
