# Catalog groups for Manon's master intent list (2026-09-28).
# Each group maps to new spec categories. The drip fill draws from ALLCATS,
# so every group fills in over time; the seed script plants a few of each now.
# Format: (group_name, cpc, default_kind, [names]) where a name may be
# "Name" (uses default_kind) or ("Name", kind) to override.
# kind is "software", "hardware", or "both" (expands to one of each).

GROUPS = [
("Media", "H04N", "both", [
    "Movies", "TV Shows", "Video Games", "Games", "Music", "Audio",
    "Podcasts", "Animations", "Comics", "Manga", "Publications", "Books",
    "Digital Media", "Physical Media", "Streaming Media", "Radio",
    "News Media", "Photography", "Art", "Graphic Design", "3D Media",
    "Virtual Media", "Augmented Media", "Mixed Reality Media",
    "Holographic Media", "Future Media",
]),
("Software & Digital Systems", "G06F", "software", [
    "Apps", "Programs", "Software", "Operating Systems", "Drivers",
    "Plugins", "Extensions", "Web Apps", "Mobile Apps", "AI Types",
    "AI Models", "AI Tools", "AI Agents", "AI Frameworks", "AI Pipelines",
    "AI Workflows", "Code", "Libraries", "Engines", "Scripts", "Automation",
    "Frameworks", "APIs", "Databases", "Cloud Services", "Virtual Machines",
    "Containers", "Cybersecurity Tools", "Encryption", "Networking Software",
    "Simulation Software", "Future Software", "Universal Software",
    "Omni Software",
]),
("Hardware & Physical Devices", "G06F", "hardware", [
    "Hardware", "PC Types", "Components", "Devices", "Machines", "Tools",
    "Office Tools", "Robotics", "Electronics", "Instruments", "Sensors",
    "Controllers", "Wearables", "Peripherals", "Embedded Systems",
    "IoT Devices", "Smart Devices", "Industrial Machines",
    "Manufacturing Machines", "Medical Devices", "Scientific Instruments",
    "Quantum Devices", "Nanotech Devices", "Future Hardware",
    "Universal Hardware", "Omni Hardware", "All Things Hardware",
]),
("Products & Manufacturing", "B65", "hardware", [
    "Products", "Consumer Goods", "Industrial Goods", "Toys", "Equipment",
    "Materials", "Manufacturing Processes", "Packaging", "Prototypes",
    "Blueprints", "Supply Chain", "Logistics", "Distribution", "Retail",
    "Wholesale", "Construction Materials", "Construction Tools",
    "Construction Systems", "Future Manufacturing",
]),
("Legal & Structural", "G06Q", "software", [
    "Patents", "Trademarks", "Copyright", "Licensing", "Specifications",
    "Standards", "Compliance", "Regulatory", "Documentation", "Contracts",
    "Policies", "Governance", "Audit", "Verification", "Certification",
    "Future Legal",
]),
("Science, Education & Lab", "G01N", "both", [
    "Labs", "Experiments", "Research Tools", "Academic Subjects",
    "Scientific Fields", "Educational Tools", "Learning Modules",
    "Curriculums", "Research Papers", "Science Prediction", "Science Theory",
    "Science Proof Solver", "Physics", "Chemistry", "Biology", "Astronomy",
    "Geology", "Ecology", "Mathematics", "Statistics", "Computer Science",
    "Neuroscience", "Psychology", "Medicine", "Genetics", "Nanoscience",
    "Quantum Science", "Future Science",
]),
("Math", "G06F", "software", [
    ("Calculators", "both"), "Algebra Calculators",
    "Signature Constant Calculators", "Paradox Immune Calculators",
    "Math Sequenced", "Patterns in Math Sequenced", "Math Proof Solver",
    "Math Theory", "Science Math", "Pattern Recognition", "Pattern Decoder",
    "All Math Fields", "Future Math",
]),
("Functional & Utility", "G06F", "software", [
    "Functions", "Utilities", "Workflow", "Templates", "System Tools",
    "Conversion Tools", "Diagnostic Tools", "Maintenance Tools",
    "Optimization Tools", "Scheduling Tools", "Monitoring Tools",
    "Logging Tools", "Indexing Tools", "Search Tools", "Mapping Tools",
    "Future Utility",
]),
("Business & Economics", "G06Q", "software", [
    "Business Tools", "Finance", "Accounting", "Economics", "Marketing",
    "Sales", "HR", "Management", "Operations", "Strategy", "Planning",
    "Forecasting", "Risk", "Business Compliance", "Future Business",
]),
("Medical & Health", "A61", "both", [
    "Medical Tools", "Medical Procedures", "Health Systems",
    "Pharmaceutical", "Biotech", "Genomics", "Proteomics", "Bioinformatics",
    "Diagnostics", "Therapeutics", "Clinical Trials", "Future Medicine",
]),
("Engineering", "G06F", "both", [
    "Mechanical Engineering", "Electrical Engineering", "Civil Engineering",
    "Chemical Engineering", "Aerospace Engineering", "Software Engineering",
    "Systems Engineering", "Industrial Engineering", "Materials Engineering",
    "Environmental Engineering", "Future Engineering",
]),
("Creative & Artistic", "G06T", "both", [
    "Design", "Fashion", "Architecture", "Music Creation", "Film Production",
    "Writing", "Storytelling", "Worldbuilding", "Game Design",
    "Future Creative",
]),
("Military & Defense", "F41", "hardware", [
    "Defense Systems", "Security Tools", "Cyber Defense", "Surveillance",
    "Tactical Equipment", ("Military Vehicles", "hardware"), "Drones",
    "Future Defense",
]),
("Transportation", "B60", "hardware", [
    "Vehicles", "Transit", "Rail", "Aviation", "Marine", "Spacecraft",
    "Infrastructure", "Road Systems", "Bridge Systems",
    "Future Transportation",
]),
("Environment & Earth", "G01W", "both", [
    "Climate", "Weather", "Ecosystems", "Agriculture", "Forestry",
    "Water Systems", "Energy Systems", "Sustainability", "Future Environment",
]),
("Signature Specials", "G06F", "both", [
    "Calculator Types", "Signature Math", "Language Interpretation",
    "Cyber Sensor", "Optional System Upgrade", "Computer Universal Antivirus",
    "Universal Thumb-Drive Cyber Design", "Universal Thumb-Drive New Persona",
    "Universal Basic Static Game", "Universal Video Game",
    "Advanced Level Gamer", "Future Level Gaming",
]),
("Solvers & Predictors", "G06F", "software", [
    "Environment Solver", "Environment Detection", "Experiment Solver",
    "Predictor", "Forecast", "Theory Solver", "Theory Maker",
    "Science Proof", "Math Proof", "All Around Proofer",
]),
("Cyber Core", "G06F", "both", [
    "All AI Python Tool Library", "AI Intelligence", "AI Ability",
    ("Super Computer Cluster", "hardware"), ("Semiconductor", "hardware"),
    ("Quanta PC", "hardware"), ("Chip Builder", "hardware"), "Code File",
    "Website Builder", "Website", "Signature Replica of Internet",
    ("All PC Model Simulator", "hardware"), "Anything Cyber",
    ("Super Cloud", "hardware"),
]),
("Genome", "C12N", "both", [
    "Human Genome Coded", "Animal Genome Coded", "Insect Genome Coded",
    "PC Genome Coded", "AI Genome Coded", "Trans-Pan-All Genome",
]),
("Space", "B64G", "hardware", [
    "NASA Hardware", "Space Zero to Infinite G", "Space Station",
    "Satellite", "Planet Orbit Harvesting", "Planet Engineering",
]),
("Occupations", "G09B", "both", [
    "PHD Track", "Lawyer Track", "Programmer Track", "Technician Track",
    "Repair Track", "All Occupations",
]),
("Task Doers", "G06F", "both", [
    "Lock Unlock Task Doer", "Translators", "Robots",
    "PC System Task Troll",
]),
("JAH-N Wiki", "G06F", "software", [
    "JAH-N Wiki Pages", "JAH-N Wiki Leaks",
]),
("JAH-N Academy", "G09B", "software", [
    "JAH-N Academy Courses", "JAH-N Academy Degrees",
]),
]

DEV_TEMPLATES = [
    "{n} system", "{n} engine", "{n} module", "{n} toolkit", "{n} suite",
    "portable {n}", "{n} console", "{n} array", "{n} hub", "{n} lab",
]

def group_devs(cat_name):
    n = cat_name.lower()
    return [t.format(n=n) for t in DEV_TEMPLATES]

def iter_group_cats():
    """Yield (group_name, cat_name, kind, cpc, devs)."""
    for gname, cpc, dkind, cats in GROUPS:
        for c in cats:
            if isinstance(c, tuple):
                cname, kind = c
            else:
                cname, kind = c, dkind
            kinds = ("software", "hardware") if kind == "both" else (kind,)
            for k in kinds:
                yield gname, cname, k, cpc, group_devs(cname)

def group_map():
    """{cat_name: group_name} for the page."""
    m = {}
    for gname, cname, _k, _c, _d in iter_group_cats():
        m.setdefault(cname, gname)
    return m
