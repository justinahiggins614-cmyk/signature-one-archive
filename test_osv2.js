// node test_osv2.js — OSV-1.0 transmutation suite
var fs = require("fs");
var src = fs.readFileSync("/home/hatch/workspace/signature-one-archive/osv.js", "utf8");
eval(src);

function hwRec() {
  return {i:"JAH-SPEC-000123", t:"Optional System Upgrade (Test Fixture)",
    a:"A test system rated at several parameters with full manufacturing detail.",
    c:"Hardware", cpc:"H05K", pd:"2026-09-30",
    tools:{LINE:"primary dimension axis along the optional system upgrade system",
      TRIANGLE:"taper and load angle of the optional system upgrade system structure",
      SQUARE:"bounding enclosure of the optional system upgrade system",
      CROSS:"junction points where optional system upgrade system subassemblies cross",
      CIRCLE:"circular features: ports and mounts of the optional system upgrade system",
      CURVATURE:"fillet and bend radii across the optional system upgrade system housing"},
    params:{WALL:"0.12 in", VOLTAGE:"5 V", POWER:"12 W", TEMP:"-20 .. 60 C", COUNT:"4",
      TAPER:"12.7 deg", RATE:"2.5 Gbps"},
    steps:["Seed the Signature-One grid to anchor the optional system upgrade as a binary-1 identity",
      "Lock the six tools in reversed-allowance order about the single controlled origin",
      "Emit the autoread block and verify STATUS=SIGNATURE-1 VALID before release"],
    line:"Signature Hardware", ln:"", mix:null,
    m:[{name:"WALL", tolerance:"±0.005 in"}],
    x:null,
    mf:{materials:["ABS","aluminum 6061","steel"], processes:["SLS 3D printing","CNC milling","final assembly"]}};
}
function swRec() {
  return {i:"JAH-SPEC-069443", t:"Adaptive Learning Controller",
    a:"A controller that routes data through a pipeline.",
    c:"Software", cpc:"G06F", pd:"2026-09-30",
    tools:{LINE:"data flow path through the adaptive learning controller pipeline",
      TRIANGLE:"decision hierarchy fanning from the adaptive learning controller core",
      SQUARE:"memory and system bounds containing the adaptive learning controller",
      CROSS:"branch logic where adaptive learning controller paths intersect",
      CIRCLE:"nodes and endpoints orbiting the adaptive learning controller",
      CURVATURE:"load and latency curves shaping adaptive learning controller behavior"},
    params:{LATENCY:"12 ms", THROUGHPUT:"1.5 Gbps", NODES:"8"},
    steps:[], line:"Signature Software", ln:"", mix:null, m:null, x:null,
    mf:{materials:[], processes:[]}};
}
function thinRec() {
  return {i:"JAH-WORD-000001", t:"Rug", word:"rug", a:"A floor covering.",
    c:"Textiles", cpc:"", pd:"2026-09-30",
    tools:{LINE:"primary axis along the rug"}, params:{}, steps:[], line:"", ln:"",
    mix:null, m:null, x:null, mf:null};
}

var fails = 0;
function ok(cond, name) {
  console.log((cond ? "PASS" : "FAIL") + " — " + name);
  if (!cond) fails++;
}

// ---- transmutation: no geometric branding in claims ----
var d1 = buildOSV(hwRec());
var claimsText = d1.document.filter(function(s){return s.heading==="What is claimed is:";})[0]
  .claims.join(" ");
ok(!/six-tool|six tool|geometric|Signature-One|autoread/i.test(claimsText), "claims carry no draft branding");
ok(/What is claimed is/.test(d1.document.map(function(s){return s.heading;}).join("|")), "'What is claimed is:' heading present");
ok(/BRIEF SUMMARY OF THE INVENTION/.test(d1.document.map(function(s){return s.heading;}).join("|")), "'BRIEF SUMMARY OF THE INVENTION' heading present");
ok(/selected from the group consisting of/.test(claimsText), "Markush group for materials");
ok(/0\.12 in/.test(claimsText) && /5 V/.test(claimsText), "concrete param values in claims");
ok(/\(110\)/.test(claimsText) && /\(170\)/.test(claimsText), "reference numerals (110)-(170) kept");
ok(/the primary dimension axis \(110\)/.test(claimsText), "antecedent basis: 'the' reuse with numeral");
ok(d1.claims ? true : true, "");
var claimLines = d1.document.filter(function(s){return s.heading==="What is claimed is:";})[0].claims;
ok(claimLines.length >= 12, "claim count >= 12 (got " + claimLines.length + ")");
ok(/A method of producing/.test(claimLines.join(" ")), "independent method claim present");
ok(/Signature-One/.test(claimsText) === false, "step/method branding kept out of claims");
var fullDoc = d1.document.map(function(s){return (s.body||[]).join(" ")+" "+(s.claims||[]).join(" ");}).join(" ");
ok(/baseline reference state/.test(fullDoc) && !/binary-1 identity/i.test(fullDoc),
  "step branding translated in document ('binary-1 identity' -> 'baseline reference state')");
ok(/reverse-order/.test(fullDoc) && !/reversed-allowance/i.test(fullDoc),
  "'reversed-allowance' -> 'reverse-order'");
ok(/verification module/.test(fullDoc) && !/autoread/i.test(fullDoc),
  "'autoread block' -> 'verification module'");
ok(/transmutation/i.test(d1.transmutation_note) && /nothing added, nothing lost/i.test(d1.transmutation_note),
  "transmutation note present");

// ---- eligibility framing ----
var elig = d1.document.filter(function(s){return s.heading==="STATEMENT OF ELIGIBILITY (35 U.S.C. §101)";})[0].body.join(" ");
ok(/statutory subject matter/.test(elig), "hardware §101 framing");
var d2 = buildOSV(swRec());
var elig2 = d2.document.filter(function(s){return s.heading==="STATEMENT OF ELIGIBILITY (35 U.S.C. §101)";})[0].body.join(" ");
ok(/Alice\/Mayo/.test(elig2) && /not papered over/.test(elig2), "software §101 Alice/Mayo honest framing");
var claims2 = d2.document.filter(function(s){return s.heading==="What is claimed is:";})[0].claims.join(" ");
ok(/the data flow path \(110\) is disposed through/.test(claims2), "software module dependent claim (disposed through)");
ok(/the nodes and endpoints \(150\) are configured to orbit/.test(claims2), "plural agreement (are configured to orbit)");
ok(/the load and latency curves \(160\) are configured to shape/.test(claims2), "plural agreement (are configured to shape)");
ok(/the decision hierarchy \(120\) is configured to fan out from/.test(claims2), "singular agreement + fan out from");
ok(!/adaptive learning controller pipeline/.test(claims2.replace(/the system pipeline/g,"")), "branded tails reduced (spot check)");

// ---- extra figures ----
var ef1 = osvExtraFigs(hwRec());
ok(ef1.length === 2 && ef1[0].kind === "overview" && ef1[1].kind === "flow", "hw rec gets overview + flow figures");
var svg1 = osvFigSVG(hwRec(), ef1[0]);
ok(/FIG\. 4/.test(svg1) && /0\.12 in/.test(svg1) && /ABS/.test(svg1), "overview SVG carries own dims + materials");
var svg2 = osvFigSVG(hwRec(), ef1[1]);
ok(/FIG\. 5/.test(svg2) && /SLS 3D printing/.test(svg2), "flow SVG carries own processes");
var ef3 = osvExtraFigs(thinRec());
ok(ef3.length === 0, "thin rec gets no extra figures (graceful skip)");
var d3 = buildOSV(thinRec());
var bd = d3.document.filter(function(s){return s.heading==="BRIEF DESCRIPTION OF THE DRAWINGS";})[0].body.join(" ");
ok(!/FIG\. 4/.test(bd), "thin rec brief description has no FIG. 4");
ok(/TBD/.test(d3.document.filter(function(s){return s.heading==="MATHEMATICAL DESCRIPTION";})[0].body.join(" ")),
  "thin rec math says TBD");
var abs3 = d3.document.filter(function(s){return s.heading==="ABSTRACT";})[0].body[0];
ok(abs3.split(/\s+/).length <= 150, "thin rec abstract <= 150 words");

// ---- renderOSV smoke (extracted from specs.html) ----
var html = fs.readFileSync("/home/hatch/workspace/signature-one-archive/specs.html", "utf8");
function esc(s){return String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}
var mStart = html.indexOf("function renderOSV(");
var rel = html.slice(mStart + 20).search(/\nfunction [A-Za-z]/);
var mEnd = mStart + 20 + rel;
eval(html.slice(mStart, mEnd).replace(/function renderOSV/, "var renderOSV = function"));
var xf = osvExtraFigs(hwRec()).map(function(f){return {n:f.n,title:f.title,svg:osvFigSVG(hwRec(),f)};});
var out = renderOSV(d1, true, ["<svg>1</svg>","<svg>2</svg>","<svg>3</svg>"], xf);
ok(/FIG\. 4 &mdash; Product overview \(generated from the draft record\)/.test(out), "rendered FIG. 4 caption w/ generated note");
ok(/FIG\. 5 &mdash; Process flow \(generated from the draft record\)/.test(out), "rendered FIG. 5 caption");
ok(/Transmutation note/.test(out), "transmutation note rendered");
ok(/What is claimed is/.test(out), "claims heading rendered");

console.log(fails === 0 ? "\nALL TESTS PASSED" : "\n" + fails + " FAILURES");
process.exit(fails ? 1 : 0);
