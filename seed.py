from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.services.models import Base, User, Team, Alert, AlertSeverity  # Make sure these match your actual imports

# Connect to SQLite (this creates a file named test.db)
DATABASE_URL = "sqlite:///seeddata.db"
engine = create_engine(DATABASE_URL, echo=True)

# Create tables
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Start a session
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# Seed teams
team_alpha = Team(name="Team Alpha")
team_beta = Team(name="Team Beta")

session.add_all([team_alpha, team_beta])
session.commit()

# Seed users
users = [
    User(email="alice@example.com", full_name="Alice Smith", team_id=team_alpha.id),
    User(email="bob@example.com", full_name="Bob Brown", team_id=team_alpha.id),
    User(email="carol@example.com", full_name="Carol Jones", team_id=team_beta.id),
    User(email="dave@example.com", full_name="Dave Lee", team_id=team_beta.id),
    User(email="eve@example.com", full_name="Eve Miller", team_id=team_alpha.id),
]

session.add_all(users)
session.commit()

# (Optional) Seed a sample alert
alert = Alert(
    title="Server Downtime",
    message_body="The server will be down at midnight for maintenance.",
    severity=AlertSeverity.WARNING,
    created_by_id=users[0].id,
    is_org_wide=False,
)
alert.target_teams.append(team_alpha)
session.add(alert)
session.commit()

session.close()
print("✅ Seed data inserted into SQLite!")
