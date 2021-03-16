from typing import Optional
import sqlite3


def _initialize_pf_db(conn: sqlite3.Connection):
    with conn.cursor() as c:
        c.execute("""CREATE TABLE entities (
                         ent_id TEXT PRIMARY KEY,
                         type TEXT NOT NULL
        );""")

        # The actual performance gain for this is probably negligible and
        # debatable from the engineering perspective, but even in a hobby
        # game project it's worth considering best practice.
        #
        # Admittedly, even the use of an index on a column with two possible
        # values is itself a bit silly, but... humor me, lovely?
        c.execute("""CREATE INDEX entity_id_type
                         ON entities (ent_id, type)""")

        # Create a table of entity introductions to the playfield.
        c.execute("""CREATE TABLE ents_introduced (
                         id INTEGER NOT NULL AUTOINCREMENT,
                         ent_id TEXT NOT NULL,
                         spawn_x INTEGER NOT NULL,
                         spawn_y INTEGER NOT NULL,
                         
                         CONSTRAINT fk_ent_id
                             FOREIGN KEY (ent_id)
                             REFERENCES entities(ent_id)
        );""")

        # Create a table of entity destruction events.
        c.execute("""CREATE TABLE ents_destroyed (
                         id INTEGER NOT NULL AUTOINCREMENT,
                         ent_id TEXT NOT NULL,
                         destroyer TEXT,
                         
                         CONSTRAINT fk_ent_id
                             FOREIGN KEY (ent_id)
                             REFERENCES entities(ent_id),
                             
                         CONSTRAINT fk_destroyer
                             FOREIGN KEY (destroyer)
                             REFERENCES entities(ent_id)
        );""")

        # Create views which divvy up the entities table into mindforms and cogforms.
        c.execute("""CREATE VIEW mindforms AS
                         SELECT * FROM entities
                             WHERE entities.type = "mindform"
        ;""")

        c.execute("""CREATE VIEW cogforms AS
                         SELECT * FROM entities
                             WHERE entities.type = "cogform"
        ;""")

        # Create a table to keep track of abilities.
        # The IDs may vary wildly for cogforms' abilities depended on how
        # they're generated, but the player's should be much easier to track.
        c.execute("""CREATE TABLE abilities (
                         ability_id TEXT NOT NULL,
                         user_id TEXT NOT NULL,
                         name TEXT,
                         
                         PRIMARY KEY (ability_id, user_id),
                         
                         CONSTRAINT fk_user_id
                             FOREIGN KEY (user_id)
                             REFERENCES entities(ent_id)
        );""")

        # Create a table which tracks uses of abilities and their targets.
        c.execute("""CREATE TABLE abilities_used (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         ability INTEGER NOT NULL,
                         user TEXT NOT NULL,
                         target TEXT NOT NULL,
                         
                         CONSTRAINT fk_ability
                             FOREIGN KEY (ability)
                             REFERENCES abilities(ability_id),
                         CONSTRAINT fk_user
                             FOREIGN KEY (user)
                             REFERENCES entities(ent_id),
                         CONSTRAINT fk_target
                             FOREIGN KEY (target)
                             REFERENCES entities(ent_id)
        );""")


class PFEventLogger:
    def __init__(self, playfield,
                 from_db: Optional[sqlite3.Connection] = None):
        """Creates a database based on the schema defined in logger.py.
        Optionally loads from the contents of an existing database (for example, one on disk.)"""
        self.playfield = playfield

        self.conn = sqlite3.connect(":memory:")
        _initialize_pf_db(self.conn)

        if from_db:
            from_db.backup(self.conn)

    def write_to_disk(self, dir_path: str, filename: str) -> None:
        """Uses sqlite3.Connection.backup to copy this file to a specified file in a specified directory on disk."""

        # Account for whether the dir_path string ends in a slash.
        if dir_path[-1] in ("\\", "/"):
            tgt = "{}{}.db".format(dir_path, filename)
        else:
            tgt = "{}/{}.db".format(dir_path, filename)

        tgt_conn = sqlite3.connect(tgt)
        self.conn.backup(tgt_conn)

    def cursor(self) -> sqlite3.Cursor:
        """Returns a fresh cursor from this logger's (probably in-memory) database connection."""
        return self.conn.cursor()

    def add_entity(self, ent_id: str, type_: str) -> None:
        """Record an entity as being present in this playfield's log."""
        with self.cursor() as c:
            c.execute("INSERT INTO entities(ent_id, type) VALUES {}, {}"
                      .format(ent_id, type_))

    def add_entity_introduced(self, ent_id: str,
                              spawn_x: int, spawn_y: int) -> None:
        """Record an entity as being introduced to the playfield, and also where."""
        with self.cursor() as c:
            c.execute("""INSERT INTO ents_introduced(ent_id, spawn_x, spawn_y)
                             VALUES({}, {}, {})"""
                      .format(ent_id, str(spawn_x), str(spawn_y)))

    def add_entity_destroyed(self, ent_id: str,
                             destroyer: Optional[str] = None) -> None:
        """Record an entity being destroyed, and what entity destroyed them."""
        with self.cursor() as c:
            c.execute("""INSERT INTO ents_destroyed(ent_id, destroyer)
                             VALUES({}, {})"""
                      .format(ent_id, destroyer))

    def add_ability(self, ability_id: str, user_id: str, name: str) -> None:
        """Adds an instance of a user having an ability to the log."""
        with self.cursor() as c:
            c.execute("INSERT INTO abilities(ability_id, user_id, name) VALUES({}, {}, {})"
                      .format(ability_id, user_id, name))

    def add_ability_used(self, ability_id: str, user_id: str, target_id: str) -> None:
        """Adds the use of an ability by one entity on another to the playfield log."""
        with self.cursor() as c:
            c.execute("""INSERT INTO abilities_used(ability, user, target)
                             VALUES({}, {}, {})"""
                      .format(ability_id, user_id, target_id))


mem_db = sqlite3.connect(":memory:")
_initialize_pf_db(mem_db)
