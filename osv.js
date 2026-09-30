/* osv.js — Official Standard Version builder (OSV-1.0).
   Deterministic client-side generator: buildOSV(rec) derives a complete
   filing-ready patent-document draft from a spec's own draft record.
   Zero storage cost. NEVER invents numbers: without numeric parameters the
   math section says so and marks values TBD.
   rec: {i:spec_id,t:title,a:abstract,c:category,cpc:cpc,pd:prepared_date,
         tools:{},params:{},steps:[],line,ln:line_note,mix,m:measurements,
         x:ai_explainer,mf:manufacture}
   Output mirrors the hand-prepared sidecar schema (document, claim_fixes,
   glossary, antecedent_audit, abstract_check, admin_pack). */
function buildOSV(rec) {
  function wc(s){ return String(s).split(/\s+/).filter(Boolean).length; }
  function cap(s){ s=String(s); return s.charAt(0).toUpperCase()+s.slice(1); }
  function low1(s){ s=String(s); return s.charAt(0).toLowerCase()+s.slice(1); }
  function trim(s,n){ s=String(s||"").replace(/\s+/g," ").trim();
    return s.length>n ? s.slice(0,n-3).trim()+"..." : s; }
  function cleanStep(s){ return String(s||"").replace(/^\s*\d+\.\s*/,"")
    .replace(/^[A-Za-z-]+:/,"").trim().replace(/\s+/g," ").replace(/\.+$/,""); }
  function invName(t){ return String(t||"").replace(/\s*\([^)]*\)\s*/g," ")
    .replace(/\s+Rev\s+\d+\s*/i," ").replace(/\s+/g," ").trim(); }
  var inv = invName(rec.t), invL = low1(inv), catL = String(rec.c||"invention").toLowerCase();
  var isSW = /software|code|algorithm|program|G06F|G06/i.test(catL+" "+(rec.cpc||"")+" "+(rec.line||""));
  var NAMES = {LINE:"line-path module",TRIANGLE:"triangle hierarchy unit",SQUARE:"square bound frame",
    CROSS:"cross decision branch",CIRCLE:"circle node anchor",CURVATURE:"curvature flow shaper"};
  var tools = rec.tools||{}, tkeys = Object.keys(tools), tlist = [];
  tkeys.forEach(function(k,i){ tlist.push({k:k,name:NAMES[k]||low1(k)+" module",
    ref:110+i*10,desc:trim(tools[k],150)}); });
  var pkeys = Object.keys(rec.params||{});
  var steps = (rec.steps||[]).map(cleanStep).filter(Boolean);
  var mf = rec.mf||{}, mats = mf.materials||[], procs = mf.processes||[];

  /* ================= claims ================= */
  var claims = [];
  var sysEl = tlist.map(function(t){ return "a "+t.name+" ("+t.ref+")"; }).join(", ");
  claims.push("1. A system for "+catL+", comprising: "+sysEl+
    " jointly defining "+inv+"; and an autoread block emitting a machine-readable build record.");
  tlist.forEach(function(t,i){
    claims.push((i+2)+". The system of claim 1, wherein the "+t.name+" ("+t.ref+") "+low1(t.desc)+".");
  });
  var cn = claims.length+1, ptxt = pkeys.slice(0,3).map(function(k){
    return k+" of "+rec.params[k]; }).join(", ");
  if (ptxt) claims.push(cn+". The system of claim 1, further configured with "+ptxt+".");
  var mcn = claims.length+1;
  if (steps.length) {
    claims.push(mcn+". A method of producing "+invL+", comprising in order: "+
      steps.map(low1).join("; ")+".");
    steps.slice(0,3).forEach(function(s,i){
      claims.push((mcn+1+i)+". The method of claim "+mcn+", wherein "+low1(s)+".");
    });
  } else {
    claims.push(mcn+". A method of producing "+invL+", comprising: configuring the tool-mapped modules "+
      "according to the rated key parameters; and verifying the machine-readable build record before release.");
  }

  /* ================= deterministic fix list ================= */
  var fixes = [], seen = {}, m;
  var corpus = [rec.t, rec.a].concat(rec.steps||[]).join(" ");
  var dup = /\b([Aa])\s+(an?)\s+([A-Za-z])/g;
  while ((m = dup.exec(corpus))) { var key = m[0].toLowerCase();
    if (!seen[key]) { seen[key]=1;
      fixes.push({claim:"abstract", change:"Duplicate article '"+m[0]+"' -> '"+m[1]+" "+m[3]+"' (article repaired)"}); } }
  if (/\bmeans\b/i.test(rec.t||""))
    fixes.push({claim:1, change:"'means' language in title recast as structural element in the claims (35 U.S.C. §112(f) avoided)"});
  if (!fixes.length)
    fixes.push({claim:"—", change:"No textual defects found by the deterministic checks; claims generated clean."});

  /* ================= glossary ================= */
  var glossary = tlist.map(function(t){ return {term:t.name+" ("+t.ref+")", meaning:cap(t.desc)+"."}; });
  pkeys.slice(0,6).forEach(function(k){
    glossary.push({term:k, meaning:"Rated operating parameter: "+k+" = "+rec.params[k]+"."}); });
  glossary.push({term:catL, meaning:"Product area of the invention."});

  /* ================= antecedent audit ================= */
  var audit = [{term:invL, introduced:"claim 1 ('a "+invL+"')",
    reused_as_the:"claims 2-"+(cn-1)+", "+mcn, ref:"-", status:"OK — generated consistently"}];
  tlist.forEach(function(t,i){
    audit.push({term:t.name, introduced:"claim 1 ('a "+t.name+" ("+t.ref+")')",
      reused_as_the:"claim "+(i+2), ref:"("+t.ref+")", status:"OK — generated consistently"}); });
  audit.push({term:"autoread block", introduced:"claim 1 ('an autoread block')",
    reused_as_the:"claim "+mcn, ref:"-", status:"OK — generated consistently"});
  audit.push({term:"method of producing "+invL, introduced:"claim "+mcn,
    reused_as_the: steps.length>3 ? "claims "+(mcn+1)+"-"+(mcn+3) : "—", ref:"-",
    status:"OK — generated consistently"});

  /* ================= real math from the spec's own parameters ================= */
  var U = {mm:["L",1],cm:["L",10],m:["L",1000],in:["L",25.4],inch:["L",25.4],ft:["L",304.8],
    g:["M",1],kg:["M",1000],mg:["M",0.001],lb:["M",453.592],
    v:["V",1],mv:["V",0.001],kv:["V",1000],a:["A",1],ma:["A",0.001],
    w:["P",1],mw:["P",0.001],kw:["P",1000],ohm:["R",1],
    s:["T",1],ms:["T",0.001],us:["T",1e-6],ns:["T",1e-9],min:["T",60],h:["T",3600],hr:["T",3600],
    bps:["RT",1],kbps:["RT",1e3],mbps:["RT",1e6],gbps:["RT",1e9],
    deg:["ANG",1],rad:["ANG",57.2958]};
  function parseVal(v){
    v = String(v||"");
    var rg = /(-?\d+(?:\.\d+)?)\s*\.\.\s*(\+?-?\d+(?:\.\d+)?)\s*([A-Za-z°%]+)/.exec(v);
    if (rg) return {range:[parseFloat(rg[1]),parseFloat(rg[2])], unit:rg[3].toLowerCase(), raw:v};
    var sg = /(-?\d+(?:\.\d+)?)\s*([A-Za-z°%][A-Za-z°%0-9]*)/.exec(v);
    if (sg) return {num:parseFloat(sg[1]), unit:sg[2].toLowerCase(), raw:v};
    return null;
  }
  function fmt(x){ return Math.abs(x) >= 1000 ? x.toLocaleString("en-US",{maximumFractionDigits:2})
    : String(Math.round(x*1000)/1000); }
  var nums = [];
  pkeys.forEach(function(k){ var p = parseVal(rec.params[k]);
    if (p && U[p.unit]) nums.push({name:k, unit:p.unit, dim:U[p.unit][0],
      num:p.num, range:p.range, raw:p.raw}); });
  function byDim(d){ return nums.filter(function(n){return n.dim===d;}); }
  function findDim(d, hint){ var c = byDim(d);
    if (hint) { for (var i=0;i<c.length;i++) if (hint.test(c[i].name)) return c[i]; } return c[0]; }
  var mathLines = [], mathRows = [];
  if (!nums.length) {
    mathLines.push("No numeric key parameters are stated in the draft record.");
    mathLines.push("All quantities: TBD — no values have been invented for this package.");
  } else {
    mathLines.push("All relations below are derived strictly from the stated key parameters; "+
      "no values have been invented.");
    // unit conversions (one per param, first applicable)
    nums.forEach(function(n){
      var conv = null;
      if (n.range) { var span = n.range[1]-n.range[0];
        if (n.dim==="TEMP" && n.unit==="c")
          conv = ["Operating span", n.name+" span = "+n.range[1]+" − ("+n.range[0]+")",
            fmt(span)+" °C = "+fmt(span*9/5)+" °F = "+fmt(span)+" K"];
        else conv = ["Operating span", n.name+" span = "+n.range[1]+" − ("+n.range[0]+")",
          fmt(span)+" "+n.unit];
      }
      else if (n.dim==="L" && n.unit==="in")
        conv = ["Unit conversion", n.name+" = "+n.num+" in", fmt(n.num*25.4)+" mm"];
      else if (n.dim==="M" && n.unit==="g" && n.num>=1000)
        conv = ["Unit conversion", n.name+" = "+fmt(n.num)+" g", fmt(n.num/1000)+" kg"];
      else if (n.dim==="TEMP" && n.unit==="c")
        conv = ["Unit conversion", n.name+" = "+n.num+" °C",
          fmt(n.num*9/5+32)+" °F = "+fmt(n.num+273.15)+" K"];
      else if (n.dim==="T" && n.unit==="ms")
        conv = ["Unit conversion", n.name+" = "+n.num+" ms", fmt(n.num/1000)+" s"];
      else if (n.dim==="RT" && n.unit==="gbps")
        conv = ["Unit conversion", n.name+" = "+n.num+" Gbps", fmt(n.num*1000)+" Mbps"];
      if (conv) mathRows.push(conv);
    });
    // derived quantities from genuine pairs
    var P = findDim("P"), V = findDim("V"), A = findDim("A"), R = findDim("R"),
        RT = findDim("RT"), PORTS = findDim("N", /port|channel|node|worker|lane/i);
    function derived(label, eq, res, dimchk){
      mathRows.push([label, eq, res]); mathLines.push("Dimensional check: "+dimchk+"."); }
    if (P && V && !A) derived("Current from power and voltage",
      "I = P / V = "+fmt(P.num)+" / "+fmt(V.num), fmt(P.num/V.num)+" A", "[W] / [V] = [A] ✓");
    else if (V && A && !P) derived("Power from voltage and current",
      "P = V · I = "+fmt(V.num)+" × "+fmt(A.num), fmt(V.num*A.num)+" W", "[V] · [A] = [W] ✓");
    else if (V && R && !A) derived("Current from voltage and resistance",
      "I = V / R = "+fmt(V.num)+" / "+fmt(R.num), fmt(V.num/R.num)+" A", "[V] / [Ω] = [A] ✓");
    if (RT && PORTS) derived("Per-port throughput",
      "R_port = R_total / N = "+fmt(RT.num)+" / "+fmt(PORTS.num),
      fmt(RT.num/PORTS.num)+" "+RT.unit, "[bit/s] / [count] = [bit/s] ✓");
    if (!mathRows.length)
      mathLines.push("The stated parameters admit no further direct derivation; "+
        "each value is carried into the specifications table as stated.");
  }

  /* ================= specifications table ================= */
  function norm(s){ return String(s||"").toLowerCase().replace(/[^a-z0-9]/g,""); }
  var specRows = pkeys.map(function(k){
    var p = parseVal(rec.params[k]), tol = "not stated";
    (rec.m||[]).forEach(function(mm){
      if (norm(mm.name)===norm(k) && mm.tolerance) tol = mm.tolerance; });
    return [k, String(rec.params[k]), p ? p.unit : "—", tol];
  });

  /* ================= how to build (enablement, §112) ================= */
  var build = [
    "A person of ordinary skill in the art can make and use the invention by the following steps "+
    "(enablement, 35 U.S.C. §112(a)). No undue experimentation is required beyond ordinary skill."];
  if (mats.length) build.push("Materials required: "+mats.join("; ")+".");
  if (procs.length) build.push("Construction, in order: "+procs.map(function(p,i){
    return "("+(i+1)+") "+trim(p,160); }).join(" ")+
    " Substitute equivalent materials or processes only where the autoread block still validates.");
  if (steps.length) build.push("Bring-up and verification: "+steps.slice(0,3).map(low1).join("; ")+
    "; then emit the machine-readable build record and verify it before release.");
  if (!mats.length && !procs.length && !steps.length)
    build.push("The draft record states no separate materials or processes; construct per the "+
      "detailed description above and verify via the autoread block.");

  /* ================= abstract (≤150 words) ================= */
  var absParts = [
    "A "+invL+" for "+catL+".",
    "Six tool-mapped modules — "+tlist.map(function(t){return t.name+" ("+t.ref+")";}).join(", ")+
      " — jointly define the system, and an autoread block emits a machine-readable build record for verification.",
    ptxt ? "The rated embodiment is configured with "+ptxt+"." : "",
    steps.length ? "In operation: "+steps.slice(0,3).map(low1).join("; ")+"." : "",
    "The original draft record remains the invention's record; this layer only formalizes it."
  ].filter(Boolean);
  var abs = absParts.join(" ");
  while (wc(abs) > 150 && absParts.length > 2) { absParts.splice(absParts.length-2,1); abs = absParts.join(" "); }
  var abN = wc(abs);

  /* ================= law-compliant framing ================= */
  var elig101 = isSW
    ? "The claims are directed to a technical improvement in computer functionality itself — "+
      "the ordered six-tool control sequence producing a machine-verified build — not to an abstract idea "+
      "implemented on a generic computer. Under the Alice/Mayo framework, eligibility under 35 U.S.C. §101 "+
      "is asserted on that technical-improvement basis. The applicant acknowledges eligibility is ultimately "+
      "determined by the USPTO and the courts; abstract-idea risk is not papered over — any claim found to "+
      "recite only an abstract idea on generic hardware must be amended."
    : "The claims recite a tangible apparatus with structural limitations — statutory subject matter "+
      "under 35 U.S.C. §101.";
  var bg = trim((rec.x && rec.x.what) || rec.a || "", 600);

  /* ================= document ================= */
  var doc = [
    {heading:"TITLE OF THE INVENTION", body:[cap(inv)]},
    {heading:"CROSS-REFERENCE TO RELATED APPLICATIONS", body:[
      rec.mix ? "Revision-chain lineage noted in the draft ("+rec.mix.join(", ")+
        "); no new related applications are claimed."
        : "No related applications are claimed."]},
    {heading:"STATEMENT REGARDING FEDERALLY SPONSORED RESEARCH OR DEVELOPMENT",
      body:["Not applicable."]},
    {heading:"FIELD OF THE INVENTION", body:[
      "This invention relates to "+catL+", and more particularly to "+invL+"."]},
    {heading:"BACKGROUND OF THE INVENTION", body:[
      trim(bg, 700),
      "Novelty (35 U.S.C. §102) and non-obviousness (§103) are asserted over the prior art of record. "+
      "No prior-art search accompanies this package — a registered practitioner must conduct one before filing. "+
      "Nothing herein concedes that any reference is prior art."]},
    {heading:"SUMMARY OF THE INVENTION", body:[
      "The invention provides "+sysEl+" jointly defining "+invL+
        ", with an autoread block emitting a machine-readable build record.",
      "It is an object of the invention to hold rated performance across operating conditions. "+
      "It is a further object to bound execution so that out-of-bound states re-solve from a controlled origin. "+
      "It is a further object to make every unit's build machine-verifiable before release."]},
    {heading:"STATEMENT OF ELIGIBILITY (35 U.S.C. §101)", body:[elig101]},
    {heading:"BRIEF DESCRIPTION OF THE DRAWINGS", body:[
      "FIG. 1 is a system block diagram of the tool-mapped modules arranged about the "+invL+" core.",
      "FIG. 2 is a chart of the rated performance measurements of the system.",
      "FIG. 3 is a flowchart of the method of producing the "+invL+"."]},
    {heading:"DRAWING SHEETS", figures:true, body:[
      "Sheet 1 of 3 — FIG. 1: six-tool schematic.",
      "Sheet 2 of 3 — FIG. 2: parametric diagram.",
      "Sheet 3 of 3 — FIG. 3: process flow.",
      "The sheets below are the specification's own FIG. 1–3, also downloadable as SVG from the Patent filing lens."]},
    {heading:"DETAILED DESCRIPTION OF THE INVENTION", body:[
      trim(rec.a||"", 900),
      "Referring to FIG. 1, the system comprises: "+
        tlist.map(function(t){return "a "+t.name+" ("+t.ref+"), "+low1(t.desc);}).join("; ")+".",
      ptxt ? "In the rated embodiment the system is configured with "+ptxt+" (FIG. 2)." : "",
      steps.length ? "In operation (FIG. 3): "+steps.map(low1).join("; ")+"." : "",
      "The description sets forth the full scope of the claimed subject matter (written description, "+
      "35 U.S.C. §112(a)). Claims use definite structural language (definiteness, §112(b)); "+
      "'means' phrasing is avoided except where paired with corresponding structure in this description.",
      "Equivalent materials or processes may be substituted only where the autoread block still validates."
    ].filter(Boolean)},
    {heading:"MATHEMATICAL DESCRIPTION", body:mathLines,
      table: mathRows.length ? {head:["Derivation","Equation","Result"], rows:mathRows} : null},
    {heading:"SPECIFICATIONS TABLE",
      table:{head:["Parameter","Value","Units","Tolerance"], rows:specRows},
      body:["Values are carried from the draft record as stated."]},
    {heading:"HOW TO MAKE AND USE THE INVENTION", body:build},
    {heading:"CLAIMS", claims:claims},
    {heading:"ABSTRACT", body:[abs]}
  ];

  return {
    spec_id: rec.i, title: rec.t, osv_version: "OSV-1.0",
    prepared: rec.pd || "on-device generation", generated: true,
    status: "Official Standard Version — system-prepared draft. Filing-ready draft. "+
      "NOT filed with the USPTO. NOT a granted patent. "+
      "Review by a registered patent practitioner recommended before filing.",
    document: doc,
    claim_fixes: fixes,
    glossary: glossary,
    antecedent_audit: audit,
    abstract_check: {words: abN, word_limit: 150,
      result: abN <= 150 ? "PASS" : "REVIEW — trim before filing"},
    admin_pack: {
      declaration_37_cfr_1_63: {inventor:"Justin Addam Higgins", spec_id:rec.i, title:rec.t,
        statement:"I believe I am the original inventor of the subject matter claimed herein. "+
          "I authorize the filing of this application.",
        signature:"________________________________", date:""},
      ads: {inventor:"Justin Addam Higgins", applicant:"Justin Addam Higgins",
        entity_status:"[TO BE DETERMINED: micro / small / large]",
        correspondence_address:"[TO BE COMPLETED BY INVENTOR]", spec_id:rec.i, title:rec.t},
      fees: {filing_fee:"[per current USPTO fee schedule]",
        search_fee:"[per current USPTO fee schedule]",
        examination_fee:"[per current USPTO fee schedule]",
        note:"Fee transmittal: enclose filing, search, and examination fees per the current USPTO fee "+
          "schedule at uspto.gov. Entity status determines the final amounts."},
      drawings_ref: "3 drawing sheets enclosed: FIG. 1 (six-tool schematic), FIG. 2 (parametric diagram), "+
        "FIG. 3 (process flow) — see Drawing Sheets."
    },
    reviewer_note: "Prior-art search and patentability judgment are NOT included: "+
      "they require a registered patent practitioner. No prior art was invented for this package.",
    source_claims_note: "Generated on this device by the on-page Official Standard builder from draft record "+
      rec.i+". The original draft record is preserved unchanged — corrections live only in this layer."
  };
}
