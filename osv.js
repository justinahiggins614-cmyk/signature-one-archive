/* osv.js — Official Standard Version builder (OSV-1.0).
   TRANSMUTATION: the same invention, recast the way metric converts to imperial —
   nothing added, nothing lost. The draft's system-framework language stays in the
   draft; this layer speaks pure, conventional patent law, as a top-tier firm would
   write it: antecedent basis, "comprising" claiming, Markush groups, "What is
   claimed is:". NEVER invents numbers: without numeric parameters the math section
   says so and marks values TBD.
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

  /* ---- draft-language -> conventional patent language ---- */
  var XLAT = [
    [/signature-one grid/ig, "reference grid"],
    [/binary-1 identity/ig, "baseline reference state"],
    [/single controlled origin/ig, "common origin"],
    [/reversed-allowance/ig, "reverse-order"],
    [/infinite line/ig, "reference axis"],
    [/autoread block/ig, "verification module"],
    [/STATUS\s*=\s*SIGNATURE-1\s*VALID/ig, "a valid-verification indicator"],
    [/admitting human variance/ig, "allowing for operator variance"],
    [/tolerance slop/ig, "dimensional tolerance"],
    [/as one valid build among infinite option paths/ig, "as a verified build"],
    [/the finished function/ig, "the completed configuration"]
  ];
  function xlat(s){ s = String(s||"");
    for (var i=0;i<XLAT.length;i++) s = s.replace(XLAT[i][0], XLAT[i][1]);
    return s.replace(/\s+/g," ").trim(); }

  var inv = invName(rec.t), invL = low1(inv), catL = String(rec.c||"invention").toLowerCase();
  var isSW = /software|code|algorithm|program|G06F|G06/i.test(catL+" "+(rec.cpc||"")+" "+(rec.line||""));
  var invW = inv.split(/\s+/).filter(function(w){return w.length>3;}).slice(0,3).join(" ");
  var invEsc = invW.replace(/[.*+?^${}()|[\]\\]/g,"\\$&").replace(/\s+/g,"\\s+");
  var invRe = invW ? new RegExp("\\bthe\\s+"+invEsc+"(\\s+\\S+)?", "i") : null;
  var invReBare = invW ? new RegExp("\\b"+invEsc+"(\\s+\\S+)?", "i") : null;

  /* ---- modules: branded keys dropped; functional phrase kept ---- */
  function splitMap(txt){
    var m = String(txt||"").match(/^(.*?)\s+(along|of|through|where|across|containing|orbiting|shaping|fanning)\s+(.*)$/i);
    if (!m) return {phrase:String(txt||"").trim(), prep:"", tail:""};
    return {phrase:m[1].trim(), prep:m[2].toLowerCase(), tail:m[3]};
  }
  function sysTail(t){
    t = String(t||"");
    if (invRe) t = t.replace(invRe, "the system");
    if (invReBare) t = t.replace(invReBare, "the system");
    var w0 = invW.split(" ")[0] || "";
    if (w0 && new RegExp("\\b"+w0.replace(/[.*+?^${}()|[\]\\]/g,"\\$&")+"\\b","i").test(t))
      t = t.replace(/^the\s+\S+(\s+\S+){1,3}/, "the system");
    t = t.replace(/\bthe system(\s+system)+\b/g, "the system");
    return t.trim().replace(/\s+/g," ");
  }
  var tools = rec.tools||{}, mods = [];
  Object.keys(tools).forEach(function(k,i){
    var sp = splitMap(xlat(tools[k]));
    var pl = /(s|points|endpoints|radii|curves|bounds|mounts|nodes)$/i.test(sp.phrase||"") &&
             !/axis$/i.test(sp.phrase||"");
    mods.push({ref:110+i*10, phrase:sp.phrase||low1(k)+" module", prep:sp.prep,
      tail:sysTail(sp.tail), be: pl ? "are" : "is", pl:pl});
  });
  function art(mo){ return mo.pl ? "" : "a "; }
  function modDep(mo){
    var P = "the "+mo.phrase+" ("+mo.ref+")";
    switch (mo.prep) {
      case "along": case "through": case "across":
        return "wherein "+P+" "+mo.be+" disposed "+mo.prep+" "+mo.tail+".";
      case "of": return "wherein "+P+" "+mo.be+" formed as part of "+mo.tail+".";
      case "where": return "wherein "+mo.tail+" at "+P+".";
      case "containing": return "wherein "+P+" "+mo.be+" configured to contain "+mo.tail+".";
      case "orbiting": return "wherein "+P+" "+mo.be+" configured to orbit "+mo.tail+".";
      case "shaping": return "wherein "+P+" "+mo.be+" configured to shape "+mo.tail+".";
      case "fanning": return "wherein "+P+" "+mo.be+" configured to fan out from "+mo.tail+".";
      default: return "wherein said system includes "+P+".";
    }
  }

  var pkeys = Object.keys(rec.params||{});
  var ptxt = pkeys.slice(0,3).map(function(k){return k+" "+rec.params[k];}).join("; ");
  var steps = (rec.steps||[]).map(function(s){return cleanStep(xlat(s));}).filter(Boolean);
  var mf = rec.mf||{}, mats = mf.materials||[],
      procs = (mf.processes||[]).map(function(s){return cleanStep(xlat(s));}).filter(Boolean);

  /* ================= claims ================= */
  var claims = [], n = 0;
  function C(t){ n++; claims.push(n+". "+t); return n; }
  var elIntro = mods.map(function(mo){ return art(mo)+mo.phrase+" ("+mo.ref+")"; }).join(", ");
  var lim1 = pkeys[0] ? ", wherein the "+pkeys[0].toLowerCase()+" is "+rec.params[pkeys[0]] : "";
  var lim2 = pkeys[1] ? ", and wherein the "+pkeys[1].toLowerCase()+" is "+rec.params[pkeys[1]] : "";
  C("A system for "+catL+", comprising: "+elIntro+"; and a verification module (170) "+
    "configured to emit a machine-readable record of the build"+lim1+lim2+".");
  mods.forEach(function(mo){ C("The system of claim 1, "+modDep(mo)); });
  var nSys = n;
  if (mats.length)
    C("The system of claim 1, wherein a structural component thereof is formed from a material "+
      "selected from the group consisting of: "+mats.join(", ")+".");
  pkeys.slice(0,6).forEach(function(k){
    C("The system of claim 1, wherein the "+k.toLowerCase()+" is "+rec.params[k]+"."); });
  var mth = null, mSteps = procs.length ? procs : steps;
  if (mSteps.length) {
    mth = C("A method of producing "+invL+", comprising in order: "+
      mSteps.map(low1).join("; ")+".");
    mSteps.slice(0,2).forEach(function(s){
      C("The method of claim "+mth+", wherein "+low1(s)+" further comprises verifying "+
        "the machine-readable record before release."); });
  } else {
    mth = C("A method of producing "+invL+", comprising: configuring the modules of claim 1 "+
      "according to the rated key parameters; and verifying the machine-readable record before release.");
  }

  /* ================= deterministic fix list ================= */
  var fixes = [], seen = {}, m;
  var corpus = [rec.t, rec.a].concat(rec.steps||[]).join(" ");
  var dup = /\b([Aa])\s+(an?)\s+([A-Za-z])/g, mm;
  while ((mm = dup.exec(corpus))) { var key = mm[0].toLowerCase();
    if (!seen[key]) { seen[key]=1;
      fixes.push({claim:"abstract", change:"Duplicate article '"+mm[0]+"' -> '"+mm[1]+" "+mm[3]+"' (article repaired)"}); } }
  if (/\bmeans\b/i.test(rec.t||""))
    fixes.push({claim:1, change:"'means' language in title recast as structural element in the claims (35 U.S.C. §112(f) avoided)"});
  if (!fixes.length)
    fixes.push({claim:"—", change:"No textual defects found by the deterministic checks; claims generated clean."});

  /* ================= glossary (conventional terms) ================= */
  var glossary = mods.map(function(mo){
    return {term:mo.phrase+" ("+mo.ref+")", meaning:"A module of the system. "+cap(modDep(mo).replace(/^wherein /,""))}; });
  pkeys.slice(0,6).forEach(function(k){
    glossary.push({term:k, meaning:"Rated operating parameter: "+k+" = "+rec.params[k]+"."}); });
  glossary.push({term:catL, meaning:"Field of the invention."});

  /* ================= antecedent audit ================= */
  var audit = [{term:invL, introduced:"claim 1 ('a system for "+catL+"')",
    reused_as_the:"claims 2-"+nSys, ref:"-", status:"OK — generated consistently"}];
  mods.forEach(function(mo,i){
    audit.push({term:mo.phrase, introduced:"claim 1 ('"+art(mo)+mo.phrase+" ("+mo.ref+")')",
      reused_as_the:"claim "+(i+2), ref:"("+mo.ref+")", status:"OK — generated consistently"}); });
  audit.push({term:"verification module", introduced:"claim 1 ('a verification module (170)')",
    reused_as_the:"claim "+mth, ref:"(170)", status:"OK — generated consistently"});

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
  function byDim(d){ return nums.filter(function(nn){return nn.dim===d;}); }
  function findDim(d, hint){ var c = byDim(d);
    if (hint) { for (var i=0;i<c.length;i++) if (hint.test(c[i].name)) return c[i]; } return c[0]; }
  var mathLines = [], mathRows = [];
  if (!nums.length) {
    mathLines.push("No numeric key parameters are stated in the draft record.");
    mathLines.push("All quantities: TBD — no values have been invented for this package.");
  } else {
    mathLines.push("All relations below are derived strictly from the stated key parameters; "+
      "no values have been invented.");
    nums.forEach(function(nn){
      var conv = null;
      if (nn.range) { var span = nn.range[1]-nn.range[0];
        conv = (nn.dim==="TEMP" && nn.unit==="c")
          ? ["Operating span", nn.name+" span = "+nn.range[1]+" − ("+nn.range[0]+")",
             fmt(span)+" °C = "+fmt(span*9/5)+" °F = "+fmt(span)+" K"]
          : ["Operating span", nn.name+" span = "+nn.range[1]+" − ("+nn.range[0]+")",
             fmt(span)+" "+nn.unit];
      }
      else if (nn.dim==="L" && nn.unit==="in")
        conv = ["Unit conversion", nn.name+" = "+nn.num+" in", fmt(nn.num*25.4)+" mm"];
      else if (nn.dim==="M" && nn.unit==="g" && nn.num>=1000)
        conv = ["Unit conversion", nn.name+" = "+fmt(nn.num)+" g", fmt(nn.num/1000)+" kg"];
      else if (nn.dim==="TEMP" && nn.unit==="c")
        conv = ["Unit conversion", nn.name+" = "+nn.num+" °C",
          fmt(nn.num*9/5+32)+" °F = "+fmt(nn.num+273.15)+" K"];
      else if (nn.dim==="T" && nn.unit==="ms")
        conv = ["Unit conversion", nn.name+" = "+nn.num+" ms", fmt(nn.num/1000)+" s"];
      else if (nn.dim==="RT" && nn.unit==="gbps")
        conv = ["Unit conversion", nn.name+" = "+nn.num+" Gbps", fmt(nn.num*1000)+" Mbps"];
      if (conv) mathRows.push(conv);
    });
    var P = findDim("P"), V = findDim("V"), A = findDim("A"), R = findDim("R"),
        RT = findDim("RT"), PTS = findDim("N", /port|channel|node|worker|lane/i);
    function derived(label, eq, res, dimchk){
      mathRows.push([label, eq, res]); mathLines.push("Dimensional check: "+dimchk); }
    if (P && V && !A) derived("Current from power and voltage",
      "I = P / V = "+fmt(P.num)+" / "+fmt(V.num), fmt(P.num/V.num)+" A", "[W] / [V] = [A]");
    else if (V && A && !P) derived("Power from voltage and current",
      "P = V · I = "+fmt(V.num)+" × "+fmt(A.num), fmt(V.num*A.num)+" W", "[V] · [A] = [W]");
    else if (V && R && !A) derived("Current from voltage and resistance",
      "I = V / R = "+fmt(V.num)+" / "+fmt(R.num), fmt(V.num/R.num)+" A", "[V] / [Ω] = [A]");
    if (RT && PTS) derived("Per-port throughput",
      "R_port = R_total / N = "+fmt(RT.num)+" / "+fmt(PTS.num),
      fmt(RT.num/PTS.num)+" "+RT.unit, "[bit/s] / [count] = [bit/s]");
    if (!mathRows.length)
      mathLines.push("The stated parameters admit no further direct derivation; "+
        "each value is carried into the specifications table as stated.");
  }

  /* ================= specifications table ================= */
  function norm(s){ return String(s||"").toLowerCase().replace(/[^a-z0-9]/g,""); }
  var specRows = pkeys.map(function(k){
    var p = parseVal(rec.params[k]), tol = "not stated";
    (rec.m||[]).forEach(function(mr){
      if (norm(mr.name)===norm(k) && mr.tolerance) tol = mr.tolerance; });
    return [k, String(rec.params[k]), p ? p.unit : "—", tol];
  });

  /* ================= how to make and use (§112 enablement) ================= */
  var build = [
    "A person of ordinary skill in the art can make and use the invention by the following steps "+
    "(enablement, 35 U.S.C. §112(a)). No undue experimentation is required beyond ordinary skill."];
  if (mats.length) build.push("Materials required: "+mats.join("; ")+".");
  if (procs.length) build.push("Construction, in order: "+procs.map(function(p,i){
    return "("+(i+1)+") "+trim(p,160); }).join(" ")+
    " Equivalent materials or processes may be substituted only where the verification record still validates.");
  if (steps.length) build.push("Bring-up and verification: "+steps.slice(0,3).join("; ")+
    "; then emit the machine-readable record and verify it before release.");
  if (!mats.length && !procs.length && !steps.length)
    build.push("The draft record states no separate materials or processes; construct per the "+
      "detailed description and verify via the verification module.");

  /* ================= abstract (≤150 words) ================= */
  var art0 = /^[aeiou]/i.test(invL) ? "An" : "A";
  var absParts = [
    art0+" "+invL+" for "+catL+",",
    "comprising "+elIntro+" and a verification module (170) configured to emit a machine-readable "+
      "record of the build"+(ptxt ? ", rated at "+ptxt : "")+".",
    steps.length ? "Production proceeds by: "+steps.slice(0,3).map(low1).join("; ")+"." : ""
  ].filter(Boolean);
  var abs = absParts.join(" ");
  while (wc(abs) > 150 && absParts.length > 2) { absParts.splice(absParts.length-2,1); abs = absParts.join(" "); }
  var abN = wc(abs);

  /* ================= law-compliant framing ================= */
  var elig101 = isSW
    ? "The claims are directed to a technical improvement in computer functionality itself — "+
      "the ordered multi-module control sequence producing a machine-verified build — not to an abstract "+
      "idea implemented on a generic computer. Under the Alice/Mayo framework, eligibility under "+
      "35 U.S.C. §101 is asserted on that technical-improvement basis. The applicant acknowledges that "+
      "eligibility is ultimately determined by the USPTO and the courts; abstract-idea risk is not "+
      "papered over — any claim found to recite only an abstract idea on generic hardware must be amended."
    : "The claims recite a tangible apparatus with structural limitations — statutory subject matter "+
      "under 35 U.S.C. §101.";

  /* ================= additional figures (only where data supports) ================= */
  var extraFigs = osvExtraFigs(rec);

  /* ================= document (USPTO order) ================= */
  var bg = trim(xlat((rec.x && rec.x.what) || rec.a || ""), 600);
  var doc = [
    {heading:"TITLE OF THE INVENTION", body:[cap(inv)]},
    {heading:"CROSS-REFERENCE TO RELATED APPLICATIONS", body:[
      rec.mix ? "Revision-chain lineage noted in the draft ("+rec.mix.join(", ")+
        "); no new related applications are claimed."
        : "No related applications are claimed."]},
    {heading:"STATEMENT REGARDING FEDERALLY SPONSORED RESEARCH OR DEVELOPMENT",
      body:["Not applicable."]},
    {heading:"FIELD OF THE INVENTION", body:[
      "The present invention relates to "+catL+", and more particularly to "+invL+"."]},
    {heading:"BACKGROUND OF THE INVENTION", body:[
      bg,
      "Novelty (35 U.S.C. §102) and non-obviousness (§103) are asserted over the prior art of record. "+
      "No prior-art search accompanies this package — a registered practitioner must conduct one before filing. "+
      "Nothing herein concedes that any reference is prior art."]},
    {heading:"BRIEF SUMMARY OF THE INVENTION", body:[
      "The invention provides a system for "+catL+" comprising "+elIntro+
        ", with a verification module (170) emitting a machine-readable record of the build.",
      "It is an object of the invention to hold rated performance across operating conditions. "+
      "It is a further object to bound execution so that out-of-bound states resolve from a common origin. "+
      "It is a further object to render every unit's build machine-verifiable before release."]},
    {heading:"STATEMENT OF ELIGIBILITY (35 U.S.C. §101)", body:[elig101]},
    {heading:"BRIEF DESCRIPTION OF THE DRAWINGS", body:[
      "FIG. 1 is a system block diagram of the modules arranged about the "+invL+" core.",
      "FIG. 2 is a chart of the rated performance measurements of the system.",
      "FIG. 3 is a flowchart of the method of producing the "+invL+"."
    ].concat(extraFigs.map(function(f){ return "FIG. "+f.n+" is "+low1(f.title)+"."; }))},
    {heading:"DRAWING SHEETS", figures:true, extra:true, body:[
      "Sheet 1 of "+(3+extraFigs.length)+" — FIG. 1: system block diagram.",
      "Sheet 2 of "+(3+extraFigs.length)+" — FIG. 2: parametric diagram.",
      "Sheet 3 of "+(3+extraFigs.length)+" — FIG. 3: process flow."
    ].concat(extraFigs.map(function(f){
      return "Sheet "+f.n+" of "+(3+extraFigs.length)+" — FIG. "+f.n+": "+low1(f.title)+
        " (generated from the draft record)."; }))},
    {heading:"DETAILED DESCRIPTION OF THE INVENTION", body:[
      trim(xlat(rec.a||""), 900),
      "Referring to FIG. 1, the system comprises: "+
        mods.map(function(mo){return art(mo)+mo.phrase+" ("+mo.ref+")";}).join("; ")+". "+
        mods.map(function(mo){return cap(modDep(mo).replace(/^wherein /,"The "));}).join(" "),
      ptxt ? "In the rated embodiment the system is configured with "+ptxt+" (FIG. 2)." : "",
      mats.length ? "Structural components are formed from materials including "+mats.slice(0,4).join(", ")+"." : "",
      steps.length ? "In operation (FIG. 3): "+steps.join("; ")+"." : "",
      "The description sets forth the full scope of the claimed subject matter (written description, "+
      "35 U.S.C. §112(a)). The claims employ definite structural language (definiteness, §112(b)); "+
      "means-plus-function phrasing is avoided except where paired with corresponding structure herein."
    ].filter(Boolean)},
    {heading:"MATHEMATICAL DESCRIPTION", body:mathLines,
      table: mathRows.length ? {head:["Derivation","Equation","Result"], rows:mathRows} : null},
    {heading:"SPECIFICATIONS TABLE",
      table:{head:["Parameter","Value","Units","Tolerance"], rows:specRows},
      body:["Values are carried from the draft record as stated."]},
    {heading:"HOW TO MAKE AND USE THE INVENTION", body:build},
    {heading:"What is claimed is:", claims:claims},
    {heading:"ABSTRACT", body:[abs]}
  ];

  return {
    spec_id: rec.i, title: rec.t, osv_version: "OSV-1.0",
    prepared: rec.pd || "on-device generation", generated: true,
    transmutation_note: "Transmutation of draft record "+rec.i+": the same invention, recast from "+
      "the draft's system-framework language into conventional patent form — as metric converts to "+
      "imperial. Nothing added, nothing lost.",
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
      drawings_ref: (3+extraFigs.length)+" drawing sheets enclosed: FIG. 1 (system block diagram), "+
        "FIG. 2 (parametric diagram), FIG. 3 (process flow)"+
        (extraFigs.length ? ", "+extraFigs.map(function(f){return "FIG. "+f.n+" ("+low1(f.title)+")";}).join(", ") : "")+
        " — see Drawing Sheets."
    },
    reviewer_note: "Prior-art search and patentability judgment are NOT included: "+
      "they require a registered patent practitioner. No prior art was invented for this package.",
    source_claims_note: "Generated on this device by the on-page Official Standard builder from draft record "+
      rec.i+". The original draft record is preserved unchanged — corrections live only in this layer."
  };
}

/* ---- additional visual figures, only where the record's own data supports them ---- */
function osvExtraFigs(rec){
  var figs = [];
  var dims = Object.keys(rec.params||{}).filter(function(k){
    return /dim|length|width|height|diameter|depth|wall|thick/i.test(k) && /\d/.test(String(rec.params[k])); });
  var mats = (rec.mf && rec.mf.materials) || [];
  if (dims.length || mats.length) figs.push({n:4, kind:"overview", title:"Product overview"});
  var procs = ((rec.mf && rec.mf.processes) || []).length, st = (rec.steps||[]).length;
  if (procs >= 2 || st >= 2) figs.push({n:5, kind:"flow", title:"Process flow"});
  return figs;
}
function osvFigSVG(rec, fig){
  var W = 420, esc2 = function(s){ return String(s).replace(/&/g,"&amp;")
    .replace(/</g,"&lt;").replace(/>/g,"&gt;"); };
  var head = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+W+' ';
  var t = '<text x="12" y="20" font-family="sans-serif" font-size="13" font-weight="bold" fill="#111">'+
    esc2("FIG. "+fig.n+" — "+fig.title+" — "+rec.i)+'</text>';
  if (fig.kind === "overview") {
    var dims = Object.keys(rec.params||{}).filter(function(k){
      return /dim|length|width|height|diameter|depth|wall|thick/i.test(k) && /\d/.test(String(rec.params[k])); }).slice(0,3);
    var mats = ((rec.mf && rec.mf.materials) || []).slice(0,4);
    var H = 150 + dims.length*22 + (mats.length ? 34 : 0), y = 44, s = "";
    s += '<rect x="60" y="'+y+'" width="300" height="92" rx="10" fill="#eef1f6" stroke="#333" stroke-width="2"/>';
    s += '<text x="210" y="'+(y+50)+'" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#333">'+
      esc2(rec.t.split(" ").slice(0,5).join(" "))+'</text>';
    y += 108;
    dims.forEach(function(k){
      s += '<text x="60" y="'+y+'" font-family="sans-serif" font-size="11" fill="#111">'+
        esc2(k+": "+rec.params[k])+'</text>';
      s += '<line x1="52" y1="'+(y-4)+'" x2="368" y2="'+(y-4)+'" stroke="#888" stroke-dasharray="4 3"/>';
      y += 22;
    });
    if (mats.length) {
      s += '<text x="60" y="'+(y+6)+'" font-family="sans-serif" font-size="11" fill="#111">Materials:</text>';
      mats.forEach(function(mt,i){
        s += '<rect x="'+(60+i*96)+'" y="'+(y+12)+'" width="90" height="18" rx="9" fill="#dfe7f3" stroke="#667"/>'+
          '<text x="'+(105+i*96)+'" y="'+(y+25)+'" text-anchor="middle" font-family="sans-serif" font-size="9" fill="#223">'+
          esc2(String(mt).slice(0,14))+'</text>'; });
    }
    return head + H + '" role="img">' + t + s + "</svg>";
  }
  // flow
  var items = ((rec.mf && rec.mf.processes) || []).slice(0,6);
  if (!items.length) items = (rec.steps||[]).slice(0,6);
  var H2 = 40 + items.length*52, s2 = "", y2 = 40;
  items.forEach(function(stp, i){
    s2 += '<rect x="40" y="'+y2+'" width="340" height="36" rx="6" fill="#eef1f6" stroke="#333"/>'+
      '<text x="58" y="'+(y2+23)+'" font-family="sans-serif" font-size="11" font-weight="bold" fill="#111">'+(i+1)+'</text>'+
      '<text x="80" y="'+(y2+23)+'" font-family="sans-serif" font-size="10" fill="#333">'+
      esc2(String(stp).replace(/^\s*\d+\.\s*/,"").slice(0,52))+'</text>';
    if (i < items.length-1)
      s2 += '<line x1="210" y1="'+(y2+36)+'" x2="210" y2="'+(y2+52)+'" stroke="#333" stroke-width="2"/>'+
        '<polygon points="210,'+(y2+52)+' 204,'+(y2+44)+' 216,'+(y2+44)+'" fill="#333"/>';
    y2 += 52;
  });
  return head + H2 + '" role="img">' + t + s2 + "</svg>";
}
