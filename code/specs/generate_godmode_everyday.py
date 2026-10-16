#!/usr/bin/env python3
"""Author the "god mode engineering" everyday-object specs as JAH-SPEC drafts.

Source: the user's five-layer Algorithmic Object Generation Engine for everyday
objects (ergonomic constraints, material science, parametric CAD, manufacturing
toolpaths, supply chain/packaging). His order: "That last one just solve and
put in specks."

Writes 6 specs (IDs 908996-909001): one flagship solved Ultimate Ergonomic
Travel Cup, plus one per master-matrix category (kitchenware, ergonomic
chairs, hand tools, storage containers, desktop organizers). Each spec is a
full filing-ready draft package in the repo's standard schema: identity,
five-layer specification with parametric tables, manufacturing instructions,
packaging spec, and a claims-style enumeration of novel features.

Original Signature work (his pipeline concept); never reworded copies of
others' patents. Status: Draft - ready to file; NOT filed, NOT granted.
"""
import gzip
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import autoread as ja

REPO = os.path.dirname(os.path.dirname(HERE))
HOT = os.path.join(REPO, "data", "specs.jsonl")
STATE = os.path.join(REPO, "code", "specs", "state.json")

INVENTOR = "Justin Addam Higgins"
STATUS = "Draft \u2014 ready to file"
PREPARED = "2026-10-15"
CATEGORY = "Industrial Engineering"
CPC = "G06F"
ERA = "Current"

FIRST_ID = 908996
COUNT = 6

TOOLMAP = {
    "LINE": "line-path module (110): governs parametric spline definitions and toolpath vectors",
    "TRIANGLE": "triangle hierarchy unit (120): governs the five-layer generation hierarchy",
    "SQUARE": "square bound frame (130): bounds tolerance envelopes and dimensional frames",
    "CROSS": "cross decision branch (140): decides material and process selection at each branch",
    "CIRCLE": "circle node anchor (150): anchors the single solvable origin datum",
    "CURVATURE": "curvature flow shaper (160): shapes ergonomic curves, fluid paths, and fillet radii",
}

PIPELINE_STEPS = [
    "Layer 1 - Ontological & Ergonomic Constraints: capture human grip forces, contact angles, center of mass, fluid dynamics, and intended daily wear cycles as solvable numeric targets.",
    "Layer 2 - Material Science & Rheology: select molecular structure, thermal behavior, safety certifications, and surface micro-metrics that satisfy Layer 1 targets.",
    "Layer 3 - Parametric CAD & Geometry: express every surface as mathematical spline definitions with wall-thickness gradients, draft angles, and fillet radii.",
    "Layer 4 - Manufacturing Toolpaths (CAM): emit injection-mold tooling specs, CNC multi-axis milling G-code, or 3D-printer slicing layers directly from Layer 3 geometry.",
    "Layer 5 - Supply Chain & Packaging: solve nesting geometry for shipping density, custom die-cut box layouts, and retail label placement from the finished dimensions.",
]


def filing_obj(spec_id, title):
    return {
        "form": "utility",
        "status": "Draft \u2014 ready to file. NOT filed with the USPTO. NOT a granted patent.",
        "inventor": INVENTOR,
        "applicant": INVENTOR,
        "title": title,
        "spec_id": spec_id,
        "declaration": "Declaration under 37 CFR 1.63 to be completed by the inventor before filing.",
        "correspondence": "TBD by inventor",
        "reviewer_note": ("Prior-art search and patentability judgment are NOT included: they require "
                          "a registered patent practitioner. No prior art was invented for this package."),
    }


def workfile_obj(spec_id):
    return {
        "spec_id": spec_id,
        "prior_art_search": "NOT STARTED - examination decides patentability, not generation.",
        "honesty": ("All parameters are design targets of this draft, not measured production results. "
                    "Examples are illustrative, not test data."),
        "governance": "JAH governance leaking its own files - deterministic ID coding is the protection.",
    }


def technical_obj(spec_id, title, c):
    return {
        "identity": {
            "invention_id": spec_id, "version": "1.0", "revision": 0,
            "created": PREPARED, "modified": PREPARED,
            "inventor": INVENTOR, "applicant": INVENTOR, "assignee": None,
            "title": title, "field": CATEGORY, "cpc": CPC,
            "patent_type": "utility",
            "signature_line": "Signature-One Core",
            "catalog": f"signature-one-archive/specs.html#{spec_id}",
            "origin_concept": ("The user's five-layer Algorithmic Object Generation Engine "
                               "('god mode engineering'): an everyday object is treated as the output "
                               "of an exhaustive, multi-variable manufacturing pipeline, solved across "
                               "five parallel layers from a single origin."),
        },
        "overview": {
            "one_sentence": c["one_sentence"],
            "plain_english": c["plain_english"],
            "problem": ("Conventional product design leaves ergonomics, material choice, geometry, "
                        "toolpaths, and packaging to separate teams and ad-hoc late decisions; the "
                        "object that ships is a compromise, not a solution."),
            "purpose": ("Collapse the entire everyday object - from raw chemical composition to retail "
                        "box - into one solvable, parametric, machine-verifiable specification generated "
                        "in a single pass."),
            "primary_function": c["primary_function"],
            "intended_users": "Product designers, manufacturers, and builders who want a buildable specification instead of a sketch.",
            "advantages": ("single re-derivable origin; every number traceable to a layer; buildable "
                           "output (CAD, CAM, packaging) from one run; per-unit machine-readable verification"),
            "best_mode": "full five-layer embodiment with autoread verification before release",
        },
        "background": {"text": c["background"]},
        "summary": {"text": c["summary"]},
        "definitions": c["definitions"],
        "architecture": {
            "layers": PIPELINE_STEPS,
            "note": ("The five layers run in parallel from one origin datum: each layer consumes the "
                     "previous layer's solved parameters as hard constraints, so nothing is decided twice."),
        },
        "components": c["components"],
        "method": {
            "inputs": ["Object class prompt (e.g. 'ergonomic travel cup')", "Target user percentile range",
                       "Regulatory/safety target list", "Production volume band"],
            "steps": PIPELINE_STEPS,
            "output": ["Complete parametric specification", "CAM toolpaths", "Packaging die layout", "Claims enumeration"],
        },
        "data": {"parametric_table": c["parametric_table"]},
        "math": {"origin": "Signature-One origin datum (circle node anchor 150)",
                 "formulas": c["formulas"]},
        "drawings": {
            "numerals": {
                "110": "line-path module - spline definitions, toolpath vectors",
                "120": "triangle hierarchy unit - five-layer generation hierarchy",
                "130": "square bound frame - tolerance envelopes, dimensional frames",
                "140": "cross decision branch - material/process selection branches",
                "150": "circle node anchor - single solvable origin datum",
                "160": "curvature flow shaper - ergonomic curves, fluid paths, fillets",
            },
            "figures": c["figures"],
        },
        "embodiments": c["embodiments"],
        "examples": [{"scenario": c["example_scenario"]}],
        "examples_note": "Examples are illustrative design targets, not measured production results.",
        "performance": {"targets": c["performance"]},
        "manufacturing": {
            "materials": c["materials"],
            "processes": c["processes"],
            "steps": c["manufacture_steps"],
        },
        "operation": {"use": c["operation"]},
        "security": {"note": "No networked component; no data collection. Physical product only."},
        "claims": c["claims"],
    }


def make_record(idx, c):
    spec_id = f"JAH-SPEC-{idx:06d}"
    title = c["title"]
    params = {k: v for k, v in c["parametric_table"].items()}
    return {
        "spec_id": spec_id,
        "title": title,
        "abstract": c["abstract"],
        "category": CATEGORY,
        "cpc": CPC,
        "era": ERA,
        "prepared_date": PREPARED,
        "inventor": INVENTOR,
        "owner": INVENTOR,
        "status": STATUS,
        "line": "Signature-One Core",
        "line_note": "",
        "signature_tool_mapping": TOOLMAP,
        "key_parameters": params,
        "autoread_block": ja.make_autoread(spec_id, title, CATEGORY, CPC, ERA, params,
                                           object_phrase=c.get("object_phrase", "everyday object")),
        "algorithm_steps": PIPELINE_STEPS,
        "patent_draft": {
            "objects": {
                "technical": technical_obj(spec_id, title, c),
                "filing": filing_obj(spec_id, title),
                "workfile": workfile_obj(spec_id),
            },
        },
        "manufacture": {
            "note": ("Means of manufacture for the invention. Follow in order; substitute equivalent "
                     "materials or processes only where the autoread block still validates."),
            "materials": c["materials"],
            "processes": c["processes"],
            "steps": c["manufacture_steps"],
        },
        "demo": {
            "kind": "simulator",
            "blurb": c["demo_blurb"],
            "params": c["demo_params"],
            "outputs": c["demo_outputs"],
            "note": "Interactive working demo. Figures are simulated estimates for demonstration, not measured results.",
        },
        "measurements": c["measurements"],
        "ai_explainer": {
            "headline": f"AI explainer: {title}",
            "what": c["plain_english"],
            "how_it_works": PIPELINE_STEPS,
            "who_its_for": "Builders, manufacturers, and product teams who want a documented, repeatable way to make an everyday object.",
            "bottom_line": ("This invention treats an everyday object as the solved output of a "
                            "five-layer pipeline: ergonomics, materials, CAD, toolpaths, packaging - "
                            "nothing arbitrary, everything buildable."),
        },
    }


# ----------------------------------------------------------------------------
# Spec content: flagship travel cup
# ----------------------------------------------------------------------------
CUP = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to the Ultimate Ergonomic Travel Cup",
    "object_phrase": "travel cup",
    "one_sentence": "A ceramic-lined steel travel cup whose grip, rim, balance, materials, toolpaths, and packaging are all solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("This is a travel cup designed the god-mode way: instead of sketching a cup and "
                      "hoping it feels right, the engine solves the hand, the lip, the balance, the steel, "
                      "the factory steps, and the shipping box as one connected calculation - then hands "
                      "you a specification you can actually manufacture."),
    "primary_function": "Hold 500 ml of hot or cold beverage, seal leak-proof, pour without dribbling, and survive daily carry for years.",
    "background": ("Travel cups are designed by styling first and engineering second: grip diameters "
                   "are chosen by eye, rims dribble, lids leak under steam pressure, vacuum gaps fail "
                   "at the weld, and packaging ships mostly air. Each failure is a layer that was never "
                   "solved. The five-layer engine inverts this: Layer 1 fixes the human interface as "
                   "numbers (grip 72 mm tapering to 65 mm for 5th-95th percentile hands; 15-degree rim "
                   "flare for laminar detachment; center of gravity 45 mm above base at 3.2:1 "
                   "height-to-width so it cannot tip in a cup holder). Layer 2 then selects materials "
                   "that satisfy those numbers (AISI 304 electropolished to Ra <= 0.4 um; dual-wall "
                   "vacuum at 1e-5 Torr holding heat loss under 2 C/hour; powder-coat grip at "
                   "mu = 0.65). Layers 3-5 derive CAD, CAM, and packaging deterministically from the "
                   "solved parameters. The cup below is the engine's solved output - a complete, "
                   "buildable specification, not a concept."),
    "summary": ("A double-wall vacuum-insulated travel cup, 500 ml, with a 72-to-65 mm tapered grip, "
                "15-degree flared rim, and a half-turn dual-start Acme lid sealed by a 30-durometer "
                "silicone O-ring at 25% crush. Manufactured by 5-stage progressive deep drawing, "
                "1.2 kW fiber-laser rim weld, and 2500 RPM lathe lip trim; packed in an E-flute sleeve "
                "with die-cut anchor wings, nesting at 12 mm base recess."),
    "definitions": {
        "God-mode generation": "solving an object across all five layers in one pass from a single origin, leaving no parameter to styling alone.",
        "Laminar detachment": "liquid leaving the rim as a clean sheet without running down the outer wall.",
        "Crush tolerance": "the percentage an O-ring compresses at full seal; 25% here.",
        "Nesting offset": "the base recess depth allowing stacked cups to interlock in shipping.",
    },
    "components": [
        "Inner vessel: AISI 304 stainless, electropolished Ra <= 0.4 um",
        "Outer shell: AISI 304, matte polyester-epoxy powder coat, mu = 0.65",
        "Vacuum core: dual-wall gap evacuated to 1e-5 Torr",
        "Lid: 4.0 mm dual-start Acme thread, half-turn seal",
        "Gasket: 30-durometer food-grade silicone O-ring, 25% crush",
        "Base recess: 12 mm nesting offset",
    ],
    "parametric_table": {
        "grip_diameter_top_mm": "72",
        "grip_diameter_base_mm": "65",
        "hand_span_percentile": "5th-95th",
        "rim_flare_deg": "15",
        "center_of_gravity_height_mm": "45",
        "height_to_width_ratio": "3.2:1",
        "capacity_ml": "500",
        "inner_steel": "AISI 304, electropolished Ra <= 0.4 um",
        "vacuum_torr": "1e-5",
        "heat_loss_c_per_h": "< 2",
        "outer_coat": "polyester-epoxy powder coat, mu = 0.65",
        "lid_thread": "4.0 mm dual-start Acme",
        "oring_durometer": "30",
        "oring_crush_pct": "25",
        "draft_angle_deg": "1.5",
        "laser_weld_kw": "1.2",
        "laser_speed_m_per_min": "4.5",
        "lathe_trim_rpm": "2500",
        "nesting_recess_mm": "12",
        "packaging": "E-flute corrugated sleeve, die-cut anchor wings",
    },
    "formulas": [
        "Tip resistance: CG height 45 mm with base radius >= 32.5 mm keeps the tipping angle above 35 degrees.",
        "Heat loss: vacuum 1e-5 Torr suppresses convection; loss < 2 C/hour by conduction through the rim weld only.",
        "Seal: O-ring crush 25% of cross-section at lid torque from half-turn dual-start thread.",
    ],
    "figures": [
        "FIG. 1: side elevation with grip taper 72-65 mm and CG marker at 45 mm.",
        "FIG. 2: rim cross-section showing 15-degree flare and laminar detachment vector.",
        "FIG. 3: exploded view: inner vessel, vacuum gap, outer shell, lid, O-ring.",
    ],
    "embodiments": [
        "500 ml commuter embodiment with cup-holder base.",
        "350 ml compact embodiment with identical layer solutions scaled by volume.",
        "Ceramic-lined variant: inner vessel ceramic-coated for taste neutrality.",
    ],
    "example_scenario": ("A commuter fills the cup with coffee at 92 C, seals with a half-turn, tosses it "
                         "in a bag; four hours later the drink is above 84 C and the bag is dry."),
    "performance": [
        "Heat retention: < 2 C/hour loss from 92 C fill.",
        "Leak: zero weep at 25% O-ring crush under steam pressure.",
        "Drop: survives 1.2 m drop to concrete without vacuum loss (design target).",
        "Dishwasher cycles: 500+ without coat degradation (design target).",
    ],
    "materials": ["AISI 304 stainless steel", "food-grade silicone (30 durometer)",
                  "polyester-epoxy powder coat", "E-flute corrugated cardboard"],
    "processes": ["5-stage progressive deep drawing", "continuous-wave fiber laser welding",
                  "3-axis lathe trimming", "powder coating", "die cutting"],
    "manufacture_steps": [
        "1. Deep-draw outer shell in 5 stages: blank > cup > redraw 1 > redraw 2 > bottom trim.",
        "2. Deep-draw inner vessel; electropolish to Ra <= 0.4 um.",
        "3. Laser-weld rim at 1.2 kW, 4.5 m/min to hermetically seal the vacuum gap.",
        "4. Evacuate core to 1e-5 Torr and seal the evacuation port.",
        "5. Trim lip on 3-axis lathe at 2500 RPM with carbide insert.",
        "6. Powder-coat outer shell to mu = 0.65 matte texture.",
        "7. Mold lid with 4.0 mm dual-start Acme thread; fit 30-durometer O-ring.",
        "8. QA: vacuum check, torque seal test, drop test; stamp the autoread block on the unit.",
    ],
    "operation": "Fill, half-turn lid to seal, drink from the flared rim; hand-wash or dishwasher safe.",
    "claims": [
        "1. A travel cup generated as the solved output of a five-layer pipeline, wherein grip taper (72 mm to 65 mm), rim flare (15 degrees), and center of gravity (45 mm above base) are derived from percentile hand-span data rather than styling.",
        "2. The cup of claim 1 wherein the vacuum core at 1e-5 Torr and electropolished Ra <= 0.4 um inner vessel are selected by the material layer to satisfy the ergonomic layer's heat-retention and hygiene targets.",
        "3. The cup of claim 1 wherein the lid seals with a half-turn dual-start Acme thread compressing a 30-durometer silicone O-ring to 25% crush.",
        "4. The cup of claim 1 manufactured by 5-stage progressive deep drawing followed by 1.2 kW fiber-laser rim welding and 2500 RPM lathe lip trimming, as emitted by the CAM layer.",
        "5. The cup of claim 1 packaged in an E-flute sleeve with die-cut anchor wings, the cups nesting at a 12 mm base recess solved by the packaging layer.",
    ],
    "demo_blurb": "Working simulation of the travel cup: adjust fill temperature and ambient, watch heat loss and seal behavior respond.",
    "demo_params": [
        {"id": "p0", "label": "Fill temperature", "unit": "C", "min": 4, "max": 95, "step": 1, "default": 92},
        {"id": "p1", "label": "Hours carried", "unit": "h", "min": 1, "max": 12, "step": 1, "default": 4},
        {"id": "p2", "label": "O-ring crush", "unit": "%", "min": 10, "max": 35, "step": 1, "default": 25},
    ],
    "demo_outputs": [
        {"label": "Drink temperature (simulated)", "unit": "C", "expr": "p0-1.8*p1"},
        {"label": "Seal margin (simulated)", "unit": "%", "expr": "p2-15"},
        {"label": "Tip angle (simulated)", "unit": "deg", "expr": "38"},
    ],
    "measurements": [
        {"name": "Grip diameter top", "value": "72.0", "unit": "mm", "tolerance": "±0.3"},
        {"name": "Grip diameter base", "value": "65.0", "unit": "mm", "tolerance": "±0.3"},
        {"name": "Overall height", "value": "208.0", "unit": "mm", "tolerance": "±0.5"},
        {"name": "Mass", "value": "340.0", "unit": "g", "tolerance": "±5"},
        {"name": "Capacity", "value": "500", "unit": "ml", "tolerance": ""},
        {"name": "Vacuum level", "value": "1e-5", "unit": "Torr", "tolerance": ""},
    ],
    "abstract": ("A travel cup produced as the solved output of a five-layer Algorithmic Object "
                 "Generation Engine. Layer 1 derives grip taper (72 mm to 65 mm for 5th-95th percentile "
                 "hands), a 15-degree rim flare for laminar liquid detachment, and a 45 mm center of "
                 "gravity at 3.2:1 height-to-width for tip resistance. Layer 2 selects AISI 304 "
                 "electropolished to Ra 0.4 um, a 1e-5 Torr vacuum core holding heat loss under 2 C per "
                 "hour, and a mu 0.65 powder coat. Layer 3 defines a half-turn 4.0 mm dual-start Acme lid "
                 "with a 30-durometer silicone O-ring at 25% crush and 1.5-degree draft angles. Layer 4 "
                 "emits 5-stage deep drawing, 1.2 kW laser rim welding at 4.5 m/min, and 2500 RPM lathe "
                 "trimming. Layer 5 nests cups at a 12 mm base recess in E-flute die-cut sleeves."),
}

# ----------------------------------------------------------------------------
# Spec 2: kitchenware (precision flatware set)
# ----------------------------------------------------------------------------
FLATWARE = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to a Precision Flatware Set",
    "object_phrase": "flatware set",
    "one_sentence": "A spoon, fork, and knife set whose balance point, 58 HRC temper, tine spacing, and mouth-feel curvature are solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("This is a fork, spoon, and knife designed the god-mode way: the balance point in "
                      "your hand, the hardness of the steel, the spacing of the tines, and the curve "
                      "against your lip are all solved as numbers first - then the press, the forge, and "
                      "the box follow from those numbers."),
    "primary_function": "Cut, spear, and convey food with balanced handling, lasting edge, and comfortable mouth contact.",
    "background": ("Flatware is usually styled, then hardened as an afterthought: blades chip, tines "
                   "bend, handles feel dead. The engine solves Layer 1 first: balance point 15 mm ahead "
                   "of the handle midpoint for a neutral feel; blade tempered to 58 HRC for edge "
                   "retention without brittleness; tine spacing 4.2 mm with 0.8 mm tip radius; bowl and "
                   "lip curvature derived from mouth-feel contact pressure. Layer 2 selects 420HC "
                   "stainless at 58 HRC with electropolish to Ra 0.3 um. Layer 3 defines spline bowl "
                   "geometry and 2-degree draft for forging release. Layer 4 emits precision blanking "
                   "press plus drop-forging schedules and vibratory deburring. Layer 5 cards each piece "
                   "in a retail blister sized from the solved silhouette."),
    "summary": ("A three-piece flatware set (spoon, fork, knife) in 420HC stainless at 58 HRC: balance "
                "point 15 mm forward of handle midpoint, 4.2 mm tine spacing, mouth-feel curvature "
                "solved from contact pressure. Blanked and drop-forged, vibratory-deburred, "
                "electropolished to Ra 0.3 um, retail carded in blister packs."),
    "definitions": {
        "Mouth-feel curvature": "bowl and lip radii derived from lip contact pressure targets.",
        "Temper (HRC)": "Rockwell C hardness; 58 HRC balances edge retention and toughness.",
        "Balance point": "the point where the piece rests level on a finger; 15 mm ahead of handle midpoint.",
    },
    "components": [
        "Spoon: 420HC bowl, spline-defined curvature, 58 HRC",
        "Fork: four tines, 4.2 mm spacing, 0.8 mm tip radius",
        "Knife: 58 HRC edge, 18-degree bevel, serration-free",
        "Handles: full-tang, 2-degree forged taper",
    ],
    "parametric_table": {
        "steel": "420HC stainless",
        "hardness_hrc": "58",
        "balance_point_mm_ahead": "15",
        "tine_spacing_mm": "4.2",
        "tine_tip_radius_mm": "0.8",
        "knife_bevel_deg": "18",
        "surface_ra_um": "0.3",
        "forging_draft_deg": "2",
        "spoon_bowl_depth_mm": "12",
        "handle_length_mm": "110",
    },
    "formulas": [
        "Balance: mass distribution solved so the first moment about the grip center is zero at 15 mm ahead of handle midpoint.",
        "Edge: 58 HRC gives ~0.3 mm edge deformation per 10,000 cuts in standardized media (design target).",
    ],
    "figures": [
        "FIG. 1: plan view of all three pieces with balance-point markers.",
        "FIG. 2: spoon bowl cross-section with mouth-feel curvature spline.",
        "FIG. 3: fork tine detail: 4.2 mm spacing, 0.8 mm tip radius.",
    ],
    "embodiments": [
        "Three-piece starter set embodiment.",
        "Full 20-piece service embodiment with identical layer solutions scaled per piece.",
        "Matte-black PVD coated embodiment (same geometry, alternate finish).",
    ],
    "example_scenario": ("A diner picks up the knife: it balances on the finger at the marked point, cuts "
                         "cleanly through a roast, and the spoon bowl fits the lip without pressure points."),
    "performance": [
        "Edge retention: 10,000 standardized cuts before stropping (design target).",
        "Corrosion: 200-hour salt spray without pitting (design target).",
        "Dishwasher cycles: 1,000+ without handle loosening (design target).",
    ],
    "materials": ["420HC stainless steel", "blister PVC/PET", "printed retail card"],
    "processes": ["precision blanking press", "drop forging", "vibratory deburring",
                  "electropolishing", "blister packaging"],
    "manufacture_steps": [
        "1. Blank each piece on a precision blanking press from 420HC coil.",
        "2. Drop-forge to net shape with 2-degree draft; quench and temper to 58 HRC.",
        "3. Grind knife bevel to 18 degrees; form fork tines at 4.2 mm spacing.",
        "4. Vibratory-deburr all edges; electropolish to Ra 0.3 um.",
        "5. Laser-etch size/brand marks; QA balance point and hardness.",
        "6. Card in retail blister packs die-cut to the solved silhouette.",
    ],
    "operation": "Use, wash, dry; strop the knife edge as needed; dishwasher safe.",
    "claims": [
        "1. A flatware set generated by the five-layer pipeline, wherein balance point, 58 HRC temper, tine spacing, and mouth-feel curvature are solved parameters rather than styled choices.",
        "2. The set of claim 1 wherein the CAM layer emits a precision blanking press and drop-forging schedule directly from the Layer 3 spline geometry.",
        "3. The set of claim 1 wherein retail blister cards are die-cut to the solved silhouette of each piece.",
    ],
    "demo_blurb": "Working simulation of the flatware set: adjust hardness and tine spacing, watch edge life and fork stiffness respond.",
    "demo_params": [
        {"id": "p0", "label": "Blade hardness", "unit": "HRC", "min": 52, "max": 62, "step": 1, "default": 58},
        {"id": "p1", "label": "Tine spacing", "unit": "mm", "min": 3.0, "max": 5.5, "step": 0.1, "default": 4.2},
        {"id": "p2", "label": "Daily uses", "unit": "/day", "min": 1, "max": 10, "step": 1, "default": 3},
    ],
    "demo_outputs": [
        {"label": "Edge life (simulated)", "unit": "cuts", "expr": "8000+(p0-52)*600-p2*200"},
        {"label": "Fork stiffness (simulated)", "unit": "N/mm", "expr": "42/(p1/4.2)"},
        {"label": "Balance score (simulated)", "unit": "/10", "expr": "9.2"},
    ],
    "measurements": [
        {"name": "Knife hardness", "value": "58", "unit": "HRC", "tolerance": "±1"},
        {"name": "Tine spacing", "value": "4.2", "unit": "mm", "tolerance": "±0.1"},
        {"name": "Handle length", "value": "110.0", "unit": "mm", "tolerance": "±0.5"},
        {"name": "Spoon bowl depth", "value": "12.0", "unit": "mm", "tolerance": "±0.3"},
        {"name": "Surface roughness", "value": "0.3", "unit": "um", "tolerance": "max"},
        {"name": "Set mass", "value": "210.0", "unit": "g", "tolerance": "±8"},
    ],
    "abstract": ("A flatware set produced as the solved output of the five-layer generation engine. "
                 "Layer 1 fixes balance point 15 mm ahead of handle midpoint, 58 HRC temper, 4.2 mm tine "
                 "spacing with 0.8 mm tip radius, and mouth-feel curvature from contact pressure. Layer 2 "
                 "selects 420HC stainless electropolished to Ra 0.3 um. Layer 3 defines spline bowl geometry "
                 "with 2-degree forging draft. Layer 4 emits precision blanking, drop forging, vibratory "
                 "deburring, and electropolish. Layer 5 cards each piece in blister packs cut to the solved "
                 "silhouette."),
}

# ----------------------------------------------------------------------------
# Spec 3: ergonomic chair
# ----------------------------------------------------------------------------
CHAIR = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to a Workspace Ergonomic Chair",
    "object_phrase": "ergonomic chair",
    "one_sentence": "A workspace chair whose lumbar curve radius, synchro-tilt resistance, and mesh tension are solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("This is an office chair designed the god-mode way: the curve of your lower back, "
                      "the way the seat and backrest move together when you lean, and the tension of the "
                      "mesh are solved as numbers for real bodies first - then the castings, the molds, "
                      "and the flat-pack box follow."),
    "primary_function": "Support seated work for 8+ hours with correct lumbar posture, synchronized tilt, and breathable contact.",
    "background": ("Chairs are styled around a mechanism bought off the shelf; lumbar support is a pad "
                   "bolted where marketing puts it. The engine solves Layer 1: lumbar curve radius 320 mm "
                   "matched to L3-L5 lordosis across 5th-95th percentile torsos; synchro-tilt ratio 2.4:1 "
                   "(backrest to seat) with resistance 18-42 Nm across the travel; mesh tension 90 N/m "
                   "for hammock support without pressure points. Layer 2 selects die-cast aluminum "
                   "A380 frame and glass-filled nylon 66, mesh PET weave at 90 N/m. Layer 3 defines "
                   "spline backrest geometry and mold draft. Layer 4 emits die-casting and injection "
                   "molding programs plus automated torque-check assembly. Layer 5 flat-packs into a "
                   "recyclable carton solved from the disassembled envelope."),
    "summary": ("A synchro-tilt task chair: 320 mm lumbar radius, 2.4:1 tilt ratio, 18-42 Nm resistance, "
                "90 N/m mesh. Die-cast A380 aluminum frame, injection-molded nylon 66, torque-checked "
                "assembly, recyclable flat-pack carton."),
    "definitions": {
        "Synchro-tilt": "seat and backrest reclining together at a fixed ratio (2.4:1 here).",
        "Lumbar radius": "the curvature of the backrest at L3-L5; 320 mm matches average lordosis.",
        "Mesh tension": "weave preload; 90 N/m suspends without hammocking.",
    },
    "components": [
        "Backrest: PET mesh at 90 N/m over nylon 66 spline frame, 320 mm lumbar radius",
        "Seat: molded foam over nylon pan, waterfall front edge",
        "Mechanism: synchro-tilt 2.4:1, 18-42 Nm resistance",
        "Base: die-cast A380 aluminum, five-star, 60 mm casters",
    ],
    "parametric_table": {
        "lumbar_radius_mm": "320",
        "synchro_tilt_ratio": "2.4:1",
        "tilt_resistance_nm": "18-42",
        "mesh_tension_n_per_m": "90",
        "seat_height_mm": "440-560",
        "seat_depth_mm": "470",
        "backrest_height_mm": "620",
        "frame_alloy": "A380 die-cast aluminum",
        "frame_polymer": "glass-filled nylon 66",
        "caster_dia_mm": "60",
        "rated_load_kg": "150",
    },
    "formulas": [
        "Lumbar contact pressure: 320 mm radius keeps peak pressure under 4 kPa across percentile torsos (design target).",
        "Tilt torque: resistance 18-42 Nm balances recline effort against return force for 50-150 kg users.",
    ],
    "figures": [
        "FIG. 1: side elevation with lumbar radius arc and tilt pivot.",
        "FIG. 2: backrest spline geometry with mesh tension vectors.",
        "FIG. 3: exploded mechanism: tilt plates, springs, torque-check points.",
    ],
    "embodiments": [
        "Task chair embodiment with adjustable arms.",
        "Drafting stool embodiment with foot ring (same layer solutions, taller gas lift).",
        "Conference embodiment without arms (reduced envelope).",
    ],
    "example_scenario": ("A 95th-percentile user leans back: the backrest follows at 2.4:1, resistance holds "
                         "at 30 Nm, lumbar contact stays even, and the mesh breathes through an 8-hour day."),
    "performance": [
        "BIFMA X5.1 duty cycle: 200,000 tilt cycles (design target).",
        "Lumbar pressure: < 4 kPa peak (design target).",
        "Assembly torque: 100% joints torque-checked to spec.",
    ],
    "materials": ["A380 die-cast aluminum", "glass-filled nylon 66", "PET mesh",
                  "steel gas lift", "recyclable corrugated carton"],
    "processes": ["aluminum die casting", "injection molding", "mesh weaving",
                  "automated torque-check assembly", "flat-pack carton die cutting"],
    "manufacture_steps": [
        "1. Die-cast A380 base and mechanism housings; machine pivot bores.",
        "2. Injection-mold nylon 66 backrest frame and seat pan with mold draft per Layer 3.",
        "3. Weave and pre-tension PET mesh to 90 N/m; bond to frame.",
        "4. Assemble synchro-tilt mechanism; set resistance 18-42 Nm.",
        "5. Automated torque-check every fastener; record values.",
        "6. QA: tilt cycle test, lumbar pressure mapping; stamp autoread block.",
        "7. Flat-pack into recyclable carton per Layer 5 nesting solution.",
    ],
    "operation": "Adjust seat height, tilt tension, and armrests; the synchro mechanism follows the sitter.",
    "claims": [
        "1. An ergonomic chair generated by the five-layer pipeline, wherein lumbar radius 320 mm, synchro-tilt ratio 2.4:1, and mesh tension 90 N/m are solved from percentile torso data.",
        "2. The chair of claim 1 wherein the CAM layer emits die-casting and injection-molding programs directly from the Layer 3 spline geometry.",
        "3. The chair of claim 1 wherein assembly is verified by automated torque-check of every fastener.",
        "4. The chair of claim 1 packed in a recyclable flat-pack carton whose dimensions are solved from the disassembled envelope.",
    ],
    "demo_blurb": "Working simulation of the chair: adjust user weight and recline, watch resistance and lumbar pressure respond.",
    "demo_params": [
        {"id": "p0", "label": "User mass", "unit": "kg", "min": 50, "max": 150, "step": 1, "default": 80},
        {"id": "p1", "label": "Recline angle", "unit": "deg", "min": 0, "max": 25, "step": 1, "default": 10},
        {"id": "p2", "label": "Mesh tension", "unit": "N/m", "min": 60, "max": 120, "step": 5, "default": 90},
    ],
    "demo_outputs": [
        {"label": "Required resistance (simulated)", "unit": "Nm", "expr": "18+(p0-50)*0.24"},
        {"label": "Lumbar pressure (simulated)", "unit": "kPa", "expr": "3.2+(90-p2)/90*1.5"},
        {"label": "Seat-back angle (simulated)", "unit": "deg", "expr": "100+p1"},
    ],
    "measurements": [
        {"name": "Lumbar radius", "value": "320.0", "unit": "mm", "tolerance": "±5"},
        {"name": "Seat height range", "value": "440-560", "unit": "mm", "tolerance": ""},
        {"name": "Rated load", "value": "150", "unit": "kg", "tolerance": ""},
        {"name": "Mesh tension", "value": "90", "unit": "N/m", "tolerance": "±5"},
        {"name": "Tilt resistance", "value": "18-42", "unit": "Nm", "tolerance": ""},
        {"name": "Caster diameter", "value": "60.0", "unit": "mm", "tolerance": "±0.5"},
    ],
    "abstract": ("An ergonomic chair produced as the solved output of the five-layer generation engine. "
                 "Layer 1 fixes lumbar curve radius 320 mm, synchro-tilt ratio 2.4:1 with 18-42 Nm "
                 "resistance, and mesh tension 90 N/m from percentile torso data. Layer 2 selects A380 "
                 "die-cast aluminum and glass-filled nylon 66. Layer 3 defines spline backrest geometry. "
                 "Layer 4 emits die-casting, injection molding, and automated torque-check assembly. "
                 "Layer 5 flat-packs the chair in a recyclable carton solved from its disassembled envelope."),
}

# ----------------------------------------------------------------------------
# Spec 4: hand tools (hammer + screwdriver)
# ----------------------------------------------------------------------------
HANDTOOLS = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to Hand Tools",
    "object_phrase": "hand tools",
    "one_sentence": "A claw hammer and screwdriver set whose shock absorption, grip durometer, torsion limits, and alloy composition are solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("These are a hammer and screwdrivers designed the god-mode way: how much shock "
                      "reaches your elbow, how the grip feels in a sweaty hand, how much twist the shaft "
                      "takes before it yields - all solved as numbers first, then the forge, the "
                      "overmold, and the pegboard sleeve follow."),
    "primary_function": "Drive nails and fasteners with controlled impact, minimal transmitted shock, and no-slip grip.",
    "background": ("Hand tools are forged to a shape, then a grip is glued on: shock travels straight to "
                   "the elbow and handles slip when wet. The engine solves Layer 1: shock absorption - "
                   "handle system attenuates 40% of impact energy at 20 J strikes; grip durometer 55 "
                   "Shore A overmold with mu 0.8 wet; torsion limit 35 Nm on the screwdriver shaft "
                   "before yield; hammer head 1045 high-carbon steel at 52 HRC face. Layer 2 selects "
                   "1045 steel, fiberglass-core handle, TPE overmold at 55 Shore A. Layer 3 defines the "
                   "claw spline and fluted grip geometry. Layer 4 emits drop-forging schedules, induction "
                   "hardening profiles, and dual-material overmold injection. Layer 5 sleeves each tool "
                   "for pegboard hanging with laser-etched sizing."),
    "summary": ("A claw hammer (16 oz, 1045 steel, 52 HRC face) and screwdriver set with 40% shock "
                "attenuation, 55 Shore A overmold grips at mu 0.8 wet, and 35 Nm torsion limit. "
                "Drop-forged, induction-hardened, laser-etched, pegboard-sleeved."),
    "definitions": {
        "Shock attenuation": "fraction of impact energy absorbed by the handle system; 40% at 20 J.",
        "Durometer": "Shore A hardness; 55A is a firm rubber grip.",
        "Torsion limit": "twist torque before permanent shaft deformation; 35 Nm.",
    },
    "components": [
        "Hammer head: 1045 high-carbon steel, 16 oz, face 52 HRC, claw spline",
        "Handle: fiberglass core with TPE overmold, 55 Shore A, mu 0.8 wet",
        "Screwdriver shafts: S2 tool steel, 35 Nm torsion limit",
        "Tips: induction-hardened, laser-etched sizing",
    ],
    "parametric_table": {
        "hammer_mass_oz": "16",
        "head_steel": "1045 high-carbon",
        "face_hardness_hrc": "52",
        "shock_attenuation_pct": "40",
        "impact_energy_j": "20",
        "grip_durometer_shore_a": "55",
        "grip_friction_wet": "0.8",
        "shaft_torsion_limit_nm": "35",
        "shaft_steel": "S2 tool steel",
        "claw_opening_mm": "28",
    },
    "formulas": [
        "Attenuation: handle damping ratio solved so transmitted impulse at 20 J is 60% of a solid-steel handle.",
        "Torsion: shaft diameter solved so 35 Nm produces shear stress at 80% of S2 yield.",
    ],
    "figures": [
        "FIG. 1: hammer side elevation with claw spline and grip flute pattern.",
        "FIG. 2: handle cross-section: fiberglass core, TPE overmold thickness map.",
        "FIG. 3: screwdriver shaft with torsion test curve to 35 Nm.",
    ],
    "embodiments": [
        "16 oz claw hammer embodiment.",
        "6-piece screwdriver set embodiment (Phillips/flat, three sizes each).",
        "Insulated 1000 V electrician embodiment (same geometry, insulated overmold).",
    ],
    "example_scenario": ("A framer drives 16d nails all day: the handle absorbs 40% of each 20 J strike, "
                         "the wet grip holds at mu 0.8, and the screwdriver takes a 30 Nm cheater bar "
                         "without yielding."),
    "performance": [
        "Shock: 40% attenuation at 20 J strikes (design target).",
        "Face: 52 HRC, no mushrooming after 5,000 strikes (design target).",
        "Grip: mu 0.8 wet, 55 Shore A (design target).",
    ],
    "materials": ["1045 high-carbon steel", "S2 tool steel", "fiberglass handle core",
                  "TPE overmold 55 Shore A", "pegboard PET sleeve"],
    "processes": ["drop forging", "induction hardening", "dual-material overmold injection",
                  "laser etching", "pegboard sleeve sealing"],
    "manufacture_steps": [
        "1. Drop-forge hammer head and screwdriver blanks from 1045/S2 steel.",
        "2. Induction-harden striking face to 52 HRC and screwdriver tips.",
        "3. Mold fiberglass handle cores; overmold TPE at 55 Shore A with flute geometry.",
        "4. Assemble head to handle with epoxy and steel wedge; proof-load.",
        "5. Laser-etch sizing and branding; QA shock, torsion, and hardness.",
        "6. Sleeve for pegboard hanging per Layer 5 layout.",
    ],
    "operation": "Strike with the face, pull with the claw; turn fasteners within the 35 Nm shaft limit.",
    "claims": [
        "1. Hand tools generated by the five-layer pipeline, wherein 40% shock attenuation, 55 Shore A grip durometer, and 35 Nm torsion limit are solved parameters.",
        "2. The tools of claim 1 wherein the CAM layer emits drop-forging and induction-hardening schedules from the Layer 3 geometry.",
        "3. The tools of claim 1 with laser-etched sizing and pegboard sleeves solved by the packaging layer.",
    ],
    "demo_blurb": "Working simulation of the hand tools: adjust strike energy and grip, watch transmitted shock and slip respond.",
    "demo_params": [
        {"id": "p0", "label": "Strike energy", "unit": "J", "min": 5, "max": 40, "step": 1, "default": 20},
        {"id": "p1", "label": "Grip durometer", "unit": "Shore A", "min": 40, "max": 70, "step": 1, "default": 55},
        {"id": "p2", "label": "Shaft torque", "unit": "Nm", "min": 5, "max": 50, "step": 1, "default": 20},
    ],
    "demo_outputs": [
        {"label": "Transmitted shock (simulated)", "unit": "J", "expr": "p0*0.6"},
        {"label": "Grip slip risk (simulated)", "unit": "%", "expr": "(70-p1)*1.2"},
        {"label": "Shaft margin (simulated)", "unit": "Nm", "expr": "35-p2"},
    ],
    "measurements": [
        {"name": "Hammer mass", "value": "16", "unit": "oz", "tolerance": "±0.5"},
        {"name": "Face hardness", "value": "52", "unit": "HRC", "tolerance": "±2"},
        {"name": "Shock attenuation", "value": "40", "unit": "%", "tolerance": "min"},
        {"name": "Grip durometer", "value": "55", "unit": "Shore A", "tolerance": "±3"},
        {"name": "Shaft torsion limit", "value": "35", "unit": "Nm", "tolerance": "min"},
        {"name": "Claw opening", "value": "28.0", "unit": "mm", "tolerance": "±0.5"},
    ],
    "abstract": ("Hand tools produced as the solved output of the five-layer generation engine. Layer 1 "
                 "fixes 40% shock attenuation at 20 J strikes, 55 Shore A overmold grip at mu 0.8 wet, "
                 "35 Nm shaft torsion limit, and a 52 HRC hammer face. Layer 2 selects 1045 and S2 steels "
                 "with fiberglass-core handles. Layer 3 defines claw spline and fluted grip geometry. "
                 "Layer 4 emits drop forging, induction hardening, and dual-material overmolding. Layer 5 "
                 "solves laser-etched pegboard sleeves."),
}

# ----------------------------------------------------------------------------
# Spec 5: storage containers & jars
# ----------------------------------------------------------------------------
CONTAINERS = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to Storage Containers and Jars",
    "object_phrase": "storage containers",
    "one_sentence": "Airtight storage containers and jars whose stack load limits, seal compression, and wall ribbing are solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("These are food storage containers designed the god-mode way: how much weight they "
                      "hold when stacked, how the lid seals airtight, and how the walls resist dents are "
                      "solved as numbers first - then the molds, the seals, and the shrink-wrap follow."),
    "primary_function": "Store food airtight, stack safely, survive drops and dishwashers.",
    "background": ("Containers are thin-walled guesses: lids warp, seals leak, stacks crush. The engine "
                   "solves Layer 1: stack load 25 kg per container over 6-high stacks; lid seal compression "
                   "1.2 mm on a silicone gasket for airtightness; wall ribbing 1.5 mm deep for 1 m drop "
                   "survival. Layer 2 selects HDPE for blow-molded bodies and PET for injection "
                   "stretch-blow-molded jars, food-grade. Layer 3 defines rib patterns and 3-degree mold "
                   "draft. Layer 4 emits blow-molding parison programs and ISBM preform schedules plus "
                   "induction-seal liner application. Layer 5 applies tamper-evident tear bands and "
                   "shrink-wrap multi-packs."),
    "summary": ("Airtight HDPE containers and PET jars: 25 kg stack load, 1.2 mm seal compression, "
                "1.5 mm wall ribs. Blow-molded and stretch-blow-molded, induction-sealed, tamper-banded, "
                "shrink-wrapped."),
    "definitions": {
        "Stack load": "weight each container bears in a 6-high stack; 25 kg.",
        "Seal compression": "gasket squeeze at full lid closure; 1.2 mm.",
        "ISBM": "injection stretch blow molding, for PET jars.",
    },
    "components": [
        "Body: HDPE blow-molded, 1.5 mm ribbed walls, 3-degree draft",
        "Jar: PET ISBM, 28 mm neck finish",
        "Lid: PP with silicone gasket, 1.2 mm compression",
        "Seal: induction-seal foil liner; tamper-evident tear band",
    ],
    "parametric_table": {
        "stack_load_kg": "25",
        "stack_height": "6",
        "seal_compression_mm": "1.2",
        "wall_rib_depth_mm": "1.5",
        "mold_draft_deg": "3",
        "body_material": "HDPE food-grade",
        "jar_material": "PET food-grade",
        "neck_finish_mm": "28",
        "drop_height_m": "1",
        "volumes_l": "0.5 / 1 / 2 / 4",
    },
    "formulas": [
        "Stack: wall section modulus solved so 25 kg x 6 creep over 30 days stays under 2% deformation.",
        "Seal: 1.2 mm compression on the gasket gives contact pressure above the airtight threshold with margin.",
    ],
    "figures": [
        "FIG. 1: container elevation with rib pattern and stack load arrows.",
        "FIG. 2: lid cross-section: gasket, 1.2 mm compression zone, tear band.",
        "FIG. 3: jar preform and stretch-blow stages.",
    ],
    "embodiments": [
        "0.5/1/2/4 L rectangular container embodiment.",
        "PET jar embodiment with 28 mm neck for dry goods.",
        "Commercial 20 L bulk embodiment (same layer solutions, scaled).",
    ],
    "example_scenario": ("A pantry stacks six 2 L containers of flour: the bottom one holds 25 kg without "
                         "creep, every lid seals airtight at 1.2 mm compression, and a dropped jar survives "
                         "the 1 m fall."),
    "performance": [
        "Airtight: < 1% pressure loss over 7 days (design target).",
        "Stack creep: < 2% deformation at 25 kg over 30 days (design target).",
        "Drop: 1 m to concrete without cracking (design target).",
    ],
    "materials": ["HDPE food-grade", "PET food-grade", "PP lids", "silicone gaskets",
                  "induction-seal foil", "shrink film"],
    "processes": ["blow molding", "injection stretch blow molding", "induction sealing",
                  "tamper-band application", "shrink wrapping"],
    "manufacture_steps": [
        "1. Blow-mold HDPE bodies with 1.5 mm ribs and 3-degree draft.",
        "2. ISBM PET jars from preforms; finish 28 mm necks.",
        "3. Injection-mold PP lids; fit silicone gaskets.",
        "4. Apply induction-seal foil liners; fit tamper-evident tear bands.",
        "5. QA: seal compression 1.2 mm, stack load, drop test; stamp autoread block.",
        "6. Shrink-wrap multi-packs per Layer 5 layout.",
    ],
    "operation": "Fill, close lid to full compression, stack; tear band shows first opening.",
    "claims": [
        "1. Storage containers generated by the five-layer pipeline, wherein 25 kg stack load, 1.2 mm seal compression, and 1.5 mm wall ribbing are solved parameters.",
        "2. The containers of claim 1 wherein the CAM layer emits blow-molding and ISBM schedules from the Layer 3 rib and draft geometry.",
        "3. The containers of claim 1 with induction-seal liners and tamper-evident tear bands applied per the packaging layer.",
    ],
    "demo_blurb": "Working simulation of the containers: adjust stack load and seal compression, watch creep and airtightness respond.",
    "demo_params": [
        {"id": "p0", "label": "Stack load", "unit": "kg", "min": 5, "max": 40, "step": 1, "default": 25},
        {"id": "p1", "label": "Seal compression", "unit": "mm", "min": 0.5, "max": 2.0, "step": 0.1, "default": 1.2},
        {"id": "p2", "label": "Drop height", "unit": "m", "min": 0.3, "max": 2.0, "step": 0.1, "default": 1.0},
    ],
    "demo_outputs": [
        {"label": "30-day creep (simulated)", "unit": "%", "expr": "p0*0.06"},
        {"label": "Seal integrity (simulated)", "unit": "%", "expr": "p1>=1.0?99:70+p1*20"},
        {"label": "Drop survival (simulated)", "unit": "%", "expr": "p2<=1.2?98:98-(p2-1.2)*40"},
    ],
    "measurements": [
        {"name": "Stack load rating", "value": "25", "unit": "kg", "tolerance": "min"},
        {"name": "Seal compression", "value": "1.2", "unit": "mm", "tolerance": "±0.1"},
        {"name": "Rib depth", "value": "1.5", "unit": "mm", "tolerance": "±0.2"},
        {"name": "Mold draft", "value": "3.0", "unit": "deg", "tolerance": ""},
        {"name": "Neck finish", "value": "28.0", "unit": "mm", "tolerance": "±0.2"},
        {"name": "Largest volume", "value": "4", "unit": "L", "tolerance": ""},
    ],
    "abstract": ("Storage containers and jars produced as the solved output of the five-layer generation "
                 "engine. Layer 1 fixes 25 kg stack load over 6-high stacks, 1.2 mm gasket seal compression, "
                 "and 1.5 mm wall ribbing for 1 m drop survival. Layer 2 selects food-grade HDPE and PET. "
                 "Layer 3 defines rib patterns with 3-degree mold draft. Layer 4 emits blow molding and "
                 "injection stretch blow molding plus induction sealing. Layer 5 applies tamper-evident "
                 "tear bands and shrink-wrap multi-packs."),
}

# ----------------------------------------------------------------------------
# Spec 6: desktop organizers & trays
# ----------------------------------------------------------------------------
ORGANIZERS = {
    "title": "God-Mode Algorithmic Object Generation Engine Applied to Desktop Organizers and Trays",
    "object_phrase": "desktop organizers",
    "one_sentence": "Desktop organizers and trays whose slot angles, pen-well diameters, and friction-pad placement are solved in one pass of the five-layer god-mode generation engine.",
    "plain_english": ("This is a desk organizer designed the god-mode way: the angle papers rest at, the "
                      "size of the pen holes, and where the grippy pads go so it never slides are all "
                      "solved as numbers first - then the CNC paths or printer layers and the kraft sleeve "
                      "follow."),
    "primary_function": "Hold documents, pens, and tools at ergonomic angles without sliding on the desk.",
    "background": ("Organizers are boxes with holes: papers slump, pens rattle, the tray walks across the "
                   "desk. The engine solves Layer 1: document slots at 72 degrees for self-supporting "
                   "lean; pen wells 14 mm and 18 mm diameters for standard barrels; friction pads at "
                   "four corners with mu 0.9 against wood laminate. Layer 2 selects anodized aluminum "
                   "6061 or FSC walnut for CNC, PLA/PETG for 3D printing. Layer 3 defines slot spline "
                   "profiles and well bores. Layer 4 emits CNC toolpaths or slicer profiles. Layer 5 "
                   "solves beeswax finish or anodizing plus a kraft sleeve."),
    "summary": ("A modular desk organizer: 72-degree document slots, 14/18 mm pen wells, mu 0.9 corner "
                "friction pads. CNC-machined aluminum or walnut, or 3D-printed PLA/PETG; beeswax or "
                "anodized finish; kraft sleeve packaging."),
    "definitions": {
        "Slot angle": "72 degrees from horizontal; papers lean without slumping.",
        "Pen well": "bored hole; 14 mm for slim pens, 18 mm for markers.",
        "Friction pad": "corner pad at mu 0.9 preventing desk walk.",
    },
    "components": [
        "Body: anodized aluminum 6061 or FSC walnut, CNC-machined",
        "Slots: three document slots at 72 degrees",
        "Wells: 14 mm and 18 mm pen wells",
        "Pads: four silicone corner pads, mu 0.9",
    ],
    "parametric_table": {
        "slot_angle_deg": "72",
        "slot_count": "3",
        "pen_well_dia_mm": "14 / 18",
        "friction_mu": "0.9",
        "body_options": "aluminum 6061 / walnut / PLA / PETG",
        "finish_options": "beeswax / anodized",
        "footprint_mm": "320 x 140",
        "height_mm": "110",
        "print_layer_mm": "0.2",
        "infill_pct": "25",
    },
    "formulas": [
        "Slot lean: 72 degrees keeps paper stack center of mass inside the slot base for up to 40 sheets.",
        "Slide: four mu 0.9 pads resist lateral loads up to 12 N on laminate.",
    ],
    "figures": [
        "FIG. 1: front elevation with 72-degree slot angles.",
        "FIG. 2: plan view: pen wells, friction pad positions.",
        "FIG. 3: CNC toolpath preview / slicer layer diagram.",
    ],
    "embodiments": [
        "Aluminum CNC embodiment, anodized.",
        "Walnut embodiment, beeswax finish.",
        "3D-printed PLA/PETG embodiment, 0.2 mm layers, 25% infill.",
    ],
    "example_scenario": ("A designer drops 30 sheets in the slots: they lean at 72 degrees without slumping, "
                         "pens fit the 14/18 mm wells, and the tray never walks when bumped."),
    "performance": [
        "Paper capacity: 40 sheets per slot without slump (design target).",
        "Slide resistance: 12 N lateral without movement (design target).",
        "Finish: beeswax/anodize survives 5 years of desk use (design target).",
    ],
    "materials": ["aluminum 6061", "FSC walnut", "PLA/PETG filament", "silicone pads",
                  "beeswax finish", "kraft sleeve board"],
    "processes": ["CNC machining", "FDM 3D printing", "hand sanding", "beeswax finishing",
                  "anodizing", "kraft die cutting"],
    "manufacture_steps": [
        "1. CNC-machine body from aluminum 6061 or walnut; or 3D-print at 0.2 mm layers, 25% infill.",
        "2. Bore pen wells at 14 mm and 18 mm; cut document slots at 72 degrees.",
        "3. Hand-sand; apply beeswax finish or anodize per embodiment.",
        "4. Fit four silicone friction pads at solved corner positions.",
        "5. QA: slot angle, well diameter, slide test; stamp autoread block.",
        "6. Sleeve in kraft packaging per Layer 5 layout.",
    ],
    "operation": "Place on desk; load documents, pens, and tools; wipe clean as needed.",
    "claims": [
        "1. A desktop organizer generated by the five-layer pipeline, wherein 72-degree slot angles, 14/18 mm pen-well diameters, and mu 0.9 friction-pad placement are solved parameters.",
        "2. The organizer of claim 1 wherein the CAM layer emits CNC toolpaths or 3D-printer slicing profiles from the Layer 3 geometry.",
        "3. The organizer of claim 1 finished per embodiment (beeswax or anodized) and sleeved in kraft packaging solved by the packaging layer.",
    ],
    "demo_blurb": "Working simulation of the organizer: adjust slot angle and load, watch slump and slide respond.",
    "demo_params": [
        {"id": "p0", "label": "Slot angle", "unit": "deg", "min": 60, "max": 85, "step": 1, "default": 72},
        {"id": "p1", "label": "Sheets per slot", "unit": "sheets", "min": 5, "max": 60, "step": 1, "default": 30},
        {"id": "p2", "label": "Lateral push", "unit": "N", "min": 1, "max": 20, "step": 1, "default": 5},
    ],
    "demo_outputs": [
        {"label": "Slump risk (simulated)", "unit": "%", "expr": "p0<68?(68-p0)*4+p1*0.3:p1*0.3"},
        {"label": "Slide risk (simulated)", "unit": "%", "expr": "p2>12?(p2-12)*8:0"},
        {"label": "Capacity headroom (simulated)", "unit": "sheets", "expr": "40-p1"},
    ],
    "measurements": [
        {"name": "Slot angle", "value": "72.0", "unit": "deg", "tolerance": "±1"},
        {"name": "Pen well small", "value": "14.0", "unit": "mm", "tolerance": "±0.2"},
        {"name": "Pen well large", "value": "18.0", "unit": "mm", "tolerance": "±0.2"},
        {"name": "Footprint", "value": "320 x 140", "unit": "mm", "tolerance": "±1"},
        {"name": "Height", "value": "110.0", "unit": "mm", "tolerance": "±1"},
        {"name": "Friction coefficient", "value": "0.9", "unit": "mu", "tolerance": "min"},
    ],
    "abstract": ("A desktop organizer produced as the solved output of the five-layer generation engine. "
                 "Layer 1 fixes 72-degree document slots, 14/18 mm pen wells, and mu 0.9 corner friction "
                 "pads. Layer 2 selects aluminum 6061, walnut, or PLA/PETG. Layer 3 defines slot splines "
                 "and well bores. Layer 4 emits CNC toolpaths or 0.2 mm-layer 3D-print profiles. Layer 5 "
                 "solves beeswax or anodized finishing and kraft sleeve packaging."),
}

SPECS = [CUP, FLATWARE, CHAIR, HANDTOOLS, CONTAINERS, ORGANIZERS]


def existing_ids():
    """All spec IDs already present in the main repo chunks + hot file."""
    ids = set()
    if os.path.exists(HOT):
        with open(HOT, encoding="utf-8") as fh:
            for ln in fh:
                ln = ln.strip()
                if ln:
                    try:
                        ids.add(json.loads(ln)["spec_id"])
                    except Exception:
                        pass
    voldir = os.path.join(REPO, "data", "volumes")
    for fn in sorted(os.listdir(voldir)):
        if fn.startswith("specs-c") and fn.endswith(".jsonl.gz"):
            with gzip.open(os.path.join(voldir, fn), "rt", encoding="utf-8") as fh:
                for ln in fh:
                    ln = ln.strip()
                    if ln:
                        try:
                            ids.add(json.loads(ln)["spec_id"])
                        except Exception:
                            pass
    return ids


def main():
    st = json.load(open(STATE, encoding="utf-8"))
    nxt = st["next_index"]
    assert nxt == FIRST_ID, f"state next_index {nxt} != expected {FIRST_ID}; refusing to run"
    assert len(SPECS) == COUNT

    have = existing_ids()
    new_ids = [f"JAH-SPEC-{FIRST_ID + i:06d}" for i in range(COUNT)]
    dupes = [i for i in new_ids if i in have]
    if dupes:
        raise SystemExit(f"ID collision, refusing: {dupes}")

    records = [make_record(FIRST_ID + i, SPECS[i]) for i in range(COUNT)]

    # Validate autoread blocks parse under the canonical schema.
    for rec in records:
        fields, order, warnings, valid, missing = ja.parse(rec["autoread_block"])
        if not valid:
            raise SystemExit(f"autoread invalid for {rec['spec_id']}: missing={missing}")
        if fields.get("SPEC_ID") != rec["spec_id"]:
            raise SystemExit(f"autoread SPEC_ID mismatch for {rec['spec_id']}")

    with open(HOT, "a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    st["next_index"] = FIRST_ID + COUNT
    json.dump(st, open(STATE, "w", encoding="utf-8"))

    for rec in records:
        print(f"WROTE {rec['spec_id']}: {rec['title']}")


if __name__ == "__main__":
    main()
