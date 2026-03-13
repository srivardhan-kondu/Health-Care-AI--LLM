import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DB_PATH

HOSPITALS = [
    # Trauma Care
    ("Apollo Hospital", "Trauma Care", 17.4435, 78.3772, 1, "+91-40-23607777"),
    ("NIMS Hospital", "Trauma Care", 17.4418, 78.4487, 1, "+91-40-23489000"),
    ("Osmania General Hospital", "Trauma Care", 17.3816, 78.4740, 1, "+91-40-24600912"),
    ("Global Hospital", "Trauma Care", 17.4139, 78.4528, 1, "+91-40-30244444"),
    ("Maxcure Hospital", "Trauma Care", 17.4556, 78.3740, 1, "+91-40-71194444"),

    # Orthopedic
    ("Yashoda Hospital", "Orthopedic", 17.4530, 78.3915, 1, "+91-40-45670000"),
    ("Kamineni Hospital", "Orthopedic", 17.3725, 78.5005, 1, "+91-40-39879999"),
    ("Star Hospital", "Orthopedic", 17.4482, 78.3748, 1, "+91-40-44455555"),
    ("Sunshine Hospital", "Orthopedic", 17.4900, 78.3600, 1, "+91-40-44747474"),
    ("Lotus Children Hospital", "Orthopedic", 17.4800, 78.3900, 0, "+91-40-27898989"),

    # Emergency / General
    ("Care Hospital", "Emergency", 17.4239, 78.4483, 1, "+91-40-30418000"),
    ("Medicover Hospital", "Emergency", 17.4457, 78.3818, 1, "+91-40-68108888"),
    ("Continental Hospital", "Emergency", 17.4046, 78.3396, 1, "+91-40-67000000"),
    ("Virinchi Hospital", "Emergency", 17.4416, 78.4520, 1, "+91-40-71899999"),
    ("Rainbow Hospital", "Emergency", 17.4347, 78.4447, 0, "+91-40-44885000"),

    # Neurology (Head Injuries)
    ("KIMS Hospital", "Neurology", 17.4354, 78.3908, 1, "+91-40-44885000"),
    ("Manipal Hospital", "Neurology", 17.4422, 78.3796, 1, "+91-40-33366666"),
    ("Aster Prime Hospital", "Neurology", 17.4922, 78.3764, 1, "+91-40-44555666"),
]

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    emergency INTEGER NOT NULL DEFAULT 0,
    contact TEXT NOT NULL
);
"""

def setup():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE)
    cursor.execute("DELETE FROM hospitals")  # clear for re-seeding

    cursor.executemany(
        "INSERT INTO hospitals (name, specialization, latitude, longitude, emergency, contact) VALUES (?, ?, ?, ?, ?, ?)",
        HOSPITALS
    )
    conn.commit()
    conn.close()
    print(f"✅ Database seeded with {len(HOSPITALS)} hospitals at: {DB_PATH}")

if __name__ == "__main__":
    setup()
