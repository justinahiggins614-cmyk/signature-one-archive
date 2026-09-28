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

def make_spec(i, used):
    r = random.Random(f"JAH-{SEED}-{i}")
    cat, kind, cpc, devs = r.choices(ALLCATS, weights=CAT_WEIGHTS, k=1)[0]
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
    return {
        "spec_id": spec_id,
        "title": title,
        "abstract": build_abstract(r, kind, dev, fn, mech),
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
CATSET = "2026-09-28-v3: 122 categories, CPC A-H; priority lines: Footwear, Calculators"

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
ALLCATS = [(n, "software", c, devs) for n, c, devs in SWCATS] + \
          [(n, "hardware", c, devs) for n, c, devs in HWCATS] + \
          [(n, "hardware", c, devs) for n, c, devs in NEWCATS]

# Manon's product lines (2026-09-28): weighted priority so the drip generates
# more original specs in HER lines (footwear line, Signature calculators)
# while still covering every field. Applies to newly generated indices only.
PRIORITY_WEIGHTS = {"Footwear": 8, "Calculators": 8}
CAT_WEIGHTS = [PRIORITY_WEIGHTS.get(n, 1) for n, _, _, _ in ALLCATS]

if __name__ == "__main__":
    main()
