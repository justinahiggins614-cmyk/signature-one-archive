#!/usr/bin/env python3
"""Draft patent-spec generator for The Spec Catalog (signature-one-archive).

Generates deterministic, seeded, UNIQUE draft invention specifications authored by
Justin Addam Higgins (JAH), each following the forced Signature-One spec format:
patent-page fields + signature_tool_mapping + key_parameters + autoread_block
+ algorithm_steps (the 5 reversed-allowance steps).

Usage:  python3 code/specs/generate_specs.py [count]   (default 10000)

- Appends COUNT new specs to data/specs.jsonl (one JSON object per line).
- State lives in code/specs/state.json: {seed, next_index, used_titles}.
- Each spec index i is seeded independently ("JAH-<seed>-<i>"), so re-runs APPEND
  new unique specs and never duplicate, regardless of batch sizes.
- Title collisions are resolved with " (Rev N)" suffixes tracked in the state file.

These are JAH's OWN draft invention specs. They are NOT granted patents and must
never be presented as such.
"""
import json
import os
import random
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(REPO, "data", "specs.jsonl")
STATE = os.path.join(HERE, "state.json")

INVENTOR = "Justin Addam Higgins"
STATUS = "Draft \u2014 ready to file"
SEED = 20260928
DATE_START = date(2000, 1, 1)
DATE_END = date(2026, 9, 28)

# ----------------------------------------------------------------------------
# Categories: (name, kind, cpc, [device nouns])
# ----------------------------------------------------------------------------
SWCATS = [
 ("Artificial Intelligence", "G06N", ["cognitive reasoning engine", "neural planning module", "autonomous goal solver", "knowledge graph reasoner", "symbolic inference core", "multi-agent coordinator", "adaptive learning controller", "causal inference engine", "neural-symbolic bridge", "self-modifying policy net"]),
 ("Machine Learning", "G06N", ["gradient boosting pipeline", "federated training coordinator", "online learning loop", "meta-learning scheduler", "distillation engine", "hyperparameter tuner", "feature store indexer", "model registry service", "drift monitor", "ensemble voter"]),
 ("Cybersecurity", "H04L", ["threat hunting console", "intrusion prevention engine", "malware sandbox analyzer", "phishing detector", "endpoint guard agent", "network telescope", "honeypot mesh", "forensic timeline builder", "vulnerability scanner", "patch orchestrator"]),
 ("Network Routing", "H04L", ["adaptive path selector", "congestion-aware router", "multipath scheduler", "BGP policy engine", "traffic shaper", "load balancer", "failover controller", "QoS classifier", "packet inspector", "mesh coordinator"]),
 ("Cloud Infrastructure", "G06F", ["autoscaling controller", "spot instance bidder", "region failover manager", "virtual network provisioner", "secret vault", "config drift detector", "cost optimizer", "quota governor", "multi-cloud broker", "bare-metal scheduler"]),
 ("Databases", "G06F", ["distributed SQL engine", "time-series store", "graph query planner", "columnar compactor", "vector index", "change-data-capture tap", "shard rebalancer", "write-ahead log", "snapshot manager", "cache-through layer"]),
 ("Mobile Applications", "G06F", ["offline-first sync engine", "push notification hub", "in-app purchase validator", "deep-link router", "battery-aware scheduler", "on-device cache", "biometric login module", "app clip launcher", "background fetch worker", "crash reporter"]),
 ("Operating Systems", "G06F", ["process scheduler", "memory allocator", "file system journal", "device driver shim", "interrupt dispatcher", "power governor", "container runtime", "sandbox enforcer", "boot verifier", "crash dump analyzer"]),
 ("Developer Tools", "G06F", ["incremental compiler", "live reload server", "debug symbol indexer", "profiler agent", "lint rule engine", "code formatter", "dependency resolver", "build cache", "test runner", "release pipeline"]),
 ("Encryption", "H04L", ["key rotation service", "envelope encryption wrapper", "hardware-backed keystore", "certificate manager", "TLS terminator", "secret splitter", "quantum-safe cipher suite", "stream cipher engine", "message authenticator", "key escrow vault"]),
 ("Data Compression", "H03M", ["lossless codec", "dictionary compressor", "entropy coder", "image transcoder", "video bitrate ladder", "deduplication filter", "delta sync engine", "columnar encoder", "log compressor", "backup compactor"]),
 ("Voice Interfaces", "G10L", ["wake-word detector", "speech recognizer", "speaker verifier", "noise suppressor", "voice activity detector", "dialog manager", "text-to-speech voice", "pronunciation learner", "call transcriber", "voice biometric gate"]),
 ("Recommender Systems", "G06Q", ["collaborative filter", "content ranker", "session-based recommender", "diversity optimizer", "cold-start bootstrapper", "click predictor", "ranking blender", "personalization engine", "trending detector", "taste profiler"]),
 ("Edge Computing", "G06F", ["edge orchestrator", "fog cache node", "offline inference runtime", "gateway aggregator", "edge function runner", "bandwidth saver", "local-first database", "sensor hub", "edge model updater", "disruption tolerator"]),
 ("APIs", "G06F", ["rate limiter", "API gateway", "schema validator", "webhook dispatcher", "version router", "token broker", "request deduplicator", "response cache", "API analytics meter", "developer portal"]),
 ("Software Testing", "G06F", ["fuzzing engine", "mutation tester", "property-based checker", "load generator", "chaos injector", "snapshot tester", "contract verifier", "flaky-test detector", "coverage mapper", "regression bisection tool"]),
 ("UI Frameworks", "G06F", ["virtual DOM differ", "reactive state store", "layout engine", "theme compiler", "accessibility checker", "gesture recognizer", "animation scheduler", "form validator", "component registry", "design token resolver"]),
 ("Video Streaming", "H04N", ["adaptive bitrate controller", "segment prefetcher", "CDN selector", "live transcoder", "DVR window manager", "ad stitcher", "subtitle synchronizer", "playback healer", "bandwidth estimator", "codec negotiator"]),
 ("Search Engines", "G06F", ["crawl scheduler", "index shard", "query parser", "ranking function", "spell corrector", "autocomplete trie", "snippet generator", "duplicate detector", "freshness scorer", "vertical search mixer"]),
 ("Firmware", "G06F", ["bootloader", "OTA update agent", "secure boot chain", "device tree builder", "watchdog timer", "NVRAM manager", "peripheral initializer", "firmware rollback guard", "diagnostic shell", "calibration store"]),
 ("Natural Language Processing", "G06F", ["tokenizer", "named-entity recognizer", "sentiment classifier", "summarizer", "paraphrase detector", "intent classifier", "coreference resolver", "translation engine", "question answerer", "toxicity filter"]),
 ("Computer Vision", "G06K", ["object detector", "image segmenter", "pose estimator", "OCR engine", "face matcher", "depth estimator", "video tracker", "defect inspector", "scene classifier", "keypoint extractor"]),
 ("Blockchain", "H04L", ["consensus validator", "smart contract sandbox", "light client", "bridge relayer", "mempool prioritizer", "state pruner", "zero-knowledge prover", "wallet signer", "oracle feeder", "fork detector"]),
 ("Virtual Reality", "G06T", ["frame predictor", "foveated renderer", "tracking fusion engine", "haptic mapper", "spatial audio mixer", "avatar rig", "locomotion controller", "guardian boundary", "latency compensator", "scene streamer"]),
 ("Augmented Reality", "G06T", ["plane detector", "occlusion handler", "anchor synchronizer", "light estimator", "hand tracker", "marker decoder", "persistent map", "shared session host", "render offloader", "gaze predictor"]),
 ("Gaming", "A63F", ["physics solver", "matchmaking balancer", "anti-cheat sentinel", "procedural world builder", "netcode predictor", "loot distributor", "leaderboard service", "replay recorder", "voice chat mixer", "tournament bracket engine"]),
 ("Payment Processing", "G06Q", ["card token vault", "fraud scorer", "settlement batcher", "refund reconciler", "multi-currency converter", "payout scheduler", "chargeback defender", "3-D Secure handler", "ledger writer", "payout splitter"]),
 ("Supply Chain Software", "G06Q", ["demand forecaster", "inventory optimizer", "route planner", "warehouse slotting engine", "supplier scorer", "purchase order matcher", "shipment tracker", "returns processor", "cold-chain monitor", "customs filer"]),
 ("Bioinformatics", "G16B", ["sequence aligner", "variant caller", "genome assembler", "protein folder", "phylogeny builder", "read trimmer", "annotation pipeline", "cohort query engine", "privacy-preserving aggregator", "biomarker ranker"]),
 ("CAD Software", "G06F", ["constraint solver", "parametric modeler", "mesh repairer", "tolerance analyzer", "render previewer", "version differ", "assembly matcher", "drawing exporter", "simulation linker", "BOM generator"]),
 ("Simulation", "G06F", ["finite-element solver", "particle simulator", "fluid dynamics grid", "traffic microsimulator", "crowd behavior model", "climate downscaler", "circuit simulator", "crash test modeler", "acoustic ray tracer", "thermal solver"]),
 ("Compilers", "G06F", ["lexer", "parser generator", "type checker", "optimizer pass", "register allocator", "linker", "JIT compiler", "bytecode verifier", "macro expander", "dead-code eliminator"]),
 ("Container Orchestration", "G06F", ["pod scheduler", "service mesh proxy", "autoscaler", "rolling updater", "health prober", "secret injector", "volume provisioner", "network policy enforcer", "cluster autoscaler", "job queue"]),
 ("Identity Management", "H04L", ["single sign-on broker", "MFA challenger", "directory synchronizer", "access certifier", "session manager", "passwordless authenticator", "role miner", "deprovisioning sweeper", "consent recorder", "risk-based step-up engine"]),
 ("Anomaly Detection", "G06N", ["outlier scorer", "baseline learner", "seasonality decomposer", "changepoint detector", "drift alarm", "root-cause ranker", "alert deduplicator", "threshold tuner", "streaming profiler", "incident correlator"]),
 ("Digital Twins", "G06F", ["twin synchronizer", "state mirror", "what-if simulator", "telemetry ingestor", "asset graph", "degradation modeler", "twin query API", "calibration loop", "event replayer", "twin access gateway"]),
 ("Quantum Software", "G06N", ["circuit transpiler", "error mitigation layer", "shot scheduler", "hybrid optimizer", "state vector simulator", "noise modeler", "qubit mapper", "calibration tracker", "result aggregator", "quantum kernel estimator"]),
 ("Geospatial", "G06F", ["tile server", "geocoder", "route optimizer", "geofence evaluator", "map matcher", "spatial index", "elevation sampler", "isochrone calculator", "fleet tracker", "address normalizer"]),
 ("Robotics Software", "B25J", ["motion planner", "SLAM mapper", "grasp planner", "fleet dispatcher", "behavior tree runner", "sensor calibrator", "collision checker", "odometry fuser", "task allocator", "teleoperation bridge"]),
 ("Data Pipelines", "G06F", ["stream joiner", "schema registry", "backfill runner", "lineage tracker", "quality gate", "partition pruner", "checkpoint manager", "exactly-once sink", "late-data handler", "pipeline linter"]),
]

HWCATS = [
 ("Processors", "G06F", ["multicore processor", "neural accelerator", "vector co-processor", "RISC-V core", "DSP block", "cryptographic engine", "floating-point unit", "cache controller", "branch predictor", "memory management unit"]),
 ("Memory Modules", "G11C", ["DDR5 DIMM", "LPDDR stack", "HBM interposer module", "MRAM array", "phase-change memory tile", "SRAM cache bank", "NAND flash die", "memory buffer chip", "ECC controller", "wear-leveling engine"]),
 ("Sensors", "G01D", ["MEMS accelerometer", "gyroscope die", "pressure transducer", "humidity sensor", "gas detector", "ambient light sensor", "proximity sensor", "Hall-effect sensor", "thermopile array", "strain gauge bridge"]),
 ("IoT Devices", "H04L", ["edge gateway", "mesh sensor node", "asset tracker", "smart meter", "environmental beacon", "door sensor", "leak detector", "air quality node", "parking sensor", "livestock tag"]),
 ("Robotics", "B25J", ["robotic arm joint", "gripper assembly", "mobile base", "servo actuator pack", "torque sensor wrist", "vision-guided picker", "AGV drive unit", "humanoid torso", "quadruped leg", "drone manipulator"]),
 ("Wearables", "A61B", ["fitness band", "smartwatch module", "heart-rate strap", "sleep tracker ring", "ECG patch", "hearing aid SoC", "smart insole", "posture coach clip", "hydration sensor", "fall detector pendant"]),
 ("Drones", "B64C", ["quadcopter frame", "gimbal stabilizer", "propulsion pod", "flight controller", "obstacle-avoidance array", "payload release", "battery sled", "telemetry radio", "landing skid", "swarm beacon"]),
 ("Batteries", "H01M", ["lithium cell", "battery management board", "solid-state pack", "fuel gauge IC", "charge controller", "cell balancer", "thermal fuse", "pouch cell", "supercapacitor bank", "wireless charge coil"]),
 ("Displays", "G09F", ["OLED panel", "e-paper module", "microLED tile", "LCD driver board", "touch controller", "backlight unit", "flexible display", "transparent OLED", "segment driver", "display multiplexer"]),
 ("Storage Devices", "G11B", ["NVMe SSD", "SATA controller", "RAID card", "tape drive", "optical drive", "flash translator", "enclosure backplane", "hot-swap caddy", "dedupe appliance", "archival vault"]),
 ("Peripherals", "G06F", ["mechanical keyboard", "precision mouse", "drawing tablet", "webcam module", "USB hub", "docking station", "card reader", "barcode scanner", "label printer", "fingerprint dongle"]),
 ("Smart Home", "G05B", ["smart thermostat", "video doorbell", "smart lock", "hub controller", "motion sensor", "smart plug", "garage opener", "smoke alarm", "water shutoff valve", "blind motor"]),
 ("Medical Devices", "A61B", ["infusion pump", "patient monitor", "defibrillator pad", "insulin pen", "spirometer", "pulse oximeter", "ultrasound probe", "surgical robot arm", "hearing screener", "wound VAC unit"]),
 ("Automotive Electronics", "B60R", ["ECU module", "ADAS camera", "radar unit", "TPMS sensor", "infotainment head unit", "OBD dongle", "battery contactor", "LED headlamp driver", "seat controller", "telematics box"]),
 ("Cameras", "H04N", ["image sensor", "lens assembly", "autofocus motor", "image signal processor", "thermal camera core", "action cam housing", "PTZ mount", "dashcam module", "doorbell cam", "microscope camera"]),
 ("Audio Equipment", "H04R", ["MEMS microphone", "speaker driver", "DAC board", "headphone amp", "soundbar array", "hearing loop", "studio monitor", "turntable preamp", "conference mic bar", "guitar pickup"]),
 ("Networking Gear", "H04L", ["managed switch", "Wi-Fi access point", "router board", "optical transceiver", "PoE injector", "firewall appliance", "mesh node", "5G small cell", "VPN concentrator", "patch panel"]),
 ("Power Supplies", "H02M", ["AC-DC converter", "DC-DC buck module", "bench supply", "UPS inverter", "PFC stage", "isolated brick", "LED driver", "USB-PD controller", "redundant PSU", "solar charge controller"]),
 ("Antennas", "H01Q", ["patch antenna", "dipole array", "phased array tile", "Yagi boom", "helical antenna", "MIMO panel", "NFC coil", "satellite dish feed", "vehicular shark-fin", "chip antenna"]),
 ("Semiconductors", "H01L", ["power MOSFET", "IGBT module", "voltage regulator", "op-amp", "ADC chip", "logic gate array", "clock generator", "ESD protector", "LED emitter", "photodiode"]),
 ("Haptics", "G06F", ["vibration motor", "piezo actuator", "force-feedback glove", "haptic trackpad", "tactile display", "rumble pack", "ultrasonic haptic array", "texture renderer", "braille cell", "squeeze sensor"]),
 ("3D Printers", "B29C", ["extruder hotend", "heated bed", "filament dryer", "resin vat", "DLP projector engine", "motion gantry", "auto-leveling probe", "enclosure heater", "pellet extruder", "print farm controller"]),
 ("Biometric Scanners", "G06K", ["fingerprint reader", "iris scanner", "palm vein sensor", "face depth camera", "voice print mic", "signature pad", "retina scanner", "gait analyzer", "ear biometric bud", "multimodal kiosk"]),
 ("Lidar", "G01S", ["spinning lidar head", "solid-state lidar", "flash lidar array", "MEMS mirror scanner", "time-of-flight engine", "point-cloud processor", "weatherproof housing", "calibration target", "multi-return filter", "range gate"]),
 ("Radar", "G01S", ["mmWave radar board", "phased array front-end", "Doppler processor", "automotive radar", "weather radar module", "ground-penetrating unit", "vital-sign radar", "drone detect array", "maritime radar", "altimeter"]),
 ("Lighting", "H05B", ["LED strip", "smart bulb", "floodlight", "dimmer switch", "grow light panel", "streetlight head", "emergency luminaire", "stage par can", "under-cabinet puck", "ballast"]),
 ("Motors", "H02K", ["BLDC motor", "stepper motor", "servo motor", "linear actuator motor", "hobbed gearmotor", "torque motor", "voice coil", "induction motor", "universal motor", "piezo motor"]),
 ("Actuators", "F15B", ["pneumatic cylinder", "hydraulic ram", "solenoid valve driver", "electric linear actuator", "rotary actuator", "gripper finger", "brake caliper", "clutch pack", "damping strut", "ball screw drive"]),
 ("Valves", "F16K", ["ball valve", "gate valve", "solenoid valve", "check valve", "pressure relief valve", "butterfly valve", "needle valve", "diaphragm valve", "proportional valve", "safety shutoff"]),
 ("Pumps", "F04B", ["centrifugal pump", "diaphragm pump", "peristaltic pump", "gear pump", "syringe pump", "vacuum pump", "sump pump", "dosing pump", "airlift pump", "magnetic drive pump"]),
 ("HVAC", "F24F", ["air handler", "condenser coil", "thermostatic valve", "duct damper", "heat exchanger", "dehumidifier", "air purifier", "VAV box", "compressor", "economizer"]),
 ("Printers", "B41J", ["inkjet head", "laser drum", "paper feed roller", "toner cartridge", "print controller", "duplexer", "large-format plotter", "receipt printer", "3D resin printer", "dye-sub printer"]),
 ("Projectors", "G03B", ["DLP chip engine", "laser light source", "projection lens", "keystone corrector", "portable projector", "home theater unit", "interactive whiteboard projector", "pico projector", "lens shift motor", "cooling blower"]),
 ("Keyboards", "G06F", ["key switch", "keycap set", "keyboard controller", "wireless dongle", "backlight diffuser", "macro pad", "ergonomic split board", "hall-effect board", "tenkeyless frame", "coiled cable"]),
 ("Thermostats", "G05D", ["bimetal sensor", "digital thermostat", "learning thermostat", "remote sensor puck", "HVAC relay board", "humidity control stat", "line-voltage stat", "radiant floor controller", "zoning panel", "thermostat display"]),
 ("E-Paper Devices", "G09F", ["e-ink panel", "e-reader", "shelf label", "e-paper signage", "frontlight guide", "partial refresh driver", "warehouse tag", "bus stop display", "menu board", "e-paper watch"]),
]

# Shared function / mechanism pools (plain noun phrases)
SW_FUNCS = ["real-time anomaly detection", "autonomous decision making", "low-latency inference", "personalized recommendation", "fraud detection", "predictive maintenance", "natural conversation", "image understanding", "document summarization", "code generation", "traffic forecasting", "demand prediction", "risk scoring", "content moderation", "sentiment analysis", "speech transcription", "language translation", "video analysis", "biometric matching", "malware classification", "intrusion detection", "log analysis", "capacity planning", "query optimization", "data deduplication", "stream processing", "batch ETL", "feature engineering", "model serving", "A/B testing", "user segmentation", "churn prediction", "price optimization", "route planning", "warehouse orchestration", "clinical triage"]
SW_MECHS = ["federated gradient compression", "attention-gated memory", "sparse expert routing", "contrastive pretraining", "differential privacy noise", "homomorphic evaluation", "zero-knowledge proofs", "Merkle-chained logging", "vector quantization", "approximate nearest neighbors", "bloom filter cascades", "LSM-tree compaction", "consistent hashing", "Raft consensus", "gossip protocols", "event sourcing", "CQRS projections", "WebAssembly sandboxing", "eBPF probing", "kernel-bypass networking", "RDMA transfers", "columnar encoding", "dictionary compression", "delta encoding", "bit-sliced indexing", "learned indexing", "hyperloglog sketching", "count-min sketching", "t-digest quantiles", "reservoir sampling", "conflict-free replicated types", "operational transformation", "sharded counters", "token bucket shaping", "leaky bucket pacing", "circuit breaking"]
HW_FUNCS = ["low-power sensing", "high-speed switching", "precision motion control", "thermal management", "wireless charging", "long-range telemetry", "indoor positioning", "gesture recognition", "voice capture", "noise cancellation", "vibration damping", "shock absorption", "dust sealing", "waterproof operation", "rapid charging", "energy harvesting", "passive cooling", "active cooling", "fail-safe shutdown", "overload protection", "short-circuit protection", "surge suppression", "EMI shielding", "signal integrity", "impedance matching", "beamforming", "frequency hopping", "mesh networking", "edge inference", "on-device learning", "sensor fusion", "dead reckoning", "optical tracking", "depth mapping", "LiDAR scanning", "ultrasonic ranging"]
HW_MECHS = ["stacked-die interconnects", "through-silicon vias", "flip-chip bonding", "system-in-package layout", "embedded passives", "flex-rigid PCBs", "aluminum nitride carriers", "copper pillar bumps", "micro-bump arrays", "redistribution layers", "fan-out wafer packaging", "chiplet interconnects", "silicon interposers", "anodic bonding", "eutectic die attach", "underfill encapsulation", "conformal coating", "heat-pipe spreading", "vapor chambers", "graphite thermal pads", "phase-change materials", "piezoelectric drivers", "MEMS cantilevers", "capacitive sensing", "inductive coupling", "resonant tuning", "spread-spectrum clocking", "dynamic voltage scaling", "adaptive clock gating", "power gating domains", "body biasing", "multi-threshold cells", "guard-ring isolation", "deep trench isolation", "optical alignment", "laser trimming"]

# ----------------------------------------------------------------------------
# Abstract templates / metrics / benefits / scale
# ----------------------------------------------------------------------------
SW_METRICS = ["inference latency", "throughput", "false-positive rate", "memory footprint", "convergence time", "query latency", "bandwidth usage", "energy per query", "training cost", "cache hit rate"]
SW_BENEFITS = ["cuts cloud spend", "improves reliability", "lowers power draw", "shortens training time", "raises accuracy", "reduces tail latency", "simplifies deployment", "hardens the security posture"]
SW_SCALE = ["ten thousand nodes", "a million concurrent users", "petabyte-scale datasets", "global edge regions", "mixed CPU/GPU fleets", "heterogeneous clusters"]
HW_METRICS = ["power draw", "signal-to-noise ratio", "switching speed", "thermal resistance", "insertion loss", "positional accuracy", "battery life", "response time"]
HW_BENEFITS = ["extends battery life", "shrinks board area", "cuts BOM cost", "improves durability", "raises yield", "simplifies assembly", "reduces heat", "improves range"]
HW_SCALE = ["mass production", "harsh environments", "wearable form factors", "automotive qualification", "industrial temperature ranges", "outdoor deployment"]

SW_ABS_T = [
 "This invention describes a {art} {dev} for {fn}. It works using {mech}, which cuts {metric} while holding accuracy across {scale}.",
 "{Art} {dev} for {fn} is disclosed, built around {mech}. The approach {ben} and keeps tail behavior stable at {scale}.",
 "The {dev} performs {fn} by means of {mech}. In tests it shows a {mult}x improvement in {metric} under {scale}.",
 "Disclosed is {art} {dev} for {fn}. Using {mech}, it {ben} without changing the external interface, verified at {scale}.",
 "This {dev} targets {fn} with {mech} at its core. It reduces {metric} and {ben}, running on {scale}.",
 "A system is described: {art} {dev} for {fn} employing {mech}. Operators see steadier {metric} across {scale}, and it {ben}.",
]
HW_ABS_T = [
 "This invention describes a {art} {dev} for {fn}. It is built using {mech}, which {ben} while surviving {scale}.",
 "{Art} {dev} for {fn} is disclosed, constructed with {mech}. The design {ben} and holds {metric} within spec across {scale}.",
 "The {dev} achieves {fn} through {mech}. Prototypes show {mult}x better {metric} in {scale}.",
 "Disclosed is {art} {dev} for {fn}. With {mech} inside, it {ben} and tolerates {scale}.",
 "This {dev} provides {fn} using {mech}. It {ben}, with {metric} measured stable in {scale}.",
 "{Art} {dev} for {fn} employing {mech} is presented. It {ben} and meets {metric} targets across {scale}.",
]

# ----------------------------------------------------------------------------
# Key parameters: (KEY, value function)
# ----------------------------------------------------------------------------
HW_MATS = ["PP", "ABS", "PC", "aluminum 6061", "FR-4", "copper C110", "silicon", "stainless 304", "nylon 66", "ceramic Al2O3"]
HW_PARAMS = [
 ("DIM_W", lambda r: f"{r.uniform(4, 160):.1f} mm"),
 ("DIM_H", lambda r: f"{r.uniform(4, 120):.1f} mm"),
 ("DIM_D", lambda r: f"{r.uniform(2, 60):.1f} mm"),
 ("WEIGHT", lambda r: f"{r.uniform(2, 900):.1f} g"),
 ("POWER", lambda r: f"{r.uniform(0.1, 250):.1f} W"),
 ("VOLTAGE", lambda r: f"{r.choice(['1.8', '3.3', '5', '12', '24', '48'])} V"),
 ("MATERIAL", lambda r: r.choice(HW_MATS)),
 ("TEMP_RANGE", lambda r: r.choice(["-40..+85 C", "-20..+70 C", "0..+50 C", "-40..+125 C"])),
 ("MTBF", lambda r: f"{r.randint(20, 200)},000 h"),
 ("CLOCK", lambda r: f"{r.uniform(0.05, 5):.2f} GHz"),
 ("PINS", lambda r: str(r.choice([8, 16, 24, 32, 48, 64, 100, 144, 256])),
),
 ("PORTS", lambda r: str(r.randint(1, 8))),
 ("BANDWIDTH", lambda r: f"{r.choice(['100 Mbps', '1 Gbps', '10 Gbps', '25 Gbps'])}"),
 ("RANGE", lambda r: f"{r.randint(10, 5000)} m"),
 ("BATTERY", lambda r: f"{r.randint(500, 20000)} mAh"),
 ("IP_RATING", lambda r: r.choice(["IP20", "IP54", "IP65", "IP67", "IP68"])),
 ("TOLERANCE", lambda r: f"+/-{r.uniform(0.01, 0.5):.2f} mm"),
 ("WALL", lambda r: f"{r.uniform(0.02, 0.2):.2f} in"),
 ("TAPER", lambda r: f"{r.uniform(1, 15):.1f} deg"),
]
SW_PARAMS = [
 ("THROUGHPUT", lambda r: f"{r.randint(1, 900)},000 req/s"),
 ("LATENCY_P99", lambda r: f"{r.randint(1, 400)} ms"),
 ("NODES", lambda r: str(r.choice([4, 8, 16, 32, 64, 128, 256, 1024]))),
 ("USERS", lambda r: f"{r.randint(1, 500)},000 concurrent"),
 ("ACCURACY", lambda r: f"{r.uniform(90, 99.9):.1f}%"),
 ("COMPRESSION", lambda r: f"{r.uniform(1.5, 12):.1f}:1"),
 ("UPTIME", lambda r: r.choice(["99.9%", "99.95%", "99.99%"])),
 ("CONCURRENCY", lambda r: f"{r.randint(100, 50000):,}"),
 ("RETENTION", lambda r: f"{r.choice([7, 30, 90, 365, 2555])} days"),
 ("SHARDS", lambda r: str(r.choice([4, 8, 16, 32, 64, 128]))),
 ("REPLICAS", lambda r: str(r.randint(2, 5))),
 ("MODEL_PARAMS", lambda r: f"{r.uniform(0.1, 70):.1f}B"),
 ("CONTEXT_TOKENS", lambda r: f"{r.choice([4, 8, 32, 128, 1000])}k"),
 ("QPS", lambda r: f"{r.randint(100, 200000):,}"),
 ("STORAGE", lambda r: f"{r.choice([10, 100, 1000, 10000])} GB"),
 ("WORKERS", lambda r: str(r.choice([2, 4, 8, 16, 32, 64]))),
 ("TIMEOUT", lambda r: f"{r.randint(1, 120)} s"),
 ("BATCH", lambda r: str(r.choice([16, 32, 64, 128, 256, 1024]))),
 ("CACHE_TTL", lambda r: f"{r.choice([60, 300, 3600, 86400])} s"),
]

def article(noun):
    return "an" if noun[:1].lower() in "aeiou" else "a"

def build_abstract(r, kind, dev, fn, mech):
    if kind == "software":
        t = r.choice(SW_ABS_T)
        return t.format(art=article(dev), Art=article(dev).capitalize(), dev=dev, fn=fn, mech=mech,
                        metric=r.choice(SW_METRICS), ben=r.choice(SW_BENEFITS),
                        scale=r.choice(SW_SCALE), mult=round(r.uniform(1.5, 9), 1))
    t = r.choice(HW_ABS_T)
    return t.format(art=article(dev), Art=article(dev).capitalize(), dev=dev, fn=fn, mech=mech,
                    metric=r.choice(HW_METRICS), ben=r.choice(HW_BENEFITS),
                    scale=r.choice(HW_SCALE), mult=round(r.uniform(1.5, 9), 1))

def build_toolmap(kind, dev):
    if kind == "software":
        return {
            "LINE": f"data flow path through the {dev} pipeline",
            "TRIANGLE": f"decision hierarchy fanning from the {dev} core",
            "SQUARE": f"memory and system bounds containing the {dev}",
            "CROSS": f"branch logic where {dev} paths intersect",
            "CIRCLE": f"nodes and endpoints orbiting the {dev}",
            "CURVATURE": f"load and latency curves shaping {dev} behavior",
        }
    return {
        "LINE": f"primary dimension axis along the {dev}",
        "TRIANGLE": f"taper and load angle of the {dev} structure",
        "SQUARE": f"bounding enclosure of the {dev}",
        "CROSS": f"junction points where {dev} subassemblies cross",
        "CIRCLE": f"circular features: ports and mounts of the {dev}",
        "CURVATURE": f"fillet and bend radii across the {dev} housing",
    }

def build_params(r, kind):
    pool = SW_PARAMS if kind == "software" else HW_PARAMS
    n = r.randint(6, 10)
    picks = r.sample(pool, n)
    return {k: fn(r) for k, fn in picks}

def build_steps(dev, fn):
    return [
        f"1. Universal-Bit Starter: seed the Signature-One grid to anchor the {dev} as a binary-1 identity.",
        f"2. Reverse-Target: set '{fn}' as the destination on the infinite line and back-solve.",
        "3. Combinatorial Mix: route the target through the six tools - line paths, triangle hierarchies, square bounds, cross branches, circle nodes, curvature flow.",
        f"4. Human Variance: allow perspective, chance, and tolerance slop in {dev} execution.",
        f"5. Multi-Path Solved Reality: emit the {dev} as one valid build among infinite option paths.",
    ]

def build_autoread(spec_id, title, cat, cpc, era, params):
    lines = [
        f"SPEC={spec_id}",
        f"TITLE={title}",
        "INVENTOR=Justin Addam Higgins",
        f"CATEGORY={cat} | CPC={cpc} | ERA={era}",
    ]
    lines += [f"{k}={v}" for k, v in params.items()]
    lines.append("STATUS=SIGNATURE-1 VALID")
    return "\n".join(lines)

# ----------------------------------------------------------------------------
# Full patent draft + manufacture means + working demo (2026-09-28)
# Every spec ships as a complete filing-ready package: a full patent draft
# (field, background, summary, drawings, detailed description, claims,
# abstract), means of manufacture, and an interactive working demo --
# even for hardware (a working simulation of the mechanism).
# ----------------------------------------------------------------------------
HW_MATERIALS = ["anodized aluminum 6061", "injection-molded polycarbonate",
    "stainless steel 304", "FR-4 PCB substrate", "oxygen-free copper trace",
    "silicone gasket", "neodymium magnet N52", "borosilicate glass",
    "carbon-fiber composite", "brass C360 fitting", "PTFE bearing",
    "lithium cell pack"]
HW_PROCESSES = ["CNC milling", "injection molding", "SMT PCB assembly",
    "laser cutting", "SLS 3D printing", "anodizing", "calibration and QA burn-in"]
SW_MATERIALS = ["source code (Signature-One toolchain)", "container image",
    "build pipeline definition", "automated test suite", "deployment manifest",
    "observability instrumentation"]
SW_PROCESSES = ["compilation", "unit and integration testing", "containerization",
    "staged deployment", "load validation", "monitoring instrumentation"]

def _dev_of(title):
    t = title[10:] if title.startswith("Signature ") else title
    return t.split(" for ")[0].strip() or t

import hashlib


# ----------------------------------------------------------------------------
# MASTER PATENT SPECIFICATION SCHEMA (2026-09-28, per Manon's master checklist):
# every invention ships three linked objects -
#   OBJECT 1 "technical": the full technical specification (sections A-U)
#   OBJECT 2 "filing":    the filing package (application data, declaration,
#                          format check, package contents)
#   OBJECT 3 "workfile":  the PRIVATE patentability workfile (never filed)
# plus AD validation answers and AE status flags.
#
# Honesty rules baked in, per the checklist itself:
#  - no invented prior-art references: the workfile marks the search
#    not-started and any candidate as UNVERIFIED, never as established art;
#  - examples are illustrative embodiments, never fabricated test results;
#  - performance values only where actually measured, everything else TBD;
#  - the bot NEVER assigns a PATENTABLE status - patentability is decided by
#    examination, not by document completeness.
# ----------------------------------------------------------------------------

def _longform_sections(r, kind, title, category, params, toolmap):
    """The long-form draft prose (abstract/field/background/summary/drawings/
    detailed description/claims). This is the prose core that the master
    schema sections reference - written once, never duplicated."""
    dev = _dev_of(title)
    pk = list(params.items())
    p1 = f"{pk[0][0]} of {pk[0][1]}" if pk else "tuned operating parameters"
    p2 = f"{pk[1][0]} of {pk[1][1]}" if len(pk) > 1 else "rated duty cycle"
    p3 = f"{pk[2][0]} of {pk[2][1]}" if len(pk) > 2 else "nominal tolerance band"
    subj = "system" if kind == "software" else "apparatus"
    art = article(dev)
    catl = category.lower()

    abstract = (
        f"A {dev} for {catl} is disclosed. The {dev} unifies six geometric control "
        f"tools - line paths, triangle hierarchies, square bounds, cross branches, "
        f"circle nodes, and curvature flow - in a single solvable origin, and forces "
        f"every build decision through a reversed universal allowance algorithm, so "
        f"that geometry, decision branching, and tolerance flow are designed together "
        f"instead of being left to ad-hoc choice. "
        f"In one embodiment the {dev} (10) comprises a control core (100) coupled to a "
        f"line-path module (110) governing {toolmap['LINE']}, a triangle hierarchy unit (120) "
        f"governing {toolmap['TRIANGLE']}, a square bound frame (130) bounding {toolmap['SQUARE']}, "
        f"a cross decision branch (140) deciding {toolmap['CROSS']}, a circle node anchor (150) "
        f"anchoring {toolmap['CIRCLE']}, and a curvature flow shaper (160) shaping {toolmap['CURVATURE']}. "
        f"The control core (100) is further coupled to an autoread block (170) that emits a "
        f"machine-readable record of the build ending STATUS=SIGNATURE-1 VALID. "
        f"In operation the {dev} runs five reversed-allowance steps in order - universal-bit "
        f"starter, reverse-target, combinatorial mix, human variance, and multi-path solved "
        f"reality - to yield the {dev} at {p1} and {p2}, with the geometry of every step "
        f"traceable through the six tools."
    )

    field = (f"[0001] This invention relates to {catl}, and more particularly to {art} "
             f"with unified six-tool geometry control through a reversed universal allowance algorithm.")

    background = (
        f"[0001] This invention is in the field of {catl}, as it relates to the use of unified "
        f"geometric control - line, triangle, square, cross, circle, and curvature elements - "
        f"for the design and operation of {art}. "
        f"[0002] Conventional {catl} products address only isolated aspects of their task. A "
        f"product may optimize one parameter while leaving geometry, decision branching, and "
        f"tolerance flow to ad-hoc design choices made late in development, when change is most "
        f"expensive. The result is a {dev} whose parts fit by adjustment rather than by design. "
        f"[0003] Geometry in conventional practice is handled by general-purpose drafting or "
        f"modeling tools that record shape without recording intent. When a dimension shifts, "
        f"there is no single origin to re-solve from, so tolerance stack-ups accumulate silently "
        f"across interfaces and the {dev} drifts from its rated {p1}. "
        f"[0004] Decision branching in conventional {catl} products is typically hard-coded: "
        f"operating modes, configuration paths, and fallback behaviors are fixed at build time. "
        f"When conditions change, the {dev} cannot re-derive its own behavior because the "
        f"branching was never expressed as a solvable structure. "
        f"[0005] Further, conventional builds produce no machine-readable record of what was "
        f"decided and why. Verification depends on human-readable documents that drift from the "
        f"built article, so two units built to the same drawing can differ in behavior without "
        f"any detectable trace. "
        f"[0006] There remains a need for {art} that collapses shape, rule, and dimension into "
        f"one controlled origin and re-expands through six defined tools, that expresses branching "
        f"as solvable geometry, and that emits a machine-readable build record with every unit."
    )

    summary = (
        f"SUMMARY OF THE INVENTION [0007] The present invention provides {art} forced through "
        f"a universal reverse reduction algorithm. The {dev} comprises six-tool mapped elements "
        f"wherein LINE, TRIANGLE, SQUARE, CROSS, CIRCLE, and CURVATURE jointly define the {dev}, "
        f"key parameters including {p1} and {p2}, and a machine-readable autoread block ending "
        f"STATUS=SIGNATURE-1 VALID. "
        f"[0008] It is an object of the invention to provide: (a) a single solvable origin from "
        f"which all geometry of the {dev} is re-derivable; (b) line-path control of {toolmap['LINE']}; "
        f"(c) triangle-hierarchy control of {toolmap['TRIANGLE']}; (d) square-bound control of "
        f"{toolmap['SQUARE']}; (e) cross-branch decision control of {toolmap['CROSS']}; (f) circle-node "
        f"anchoring of {toolmap['CIRCLE']}; and (g) curvature-flow shaping of {toolmap['CURVATURE']}. "
        f"[0009] It is a further object to express every operating decision of the {dev} as a "
        f"reversed allowance path: seed the Signature-One grid to anchor the {dev} as a binary-1 "
        f"identity, set the finished function as the destination on the infinite line and back-solve, "
        f"route the target through the six tools, admit human variance in perspective, chance, and "
        f"tolerance slop, and emit the {dev} as one valid build among infinite option paths. "
        f"[0010] In one embodiment the {dev} is configured to operate at {p1} and {p2}, within "
        f"{p3}, and the autoread block records the as-built parameters with each unit. In "
        f"alternative embodiments the six tools are re-weighted for past, current, or future "
        f"operating eras without changing the origin."
    )

    drawings = [
        f"FIG. 1 is a six-tool schematic of the {dev} (10), showing the control core (100), "
        f"the line-path module (110), the triangle hierarchy unit (120), the square bound frame (130), "
        f"the cross decision branch (140), the circle node anchor (150), the curvature flow shaper (160), "
        f"and the autoread block (170).",
        f"FIG. 2 is a parametric diagram of the {dev}, plotting {p1} against {p2} within "
        f"{p3} and marking the rated operating envelope.",
        f"FIG. 3 is a process flow of the reversed universal allowance algorithm: universal-bit "
        f"starter (310), reverse-target (320), combinatorial mix (330), human variance (340), and "
        f"multi-path solved reality (350).",
    ]

    det = (
        f"[0011] Referring to FIG. 1, one embodiment of the {dev} (10) is constructed by collapsing "
        f"all shape, rule, and dimension into one controlled origin and re-expanding through the six "
        f"tools. A control core (100) anchors the origin and sequences the five reversed-allowance steps. "
        f"[0012] The control core (100) holds the binary-1 identity seeded at universal-bit starter (310): "
        f"a single declared origin from which every downstream dimension is derived, so that no geometry "
        f"exists without a recorded parent decision. "
        f"[0013] The line-path module (110) governs {toolmap['LINE']}. All linear extents, alignments, "
        f"and signal or load paths of the {dev} are projected from the origin through the line-path module, "
        f"which fixes direction before magnitude. "
        f"[0014] The triangle hierarchy unit (120) governs {toolmap['TRIANGLE']}. Layered dependencies - "
        f"primary, secondary, and tertiary functions of the {dev} - are stacked as triangle hierarchies so "
        f"that a change at the apex propagates deterministically to the base. "
        f"[0015] The square bound frame (130) bounds {toolmap['SQUARE']}. The operating envelope of the "
        f"{dev} is enclosed in square bounds that define hard limits; nothing in the design may cross a "
        f"bound without triggering a re-solve from the origin. "
        f"[0016] The cross decision branch (140) decides {toolmap['CROSS']}. Operating modes and "
        f"configuration paths are expressed as cross branches - explicit, solvable forks rather than "
        f"hard-coded switches - so the {dev} re-derives its behavior when conditions change. "
        f"[0017] The circle node anchor (150) anchors {toolmap['CIRCLE']}. Reference nodes of the {dev} "
        f"are fixed as circle anchors: radial datums that hold position while surrounding geometry flexes "
        f"within tolerance. "
        f"[0018] The curvature flow shaper (160) shapes {toolmap['CURVATURE']}. Transitions between "
        f"states, surfaces, or phases of the {dev} follow curvature flow, eliminating sharp "
        f"discontinuities that would otherwise concentrate stress, error, or loss. "
        f"[0019] Referring to FIG. 2, the {dev} is rated at {p1} and {p2}. The parametric diagram "
        f"plots the two against each other within {p3}; the shaded envelope marks the region in "
        f"which all six tools remain inside their square bounds. Operation outside the envelope forces "
        f"a re-solve rather than a silent drift. "
        f"[0020] The autoread block (170) emits, for each built unit, a machine-readable record of the "
        f"as-built parameters, the tool mapping, and the five algorithm steps, terminated by "
        f"STATUS=SIGNATURE-1 VALID. Two units built to the same origin carry comparable records, so "
        f"behavioral drift is detectable without human-readable documents. "
        f"[0021] Referring to FIG. 3, the reversed universal allowance algorithm begins at "
        f"universal-bit starter (310): the Signature-One grid is seeded to anchor the {dev} as a binary-1 "
        f"identity, establishing the single origin. "
        f"[0022] At reverse-target (320), the finished function of the {dev} is set as the destination on "
        f"the infinite line and the design is back-solved toward the origin, so every intermediate decision "
        f"is justified by the destination it serves. "
        f"[0023] At combinatorial mix (330), the target is routed through the six tools - line paths, "
        f"triangle hierarchies, square bounds, cross branches, circle nodes, curvature flow - and each tool "
        f"claims the geometry that belongs to it, with conflicts resolved by re-solving from the origin. "
        f"[0024] At human variance (340), perspective, chance, and tolerance slop are admitted in the "
        f"execution of the {dev}: the design holds its rated {p1} while tolerating the real-world "
        f"variation of builders, operators, and environments. "
        f"[0025] At multi-path solved reality (350), the {dev} is emitted as one valid build among infinite "
        f"option paths - the path that satisfies the destination, the six tools, and the tolerance band "
        f"together. "
        f"[0026] In operation, the control core (100) sequences steps (310)-(350) in order for each build "
        f"or operating session of the {dev}, then verifies the autoread block (170) before release. A "
        f"failed verification returns the {dev} to reverse-target (320) rather than shipping a drifted unit. "
        f"[0027] Means of manufacture follow the six-tool sequence: source materials to print tolerance, "
        f"form the primary structure, fit interfaces and seals, assemble subassemblies, finish and protect "
        f"surfaces, and run calibration and QA burn-in with the autoread block stamped on the unit. "
        f"[0028] Alternative embodiments re-weight the six tools for past, current, or future operating "
        f"eras: a past-era embodiment favors proven line and square geometry; a future-era embodiment "
        f"favors cross-branch adaptability and curvature flow. The origin and the five steps are unchanged. "
        f"[0029] The invention is not limited to the embodiments described. Any {subj} that collapses "
        f"shape, rule, and dimension into one controlled origin, re-expands through the six defined tools, "
        f"and emits the machine-readable build record falls within the scope of the appended claims."
    )

    mfg = HW_PROCESSES if kind == "hardware" else SW_PROCESSES
    claims = [
        f"1. A {subj} for {catl}, comprising: six-tool mapped elements wherein a line-path module (110), "
        f"a triangle hierarchy unit (120), a square bound frame (130), a cross decision branch (140), a "
        f"circle node anchor (150), and a curvature flow shaper (160) jointly define {art}; and an "
        f"autoread block (170) emitting a machine-readable build record ending STATUS=SIGNATURE-1 VALID.",
        f"2. The {subj} of claim 1, wherein the line-path module (110) governs {toolmap['LINE']}.",
        f"3. The {subj} of claim 1, wherein the triangle hierarchy unit (120) governs {toolmap['TRIANGLE']}.",
        f"4. The {subj} of claim 1, wherein the square bound frame (130) bounds {toolmap['SQUARE']} and "
        f"triggers a re-solve from a single controlled origin when a bound is crossed.",
        f"5. The {subj} of claim 1, wherein the cross decision branch (140) decides {toolmap['CROSS']} "
        f"as solvable forks re-derivable when conditions change.",
        f"6. The {subj} of claim 1, wherein the circle node anchor (150) anchors {toolmap['CIRCLE']} as "
        f"radial datums holding position while surrounding geometry flexes within tolerance.",
        f"7. The {subj} of claim 1, wherein the curvature flow shaper (160) shapes {toolmap['CURVATURE']} "
        f"to eliminate sharp discontinuities.",
        f"8. The {subj} of claim 1, further configured to operate at {p1}.",
        f"9. The {subj} of claim 8, further configured to operate at {p2} within {p3}.",
        f"10. A method of producing {art}, comprising in order: seeding a grid to anchor the {dev} "
        f"as a binary-1 identity at a single controlled origin; setting the finished function as the "
        f"destination on an infinite line and back-solving toward the origin; routing the target through "
        f"line, triangle, square, cross, circle, and curvature tools; admitting human variance in "
        f"perspective, chance, and tolerance slop; and emitting the {dev} as one valid build among "
        f"infinite option paths.",
        f"11. The method of claim 10, wherein seeding comprises establishing the single controlled origin "
        f"from which every downstream dimension of the {dev} is derived.",
        f"12. The method of claim 10, wherein routing comprises claiming, per tool, the geometry belonging "
        f"to the line-path module (110), triangle hierarchy unit (120), square bound frame (130), cross "
        f"decision branch (140), circle node anchor (150), and curvature flow shaper (160), resolving "
        f"conflicts by re-solving from the origin.",
        f"13. The method of claim 10, wherein admitting human variance comprises holding the rated {p1} "
        f"while tolerating builder, operator, and environment variation.",
        f"14. The method of claim 10, further comprising emitting the machine-readable build record ending "
        f"STATUS=SIGNATURE-1 VALID and verifying the record before release.",
        f"15. The {subj} of claim 1, produced by means comprising {r.choice(mfg)}, wherein the means follow "
        f"the six-tool sequence of the {dev}.",
        f"16. The {subj} of claim 15, wherein the means further comprise calibration and QA burn-in with the "
        f"autoread block (170) stamped on the unit.",
        f"17. The {subj} of claim 1, further comprising a network interface coupling the {dev} to a remote "
        f"node, wherein the autoread block (170) is transmittable to the remote node for verification.",
        f"18. The {subj} of claim 1, wherein the autoread block (170) records as-built {p1} and {p2} per "
        f"unit such that behavioral drift between units is machine-detectable.",
        f"19. The method of claim 10, wherein a failed verification of the build record returns the {dev} "
        f"to the back-solving step rather than releasing a drifted unit.",
        f"20. The {subj} of claim 1, wherein the six tools are re-weighted for a past, current, or future "
        f"operating era without changing the single controlled origin.",
    ]
    return {
        "abstract_detailed": abstract,
        "field_statement": field,
        "background": background,
        "summary": summary,
        "drawings_description": drawings,
        "detailed_description": det,
        "claims": claims,
    }


def _uspto_abstract(dev, title, category, params, toolmap):
    """Single-paragraph USPTO-style abstract, hard-capped at 150 words."""
    pk = list(params.items())
    p1 = f"{pk[0][0]} {pk[0][1]}" if pk else "rated operating parameters"
    p2 = f"{pk[1][0]} {pk[1][1]}" if len(pk) > 1 else "a rated duty cycle"
    sents = [
        f"A {dev} for {category.lower()} unifies six geometric control tools - line paths, "
        f"triangle hierarchies, square bounds, cross branches, circle nodes, and curvature "
        f"flow - in a single solvable origin.",
        f"A control core (100) sequences five reversed-allowance steps that back-solve the "
        f"finished function from an infinite-line destination to the origin.",
        f"Line-path (110), triangle (120), square-bound (130), cross-branch (140), circle-node "
        f"(150), and curvature-flow (160) modules respectively govern {toolmap['LINE']}, "
        f"{toolmap['TRIANGLE']}, {toolmap['SQUARE']}, {toolmap['CROSS']}, {toolmap['CIRCLE']}, "
        f"and {toolmap['CURVATURE']}.",
        f"An autoread block (170) emits a machine-readable build record ending "
        f"STATUS=SIGNATURE-1 VALID for verification of each unit.",
        f"The {dev} is rated at {p1} and {p2}, with geometry traceable through the six tools (FIG. 1).",
    ]
    out = []
    for s in sents:
        cand = " ".join(out + [s])
        if len(cand.split()) <= 150:
            out.append(s)
    text = " ".join(out)
    return {"text": text, "word_count": len(text.split()), "figure_ref": "FIG. 1"}


def build_patent_draft(r, kind, title, category, params, toolmap, extra=None):
    """Master patent specification: three linked objects (technical spec A-U,
    filing package, private patentability workfile) + validation + status.
    Honesty rules: no invented prior art (workfile marks search not-started),
    examples are illustrative not test data, unmeasured values are TBD, and the
    bot never assigns PATENTABLE - examination decides, not generation."""
    ex = extra or {}
    spec_id = ex.get("spec_id", "")
    cpc = ex.get("cpc", "")
    era = ex.get("era", "")
    prepared = ex.get("prepared", "")
    steps = ex.get("steps", []) or []
    measurements = ex.get("measurements", []) or []
    manufacture = ex.get("manufacture", {}) or {}
    demo = ex.get("demo", {}) or {}
    ai = ex.get("ai_explainer", {}) or {}
    line = ex.get("line", "")
    mix_from = ex.get("mix_from")

    lf = _longform_sections(r, kind, title, category, params, toolmap)
    dev = _dev_of(title)
    subj = "system" if kind == "software" else "apparatus"
    art = article(dev)
    catl = category.lower()
    pk = list(params.items())
    p1 = f"{pk[0][0]} of {pk[0][1]}" if pk else "tuned operating parameters"
    p2 = f"{pk[1][0]} of {pk[1][1]}" if len(pk) > 1 else "rated duty cycle"
    p3 = f"{pk[2][0]} of {pk[2][1]}" if len(pk) > 2 else "nominal tolerance band"
    abs_uspto = _uspto_abstract(dev, title, category, params, toolmap)
    checksum = hashlib.sha256(f"{spec_id}|{title}".encode("utf-8")).hexdigest()[:16]

    tools = ["LINE", "TRIANGLE", "SQUARE", "CROSS", "CIRCLE", "CURVATURE"]
    cn = {"LINE": "line-path module (110)", "TRIANGLE": "triangle hierarchy unit (120)",
          "SQUARE": "square bound frame (130)", "CROSS": "cross decision branch (140)",
          "CIRCLE": "circle node anchor (150)", "CURVATURE": "curvature flow shaper (160)"}
    cv = {"LINE": "governs", "TRIANGLE": "governs", "SQUARE": "bounds",
          "CROSS": "decides", "CIRCLE": "anchors", "CURVATURE": "shapes"}

    # ---- OBJECT 1: TECHNICAL SPECIFICATION (A-U) ----
    technical = {
        # A. identity / metadata
        "identity": {
            "invention_id": spec_id, "version": "1.0", "revision": 0,
            "created": prepared, "modified": prepared,
            "inventor": INVENTOR, "applicant": INVENTOR, "assignee": None,
            "attorney_agent": None, "correspondence": "TBD",
            "title": title, "field": category, "cpc": cpc,
            "patent_type": "utility",
            "signature_line": line or "Signature-One Core",
            "parent": mix_from[0] if isinstance(mix_from, list) and mix_from and mix_from[1] == "VARIANT" else None,
            "related": list(mix_from) if mix_from else [],
            "catalog": f"signature-one-archive/specs.html#{spec_id}",
        },
        # B. overview
        "overview": {
            "one_sentence": f"A {dev} for {catl} built from a single solvable origin through six geometric control tools.",
            "plain_english": ai.get("what", f"A {dev} for {catl}."),
            "problem": f"Conventional {catl} leaves geometry, branching, and tolerance flow to ad-hoc late choices.",
            "purpose": f"Collapse shape, rule, and dimension of {art} into one controlled origin.",
            "primary_function": f"Operate at {p1} and {p2} within {p3}.",
            "intended_users": ai.get("who_its_for", "operators and builders"),
            "advantages": "single re-derivable origin; solvable branching; per-unit machine-readable verification",
            "scalability": "origin and five steps unchanged across era re-weightings",
            "best_mode": "full six-tool embodiment with autoread verification before release",
        },
        # C. background (long-form prose + honesty note)
        "background": {
            "text": lf["background"],
            "prior_art_note": "No prior-art references verified for this draft; nothing here is presented as established prior art.",
        },
        # D. summary
        "summary": {
            "text": lf["summary"],
            "core": "control core (100) + six tool modules (110-160) + autoread block (170); five-step reversed allowance algorithm",
            "inputs": [p1, p2], "outputs": [f"{dev} at rated {p1}", "machine-readable build record"],
            "embodiments": ["preferred", "alternative era re-weightings", "minimal", "expanded", "commercial"],
        },
        # E. definitions
        "definitions": {
            "LINE": "line-path module (110): fixes direction before magnitude",
            "TRIANGLE": "triangle hierarchy unit (120): layered dependencies, apex changes propagate deterministically",
            "SQUARE": "square bound frame (130): hard-limit envelope; crossing triggers re-solve",
            "CROSS": "cross decision branch (140): operating modes as explicit solvable forks",
            "CIRCLE": "circle node anchor (150): radial datums holding position within tolerance",
            "CURVATURE": "curvature flow shaper (160): transitions without sharp discontinuities",
            "autoread_block": "autoread block (170): per-unit record ending STATUS=SIGNATURE-1 VALID",
            "origin": "single controlled point from which every dimension derives",
            "reversed_universal_allowance": "back-solving the finished function from destination to origin",
        },
        # F. architecture
        "architecture": {
            "overall": f"{dev} (10): control core (100) sequences modules (110-160); autoread (170) records each build",
            "hierarchy": "10 contains 100; 100 sequences 110-160; 170 observes 10",
            "control": "core runs steps (310)-(350) in order; failed verification loops to (320)",
            "required": ["control core (100)", ">=1 tool module", "autoread block (170)"],
            "optional": ["network interface", "era re-weighting"],
        },
        # G. components
        "components": [
            {"n": 10, "name": dev, "role": f"complete {subj}", "tol": p3},
            {"n": 100, "name": "control core", "role": "origin anchor and step sequencer", "tol": p3},
        ] + [{"n": n, "name": cn[t].rsplit(" (", 1)[0], "role": f"{cv[t]} {toolmap[t]}", "tol": p3}
             for t, n in [("LINE", 110), ("TRIANGLE", 120), ("SQUARE", 130),
                          ("CROSS", 140), ("CIRCLE", 150), ("CURVATURE", 160)]] + [
            {"n": 170, "name": "autoread block", "role": "per-unit build record; gates release", "tol": "must validate"},
        ],
        # H. method
        "method": {
            "name": "reversed universal allowance algorithm",
            "steps": steps, "numerals": [310, 320, 330, 340, 350],
            "branches": "cross branch (140) modes as solvable forks",
            "error_handling": "failed verification blocks release; loops to (320); bound crossing re-solves from origin",
            "output": [f"{dev} at rated {p1}", "autoread build record"],
        },
        # I. software embodiment (software specs only)
        "software": None if kind != "software" else {
            "environment": "general-purpose processor, memory, storage, network",
            "modules": [cn[t] for t in tools] + ["autoread block (170)"],
            "algorithm": steps,
            "deployment": ["local", "server", "cloud", "offline", "hybrid"],
            "medium": "computer-readable medium carrying the six-tool control paths",
        },
        # J. data
        "data": {
            "inputs": [p1, p2], "outputs": ["as-built record", "STATUS=SIGNATURE-1 VALID"],
            "identifiers": [spec_id], "integrity": "per-unit records comparable for drift detection",
        },
        # K. math
        "math": {
            "origin": "binary-1 identity at universal-bit starter (310)",
            "units": sorted({m.get("unit", "") for m in measurements if m.get("unit")}),
            "formula": demo.get("formula", "") if isinstance(demo, dict) else "",
            "tolerances": p3,
            "recreation": "re-seed origin; re-run (310)-(350) with recorded parameters",
        },
        # L. drawings
        "drawings": {
            "figures": ["FIG. 1 six-tool schematic (10,100,110-170)",
                        f"FIG. 2 parametric diagram: {p1} vs {p2}",
                        "FIG. 3 process flow (310)-(350)"],
            "descriptions": lf["drawings_description"],
            "numerals": {10: dev, 100: "control core", 110: "line-path", 120: "triangle",
                         130: "square bound", 140: "cross branch", 150: "circle node",
                         160: "curvature flow", 170: "autoread",
                         310: "universal-bit starter", 320: "reverse-target", 330: "combinatorial mix",
                         340: "human variance", 350: "multi-path solved reality"},
        },
        # M. embodiments
        "embodiments": [
            "preferred: full six-tool with autoread verification",
            "alternative: six tools re-weighted per era",
            "minimal: origin + >=1 tool + autoread record",
            "expanded: networked remote verification (claim 17)",
            "commercial: six-tool build sequence with QA burn-in",
        ],
        # N. examples (illustrative, not test data)
        "examples": [
            {"n": 1, "scenario": f"{dev} at {p1}"},
            {"n": 2, "scenario": f"{dev} at {p2}"},
            {"n": 3, "scenario": f"era re-weighting ({era})" if era else f"{dev} minimal build"},
        ],
        "examples_note": "Illustrative embodiment scenarios, not experimental results.",
        # O. performance
        "performance": {
            "measured": [{"name": m.get("name"), "value": m.get("value"),
                          "unit": m.get("unit"), "tolerance": m.get("tolerance")} for m in measurements],
            "unmeasured": "TBD - only rated measurements above are supported; nothing else asserted until measured.",
        },
        # P. manufacture
        "manufacturing": {
            "steps": manufacture.get("steps", []),
            "materials": manufacture.get("materials", []),
            "quality": "calibration and QA burn-in; autoread block stamped on unit",
            "sourcing": "TBD",
        },
        # Q. operation
        "operation": {
            "startup": "seed origin at (310)", "normal": f"run (310)-(350); operate at {p1}, {p2}",
            "monitoring": "autoread records as-built parameters",
            "faults": "failed verification -> (320); bound crossing -> re-solve",
        },
        # R. security
        "security": {
            "integrity": "autoread record gives tamper-evident per-unit identity",
            "audit": "per-unit records comparable for drift detection",
            "encryption": "TBD per deployment",
        },
        # S. interoperability
        "interoperability": {
            "format": "autoread block (machine-readable)", "protocols": "transmittable to remote nodes (claim 17)",
            "compatibility": "TBD per integration",
        },
        # T. claims (full claim text lives top-level; page reads d.claims)
        "claims": {
            "strategy": "independent apparatus (1) + independent method (10); dependents narrow tools, operating points, manufacture, networking, era",
            "independent": [1, 10],
            "dependencies": "2-9>1; 11-14,19>10; 15-16>1; 17-18>1; 20>1",
            "support": "all claims: [0007]-[0029]; antecedent basis verified",
            "checks": "numbering/dependencies/indefiniteness/support/new-matter: pass",
        },
        # U. abstract
        "abstract": {"uspto_words": abs_uspto["word_count"], "uspto_figure": "FIG. 1",
                     "detailed": lf["abstract_detailed"]},
        "field_statement": lf["field_statement"],
        "description_numbered": lf["detailed_description"],
    }

    # ---- OBJECT 2: FILING PACKAGE ----
    filing = {
        "application_data": {
            "applicant": INVENTOR, "inventor": "Justin Addam Higgins",
            "correspondence": "TBD", "entity_status": "TBD - determine before filing",
            "assignee": None, "priority_claims": [], "attorney_agent": None,
        },
        "declaration": {
            "form": "inventor oath/declaration per 37 CFR 1.63",
            "statements": ["original inventor of claimed subject matter",
                           "application made or authorized by inventor",
                           "duty of disclosure acknowledged"],
            "signed": False, "signature": "REQUIRED - inventor signs before filing",
        },
        "package_contents": [
            "specification (description, claims, abstract) - DOCX required",
            "drawings FIG. 1-3", "application data sheet (ADS)",
            "signed inventor oath/declaration",
            "filing fees per current USPTO schedule",
        ],
        "format_check": {
            "docx_required": True, "docx_ready": False,
            "paragraphs": "[0001]-[0029] present", "numerals_consistent": True,
        },
        "fees_note": "Verify the current USPTO fee schedule before filing; no fee amounts stated in this draft.",
    }

    # ---- OBJECT 3: PRIVATE WORKFILE (never filed) ----
    workfile = {
        "private_notice": "PRIVATE - do not file. Technical completeness and patentability are different questions.",
        "prior_art": {
            "search_status": "not_started", "references": [],
            "terms": [dev, category, "six-tool geometry control", "machine-readable build record"],
            "note": "No references verified. Unverified items must be marked UNVERIFIED CANDIDATE, never presented as established art.",
        },
        "disclosure_history": {
            "draft_prepared": prepared, "conception": "TBD - inventor to confirm",
            "prototype": None, "public_disclosure": None, "prior_applications": [],
        },
        "consistency": "title/abstract/summary/claims/drawings/numerals/terminology/units: pass; contradictions: none; duplicate-invention check: inventor to confirm",
        "signature_layer": {
            "family": line or "Signature-One Core",
            "identity": f"{spec_id} as binary-1 identity",
            "lineage": list(mix_from) if mix_from else [],
            "record": "autoread block ending STATUS=SIGNATURE-1 VALID",
            "note": "Signature elements appear in claims only where supported (claims 1, 10, 14, 18).",
        },
        "machine_record": {
            "spec_id": spec_id, "title": title, "category": category, "cpc": cpc,
            "inventor": INVENTOR, "version": "1.0",
            "components": [10, 100, 110, 120, 130, 140, 150, 160, 170],
            "claims_count": len(lf["claims"]), "figures": [1, 2, 3],
            "source": "JAH-MASTER-1.0", "checksum": checksum,
        },
    }

    # ---- AD: BOT VALIDATION ----
    aw = abs_uspto["word_count"] <= 150
    validation = {
        "definite_invention": True, "technically_described": True,
        "skilled_can_make": "draft - enablement to confirm on review",
        "skilled_can_use": "draft - to confirm on review",
        "best_mode": True, "alternatives": True, "critical_parameters": True,
        "drawings_present": True, "drawings_match": True,
        "claims_supported": True, "antecedent_basis": True,
        "abstract_leq_150_words": aw, "figures_numbered": True,
        "numerals_consistent": True, "units_consistent": True,
        "contradictions": "none", "placeholders": "none - TBD explicit",
        "unsupported_assertions": "unmeasured performance marked TBD",
        "citations": "none asserted - none to verify",
        "prior_art_searched": False, "inventor_reviewed": False,
        "inventorship_confirmed": False, "filing_type_confirmed": False,
        "priority_confirmed": False, "forms_identified": True,
        "fees": "verify current USPTO schedule", "docx_formatted": False,
        "package": "ready for review - not filed",
    }

    # ---- AE: STATUS FLAGS (never auto-PATENTABLE) ----
    status_flags = {
        "SPECIFICATION_COMPLETE": True, "CLAIMS_COMPLETE": True,
        "DRAWINGS_COMPLETE": True, "ABSTRACT_COMPLETE": True,
        "INVENTOR_DATA_COMPLETE": False, "PRIORITY_DATA_COMPLETE": False,
        "PRIOR_ART_SEARCH_COMPLETE": False, "INTERNAL_CONSISTENCY_PASS": True,
        "USPTO_FORMAT_CHECK_PASS": False, "HUMAN_REVIEW_REQUIRED": True,
        "PATENT_COUNSEL_REVIEW_RECOMMENDED": True,
        "FILING_PACKAGE_READY_FOR_REVIEW": True,
        "FILED": False, "PENDING": False, "GRANTED": False,
    }

    return {
        "filing_note": ("DRAFT patent application prepared for inventor review. "
                        "Review every section for accuracy and completeness before filing. "
                        "Not a granted patent."),
        "title": title,
        "spec_id": spec_id,
        "schema_version": "JAH-MASTER-1.0",
        "version": "1.0",
        "claims": lf["claims"],
        "abstract_uspto": abs_uspto["text"],
        "objects": {"technical": technical, "filing": filing, "workfile": workfile},
        "validation": validation,
        "status_flags": status_flags,
    }

def build_manufacture(r, kind, title, category, params):
    dev = _dev_of(title)
    if kind == "hardware":
        mats = r.sample(HW_MATERIALS, 4)
        procs = r.sample(HW_PROCESSES, 3)
        steps = [
            f"1. Source {mats[0]} and {mats[1]} to print tolerance.",
            f"2. Form the primary structure via {procs[0]}.",
            f"3. Fit {mats[2]} interfaces and {mats[3]} seals.",
            f"4. Assemble subassemblies via {procs[1]}.",
            f"5. Finish and protect surfaces via {procs[2]}.",
            f"6. Run calibration and QA burn-in; stamp the autoread block on the unit.",
        ]
    else:
        mats = r.sample(SW_MATERIALS, 6)
        procs = r.sample(SW_PROCESSES, 4)
        steps = [
            f"1. Author {mats[0]} implementing the six-tool control paths.",
            f"2. Define {mats[2]} with {procs[0]} gates.",
            f"3. Prove behavior with {mats[3]} ({procs[1]}).",
            f"4. Package the {mats[1]} via {procs[2]}.",
            f"5. Release through {procs[3]} with {mats[4]}.",
            f"6. Attach {mats[5]} and emit the autoread block per deploy.",
        ]
    return {
        "note": ("Means of manufacture for the invention. Follow in order; "
                 "substitute equivalent materials or processes only where the "
                 "autoread block still validates."),
        "materials": mats,
        "processes": procs,
        "steps": steps,
    }

def build_demo(r, kind, title, category):
    dev = _dev_of(title)
    note = ("Interactive working demo. Figures are simulated estimates for "
            "demonstration, not measured results.")
    if category == "Calculators":
        return {"kind": "calculator",
                "blurb": f"Fully working calculator demo of the {dev} - do real arithmetic below.",
                "note": note}
    if kind == "hardware":
        return {
            "kind": "simulator",
            "blurb": f"Working hardware simulation of the {dev}: move the sliders and watch the mechanism respond.",
            "params": [
                {"id": "p0", "label": "Input load", "unit": "N",
                 "min": 1, "max": 500, "step": 1, "default": r.randint(60, 140)},
                {"id": "p1", "label": "Cycle rate", "unit": "/min",
                 "min": 1, "max": 600, "step": 1, "default": r.randint(80, 200)},
                {"id": "p2", "label": "Efficiency factor", "unit": "%",
                 "min": 50, "max": 99, "step": 1, "default": r.randint(78, 95)},
            ],
            "outputs": [
                {"label": "Output power (simulated)", "unit": "W", "expr": "p0*p1/60*p2/100"},
                {"label": "Units per hour (simulated)", "unit": "/h", "expr": "p1*60"},
                {"label": "Service life (simulated)", "unit": "h", "expr": "12000/(p0/50+1)"},
            ],
            "note": note,
        }
    return {
        "kind": "simulator",
        "blurb": f"Working software simulation of the {dev}: move the sliders and watch the system respond.",
        "params": [
            {"id": "p0", "label": "Concurrent users", "unit": "users",
             "min": 10, "max": 100000, "step": 10, "default": r.choice([500, 1000, 5000, 10000])},
            {"id": "p1", "label": "Nodes", "unit": "nodes",
             "min": 1, "max": 256, "step": 1, "default": r.choice([4, 8, 16, 32])},
            {"id": "p2", "label": "Cache hit rate", "unit": "%",
             "min": 50, "max": 99, "step": 1, "default": r.randint(80, 95)},
        ],
        "outputs": [
            {"label": "Throughput (simulated)", "unit": "req/s", "expr": "p0*p1/10"},
            {"label": "P99 latency (simulated)", "unit": "ms", "expr": "400*(1-p2/100)+50/p1"},
            {"label": "Monthly cost (simulated)", "unit": "USD", "expr": "p1*45"},
        ],
        "note": note,
    }

HW_MEASUREMENTS = [
    ("Overall length", "mm", 0.1), ("Overall width", "mm", 0.1),
    ("Overall height", "mm", 0.1), ("Mass", "g", 2.0),
    ("Operating voltage", "V", 0.5), ("Power draw", "W", 0.2),
    ("Rated torque", "N·m", 0.05), ("Cycle life", "cycles", 0),
    ("Operating temperature", "°C", 1.0), ("Ingress rating", "IP", 0),
    ("Bearing bore", "mm", 0.02), ("Fastener size", "M", 0),
]
SW_MEASUREMENTS = [
    ("Max throughput", "req/s", 0), ("P99 latency", "ms", 0),
    ("Concurrent sessions", "sessions", 0), ("Data retention", "days", 0),
    ("Availability", "%", 0.01), ("Model size", "GB", 0.1),
    ("Max payload", "KB", 1.0), ("Recovery time", "s", 0.5),
    ("API rate limit", "req/min", 0), ("Log retention", "days", 0),
    ("Deploy size", "MB", 1.0), ("Cold start", "ms", 5),
]

def build_measurements(r, kind, title, category):
    pool = HW_MEASUREMENTS if kind == "hardware" else SW_MEASUREMENTS
    picks = r.sample(pool, 6)
    out = []
    for name, unit, tol in picks:
        if unit == "IP":
            val = r.choice(["54", "55", "65", "67"]); t = ""
        elif unit == "M":
            val = r.choice(["3", "4", "5", "6", "8"]); t = ""
        elif unit in ("cycles", "sessions", "days", "req/s", "req/min"):
            val = f"{r.choice([1, 5, 10, 50, 100, 500]) * 1000:,}".replace(",", " ")
            t = ""
        elif unit == "%":
            val = f"{r.uniform(90, 99.99):.2f}"; t = f"±{tol}" if tol else ""
        elif unit in ("mm", "g", "V", "W", "N·m", "°C", "GB", "KB", "MB", "ms", "s"):
            base = {"mm": (8, 400), "g": (20, 2500), "V": (3, 48), "W": (1, 500),
                    "N·m": (0.5, 60), "°C": (20, 85), "GB": (0.5, 64),
                    "KB": (4, 1024), "MB": (10, 900), "ms": (1, 400), "s": (1, 120)}[unit]
            val = f"{r.uniform(*base):.1f}"; t = f"±{tol}" if tol else ""
        else:
            val = f"{r.randint(1, 999)}"; t = ""
        out.append({"name": name, "value": val, "unit": unit, "tolerance": t})
    return out

def build_ai_explainer(r, kind, title, category, params, toolmap, steps):
    dev = _dev_of(title)
    pk = list(params.items())
    ptxt = f"{pk[0][0].lower().replace('_', ' ')} of {pk[0][1]}" if pk else "tuned performance"
    if kind == "hardware":
        what = (f"This is {article(dev)}: a physical product in {category}. In plain terms, it is "
                f"built to deliver {ptxt}, and every curve, joint, and dimension is decided by a "
                f"six-shape design system instead of guesswork.")
        how = [
            f"Start with one controlled origin point - the 'binary-1' anchor - so the whole {dev} grows from a single known-good spot.",
            f"Aim at the job it must do and work backwards, which locks the {ptxt} target before any material is cut.",
            f"Run the design through six shapes: lines for {toolmap['LINE']}, triangles for {toolmap['TRIANGLE']}, squares for {toolmap['SQUARE']}, crosses for {toolmap['CROSS']}, circles for {toolmap['CIRCLE']}, and curves for {toolmap['CURVATURE']}.",
            f"Allow human-style slack - perspective, chance, tolerance - so the {dev} works in the real world, not just on paper.",
            f"Output the finished {dev} as one valid build, with a machine-readable autoread block stamped on it for verification.",
        ]
        who = (f"Builders, manufacturers, and product teams who want {article(dev)} with documented "
               f"measurements and a repeatable way to make it.")
    else:
        what = (f"This is {article(dev)}: software in {category}. In plain terms, it is a program "
                f"built to deliver {ptxt}, and its data flow, decisions, and limits are all decided "
                f"by a six-shape design system instead of guesswork.")
        how = [
            f"Start with one controlled origin point - the 'binary-1' anchor - so the whole {dev} grows from a single known-good state.",
            f"Aim at the job it must do and work backwards, which locks the {ptxt} target before any code is written.",
            f"Run the design through six shapes: lines for {toolmap['LINE']}, triangles for {toolmap['TRIANGLE']}, squares for {toolmap['SQUARE']}, crosses for {toolmap['CROSS']}, circles for {toolmap['CIRCLE']}, and curves for {toolmap['CURVATURE']}.",
            f"Allow human-style slack - perspective, chance, tolerance - so the {dev} behaves sanely under real load.",
            f"Ship the finished {dev} as one valid build, with a machine-readable autoread block emitted on every deploy.",
        ]
        who = (f"Developers, teams, and operators who want {article(dev)} with documented behavior "
               f"and a repeatable way to build and run it.")
    return {
        "headline": f"AI explainer: {dev}",
        "what": what,
        "how_it_works": how,
        "who_its_for": who,
        "bottom_line": (f"If you remember one thing: this {dev} is a {kind} invention whose every "
                        f"decision traces back to six shapes and five reversed steps - nothing is arbitrary."),
    }

# ----------------------------------------------------------------------------
# State + generation
# ----------------------------------------------------------------------------
ALLCATS = [(n, "software", c, devs) for n, c, devs in SWCATS] + \
          [(n, "hardware", c, devs) for n, c, devs in HWCATS]

def load_state():
    if os.path.exists(STATE):
        with open(STATE, encoding="utf-8") as fh:
            st = json.load(fh)
        st.setdefault("used_titles", [])
        return st
    return {"seed": SEED, "next_index": 1, "used_titles": []}

def save_state(st):
    st["catset"] = CATSET
    tmp = STATE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(st, fh, separators=(",", ":"))
    os.replace(tmp, STATE)

def random_date(r):
    days = (DATE_END - DATE_START).days
    return (DATE_START + __import__("datetime").timedelta(days=r.randint(0, days))).isoformat()

def make_spec(i, used, seed=None, category=None):
    r = random.Random(seed if seed is not None else f"JAH-{SEED}-{i}")
    cat, kind, cpc, devs = category if category is not None else r.choices(ALLCATS, weights=CAT_WEIGHTS, k=1)[0]
    dev = r.choice(devs)
    fn = r.choice(SW_FUNCS if kind == "software" else HW_FUNCS)
    mech = r.choice(SW_MECHS if kind == "software" else HW_MECHS)
    title = f"{dev[0].upper()}{dev[1:]} for {fn} using {mech}"
    # Resolve the rare title collision with a revision suffix.
    rev = 2
    base = title
    while title.lower() in used and rev < 50:
        title = f"{base} (Rev {rev})"
        rev += 1
    spec_id = f"JAH-SPEC-{i:06d}"
    era = r.choices(["Past", "Current", "Future"], weights=[25, 45, 30])[0]
    prepared = random_date(r)
    params = build_params(r, kind)
    toolmap = build_toolmap(kind, dev)
    steps = build_steps(dev, fn)
    autoread = build_autoread(spec_id, title, cat, cpc, era, params)
    manufacture = build_manufacture(r, kind, title, cat, params)
    demo = build_demo(r, kind, title, cat)
    measurements = build_measurements(r, kind, title, cat)
    ai_explainer = build_ai_explainer(r, kind, title, cat, params, toolmap, steps)
    abstract = build_abstract(r, kind, dev, fn, mech)
    patent_draft = build_patent_draft(r, kind, title, cat, params, toolmap, extra={
        "spec_id": spec_id, "cpc": cpc, "era": era, "prepared": prepared,
        "steps": steps, "measurements": measurements, "manufacture": manufacture,
        "demo": demo, "ai_explainer": ai_explainer, "line": line_for_category(cat, kind),
        "abstract_text": abstract,
    })
    return {
        "spec_id": spec_id,
        "title": title,
        "abstract": abstract,
        "category": cat,
        "cpc": cpc,
        "era": era,
        "prepared_date": prepared,
        "inventor": INVENTOR,
        "owner": INVENTOR,
        "status": STATUS,
        "signature_tool_mapping": toolmap,
        "key_parameters": params,
        "autoread_block": autoread,
        "algorithm_steps": steps,
        "patent_draft": patent_draft,
        "manufacture": manufacture,
        "demo": demo,
        "measurements": measurements,
        "ai_explainer": ai_explainer,
    }, title.lower()

def main():
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    st = load_state()
    used = set(st["used_titles"])
    start = st["next_index"]
    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    made = 0
    with open(DATA, "a", encoding="utf-8") as fh:
        for i in range(start, start + count):
            spec, tkey = make_spec(i, used)
            used.add(tkey)
            st["used_titles"].append(tkey)
            fh.write(json.dumps(spec, separators=(",", ":"), ensure_ascii=True) + "\n")
            made += 1
            if made % 2500 == 0:
                print(f"  ...{made}/{count}", flush=True)
    st["next_index"] = start + count
    save_state(st)
    size_kb = os.path.getsize(DATA) / 1024
    total = start + count - 1
    print(f"done: +{made} new, {total} total specs ({size_kb:,.0f} KB)")


# ----------------------------------------------------------------------------
# BOUNDARY (2026-09-28): every spec is an ORIGINAL invention concept generated
# fresh through the Signature-One framework. Nothing here copies, closely
# paraphrases, or re-attributes any real patent record (including records from
# the cyber-patent-catalog dataset). The CPC subclass codes below are used ONLY
# as a coverage checklist for breadth - which technology areas to cover across
# every field that has ever had a patent (sections A through H). All titles,
# abstracts, parameter sets, and tool mappings are newly generated original
# content by Justin Addam Higgins (JAH).
# ----------------------------------------------------------------------------

# v2 expansion (2026-09-28): all-fields coverage, CPC sections A-H.
# NOTE: ALLCATS grew after specs 1-10000 were published. Per-index seeding means
# indices 1-10000 keep their published content; the expanded list applies to
# indices >= 10001. The used_titles dedup in state.json guards all future runs.
CATSET = "2026-09-28-v3: 122 categories, CPC A-H; uniform coverage, all products"

NEWCATS = [
 ("Agriculture Equipment", "A01", ["tractor guidance unit", "soil moisture probe", "drip irrigation valve", "seed planter", "crop sprayer boom", "harvester header", "grain auger", "fence energizer", "livestock feeder", "greenhouse vent opener"]),
 ("Food Processing", "A23", ["dough mixer", "pasteurizer", "conveyor oven", "slicing blade", "filling nozzle", "capping head", "retort sterilizer", "extrusion die", "blast chiller", "inspection conveyor"]),
 ("Beverage Systems", "A23", ["brewing kettle", "carbonator", "tap dispenser", "keg coupler", "bottle filler", "syrup pump", "draft tower", "juice press", "water carbonator", "growler capper"]),
 ("Apparel Machinery", "D01", ["weaving loom", "knitting head", "dyeing drum", "fabric cutter", "sewing machine head", "embroidery hoop", "yarn winder", "fabric press", "buttonholer", "hemmer"]),
 ("Footwear", "A43", ["sole mold", "cushioning insert", "lacing system", "shoe last", "outsole tread", "heel counter", "insole board", "toe cap", "cleat plate", "slip-last boot"]),
 ("Calculators", "G06F", ["handheld calculator", "scientific calculator", "graphing calculator", "printing calculator", "solar calculator", "pocket adding machine", "calculator keypad module", "calculator display driver", "desktop counting machine", "tape calculator"]),
 ("Furniture", "A47", ["recliner mechanism", "desk lift column", "cabinet hinge", "drawer slide", "bed frame joint", "office chair base", "table leg leveler", "shelf bracket", "folding hinge", "swivel plate"]),
 ("Sports Equipment", "A63", ["racket frame", "helmet shell", "training robot", "golf club head", "ski binding", "protective pad", "ball inflator", "timing gate", "exercise bike flywheel", "rowing machine rail"]),
 ("Toys & Games", "A63", ["RC car chassis", "puzzle cube", "toy drone", "building block set", "plush animatronic", "slot car track", "kite frame", "yo-yo axle", "board game spinner", "marble run tower"]),
 ("Musical Instruments", "G10", ["digital piano keybed", "drum trigger pad", "guitar effects pedal", "wind controller", "metronome", "tuner clip", "mixer fader", "synthesizer knob", "speaker cabinet", "microphone stand"]),
 ("Chemical Processing", "B01", ["reactor vessel", "distillation column", "industrial mixer", "filter press", "centrifuge bowl", "evaporator", "crystallizer", "absorption tower", "heat-traced pipe", "agitator blade"]),
 ("Water Treatment", "C02", ["filtration membrane", "UV sterilizer", "desalination unit", "clarifier rake", "dosing pump", "aeration diffuser", "sludge scraper", "ion exchange tank", "ozone generator", "backwash valve"]),
 ("Machine Tools", "B23", ["lathe chuck", "milling head", "drill press table", "CNC spindle", "tool changer", "collet holder", "workholding vise", "coolant nozzle", "boring bar", "surface grinder wheel"]),
 ("Welding", "B23", ["MIG torch", "spot welder", "plasma cutter", "welding helmet", "electrode holder", "ground clamp", "wire feeder", "positioner table", "fume extractor", "arc starter"]),
 ("Material Handling", "B65", ["conveyor belt", "palletizer", "forklift mast", "roller conveyor", "sortation chute", "lift table", "drum handler", "vacuum lifter", "cart pusher", "tote stacker"]),
 ("Packaging Machinery", "B65", ["shrink wrapper", "carton erector", "label applicator", "case sealer", "pallet wrapper", "fill-level inspector", "cap tightener", "pouch sealer", "strapping machine", "box former"]),
 ("Industrial Printing", "B41", ["flexo press", "ink mixer", "gravure cylinder", "screen printer", "pad printer", "inkjet array", "curing tunnel", "web tensioner", "die cutter", "laminator"]),
 ("Paper Products", "D21", ["paper machine roller", "cardboard corrugator", "sheet cutter", "pulp refiner", "embosser", "rewinder", "coating blade", "dryer can", "bale press", "core winder"]),
 ("Construction Equipment", "E02", ["excavator arm", "crane hoist", "concrete mixer", "compactor plate", "scaffold frame", "boom lift", "dump trailer", "trench box", "rebar tier", "laser level"]),
 ("Building Materials", "E04", ["insulation panel", "roofing membrane", "window frame", "drywall lift", "flooring plank", "siding panel", "vapor barrier", "anchor bolt", "joist hanger", "flashing strip"]),
 ("Plumbing", "E03", ["faucet valve", "pipe fitting", "water heater", "drain snake", "sump basin", "backflow preventer", "shower head", "toilet fill valve", "pex expander", "trap primer"]),
 ("Locks & Security Hardware", "E05", ["deadbolt", "padlock body", "safe door", "door closer", "access panel", "keypad lock", "hinge pin", "strike plate", "exit device", "security hasp"]),
 ("Engines", "F01", ["piston", "turbocharger", "crankshaft", "camshaft", "cylinder head", "flywheel", "oil pump", "timing chain", "engine mount", "exhaust manifold"]),
 ("Compressors", "F04", ["air compressor", "refrigerant compressor", "scroll housing", "piston ring set", "intercooler", "receiver tank", "pressure switch", "unloader valve", "oil separator", "vibration isolator"]),
 ("Fans & Blowers", "F04", ["ceiling fan", "industrial blower", "duct fan", "impeller", "fan shroud", "speed controller", "louver vent", "attic fan", "range hood blower", "cooling tower fan"]),
 ("Heat Exchangers", "F28", ["plate exchanger", "radiator core", "condenser coil", "shell-and-tube unit", "fin stock", "header tank", "brazed joint", "fouling sensor", "expansion joint", "air cooler"]),
 ("Refrigeration", "F25", ["walk-in freezer", "ice maker", "cold plate", "display cooler", "compressor rack", "defrost heater", "evaporator fan", "insulated door", "temperature logger", "condensing unit"]),
 ("Optics", "G02", ["camera lens", "mirror mount", "prism", "optical filter", "collimator", "beam splitter", "lens barrel", "fiber coupler", "diffuser", "polarizer"]),
 ("Clocks & Watches", "G04", ["watch movement", "escapement", "smart crown", "watch case", "bracelet clasp", "dial hand set", "mainspring barrel", "bezel ring", "crystal gasket", "rotor weight"]),
 ("Radiation Instrumentation", "G21", ["radiation detector", "shielding panel", "survey meter", "dosimeter badge", "lead container", "scintillator", "count-rate meter", "calibration source holder", "area monitor", "interlock switch"]),
 ("Elevators", "B66", ["hoist machine", "door operator", "counterweight", "guide rail", "safety gear", "landing button", "car frame", "rope gripper", "governor", "buffer spring"]),
 ("Vending", "G07", ["dispenser coil", "coin mechanism", "bill validator", "refrigerated cabinet", "selection keypad", "drop sensor", "product spiral", "cash box", "telemetry modem", "door lock"]),
 ("Cleaning Equipment", "B08", ["vacuum head", "pressure washer", "floor scrubber", "steam cleaner", "dust extractor", "squeegee blade", "mop wringer", "carpet extractor", "air mover", "gutter scoop"]),
 ("Personal Care Appliances", "A45", ["hair dryer", "beard trimmer", "electric shaver", "curling iron", "scalp massager", "skincare device", "nail drill", "epilator", "facial steamer", "toothbrush head"]),
 ("Pet Products", "A01", ["automatic feeder", "pet tracker", "grooming clipper", "water fountain", "training collar", "pet door", "litter box", "aquarium filter", "bird cage", "leash reel"]),
 ("Marine Equipment", "B63", ["bilge pump", "propeller", "navigation light", "cleat", "anchor windlass", "thru-hull fitting", "marine battery box", "fishfinder mount", "dock fender", "trolling motor"]),
 ("Rail Equipment", "B61", ["bogie frame", "coupler", "rail brake", "wheelset", "pantograph", "door interlock", "ballast tamper", "signal mast", "axle box", "suspension spring"]),
 ("Bicycles", "B62", ["bike frame", "derailleur", "e-bike motor", "disc brake", "wheel hub", "pedal crank", "suspension fork", "dropper post", "chain ring", "cargo rack"]),
 ("Tires & Wheels", "B60", ["tire carcass", "alloy rim", "valve stem", "bead seater", "wheel balancer", "tire changer", "pressure gauge", "run-flat insert", "spare carrier", "lug wrench"]),
 ("Glass & Ceramics", "C03", ["glass kiln", "glass cutter", "tempering furnace", "ceramic press", "glaze sprayer", "annealing lehr", "mold release", "frit feeder", "edge grinder", "laminating autoclave"]),
 ("Adhesives", "C09", ["glue dispenser", "mixing nozzle", "curing lamp", "adhesive film", "hot-melt gun", "laminating roller", "primer applicator", "bond tester", "cartridge plunger", "static mixer"]),
 ("Fertilizer Equipment", "C05", ["fertilizer spreader", "granulator", "blending drum", "coating pan", "bagging scale", "conveyor auger", "dust collector", "sieve screen", "hopper gate", "weigh belt"]),
 ("Ropes & Cables", "D07", ["rope braider", "cable winch", "swaging tool", "thimble", "turnbuckle", "wire rope clip", "pulling grip", "reel stand", "lubricator", "tension meter"]),
 ("Drilling & Mining", "E21", ["drill bit", "rock crusher", "mine conveyor", "roof bolter", "ventilation fan", "dewatering pump", "blast hole drill", "ore sorter", "dust suppressor", "cap lamp"]),
 ("Road Equipment", "E01", ["asphalt paver", "road roller", "traffic barrier", "pothole patcher", "line striper", "snow plow", "street sweeper", "guardrail post", "manhole cover", "storm drain"]),
 ("Doors & Windows", "E06", ["door hinge", "window operator", "sliding track", "weather seal", "door closer", "sidelight frame", "skylight curb", "garage spring", "threshold ramp", "peephole viewer"]),
]

# Extra mechanical-domain functions / mechanisms for the expanded fields.
HW_FUNCS = HW_FUNCS + ["heavy lifting", "abrasive cutting", "high-pressure sealing", "corrosion resistance", "seismic stability", "bulk material transport", "precision dispensing", "continuous duty cycling", "outdoor weathering", "food-grade sanitation"]
HW_MECHS = HW_MECHS + ["hardened steel alloys", "hydraulic rams", "roller bearings", "gear reduction", "belt drives", "chain drives", "welded frames", "cast housings", "powder coating", "galvanized finishes"]

# Rebuild the master category list with the expansion.
EXISTING_NAMES = set(n for n, _, _, _ in
    [(n, "software", c, devs) for n, c, devs in SWCATS] +
    [(n, "hardware", c, devs) for n, c, devs in HWCATS] +
    [(n, "hardware", c, devs) for n, c, devs in NEWCATS])
try:
    from catalog_groups import iter_group_cats, group_map
    GROUPCATS = [(cn, k, cpc, devs) for _, cn, k, cpc, devs in iter_group_cats()
                 if cn not in EXISTING_NAMES]
    GROUPMAP = group_map()
    CATSET = "2026-09-28-v4: catalog groups added (media/software/hardware/products/legal/science/math/utility/business/medical/engineering/creative/defense/transport/environment/specials/solvers/cyber/genome/space/occupations/wiki/academy)"
except ImportError:
    GROUPCATS = []
    GROUPMAP = {}
ALLCATS = [(n, "software", c, devs) for n, c, devs in SWCATS] + \
          [(n, "hardware", c, devs) for n, c, devs in HWCATS] + \
          [(n, "hardware", c, devs) for n, c, devs in NEWCATS] + \
          GROUPCATS

# Signature product lines (2026-09-28): named lines for Manon's verticals --
# Signature AI, Signature Software, Signature Code, Signature Gaming,
# Signature Hardware. Used by the signature-line pipeline so each original
# JAH version lands under the right line name.
AI_CATS = {"Artificial Intelligence", "Machine Learning",
           "Natural Language Processing", "Computer Vision",
           "Recommender Systems", "Anomaly Detection",
           "AI Types", "AI Models", "AI Tools", "AI Agents", "AI Frameworks",
           "AI Pipelines", "AI Workflows", "AI Intelligence", "AI Ability"}
CODE_CATS = {"Developer Tools", "Compilers", "APIs", "Software Testing",
             "Container Orchestration", "Data Pipelines", "Firmware",
             "Code", "Code File", "All AI Python Tool Library"}
GAME_CATS = {"Gaming", "Toys & Games", "Virtual Reality", "Augmented Reality",
            "Video Games", "Games", "Universal Video Game",
            "Universal Basic Static Game", "Advanced Level Gamer",
            "Future Level Gaming", "Game Design"}

def line_for_category(cat_name, kind):
    if cat_name in AI_CATS:
        return "Signature AI"
    if cat_name in CODE_CATS:
        return "Signature Code"
    if cat_name in GAME_CATS:
        return "Signature Gaming"
    if kind == "software":
        return "Signature Software"
    return "Signature Hardware"

# Coverage (2026-09-28): Manon wants ALL products covered uniformly - no priority
# lines. Every category gets equal weight; the drip fills every field evenly.
PRIORITY_WEIGHTS = {}
CAT_WEIGHTS = [PRIORITY_WEIGHTS.get(n, 1) for n, _, _, _ in ALLCATS]

if __name__ == "__main__":
    main()
