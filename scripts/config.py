"""Central configuration for the profile-art generators."""
import os

# GitHub username (also the repo name). Override with env GH_USERNAME if needed.
USERNAME = os.environ.get("GH_USERNAME", "LeonardoVanni21")

# GitHub-style dark heatmap palette (levels 0..4)
HEATMAP_COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# Shared visual theme
BG = "#0d1117"          # canvas background
FG = "#c9d1d9"          # default text
ACCENT = "#39d353"      # green accent
DIM = "#8b949e"         # muted text
FONT = "ui-monospace, SFMono-Regular, 'DejaVu Sans Mono', Consolas, monospace"

# Info-card content (edit these freely)
NAME = "Leonardo Vanni Bonavigo"
CARD_FIELDS = [
    ("role",     "Backend Software Engineer"),
    ("company",  "Epicora Software House"),
    ("location", "Chapecó — SC, Brazil"),
    ("exp",      "4+ yrs · 30+ systems shipped"),
    ("lang",     "TypeScript · Node.js · C#"),
    ("stack",    "NestJS · .NET · Laravel"),
    ("cloud",    "AWS · Docker · CI/CD"),
    ("db",       "MongoDB · PostgreSQL · Redis"),
    ("auth",     "OAuth2 · JWT · Security"),
    ("langs",    "PT native · EN advanced"),
    ("focus",    "Scalable backend systems"),
    ("uptime",   "Creating Luck \U0001f340"),
]
