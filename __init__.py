from aqt import mw, QAction, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QDialog
from anki.notes import Note
from anki.cards import FSRSMemoryState
import json

class InputDialog(QDialog):
    def __init__(self):
        super().__init__(mw)

        self.setWindowTitle("Card From Custom Data")

        # Layout for the dialog
        layout = QVBoxLayout()

        # Label
        self.label = QLabel("Enter your text:")
        layout.addWidget(self.label)

        # Text input
        self.text_input = QLineEdit(self)
        self.text_input.setMaxLength(2147483647)
        layout.addWidget(self.text_input)

        # Buttons
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)  # "Confirm"
        self.buttons.rejected.connect(self.reject)  # "Cancel"
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_input_text(self):
        """Returns the text from the input field."""
        return self.text_input.text()

    def accept(self) -> None:
        data = json.loads(self.get_input_text())

        import_config_id = data['config']['id']
        did = mw.col.decks.id(f"DEBUG_CARDS::${import_config_id}")
        deck = mw.col.decks.get(did)

        new_config = mw.col.decks.add_config(str(import_config_id), data['config'])
        mw.col.decks.set_config_id_for_deck_dict(deck, new_config["id"])

        model = mw.col.models.by_name("Basic")
        note = Note(mw.col, model)

        note.fields[0] = f"<pre>{json.dumps(data, indent=2)}</pre>"

        mw.col.add_note(note, did)

        data["cardRow"][1] = note.id
        data["cardRow"][2] = did
        mw.col.db.execute("""
        REPLACE INTO cards
            ("id", "nid", "did", "ord", "mod", "usn", "type", "queue", "due", "ivl", "factor", "reps", "lapses", "left", "odue", "odid", "flags", "data")
        VALUES 
            (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            *data["cardRow"]
        )

        cid = data["cardRow"][0]
        for revlog in reversed(data["revlog"]):
            revlog["row"][1] = cid
            revlog["row"][2] = -1

            revlog["row"][0] += 1 # Prevent overwriting actual cards

            mw.col.db.execute(f"""
                REPLACE INTO revlog (
                    id, cid, usn, ease, ivl, lastIvl, factor, time, type
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?
                );
            """, *revlog["row"])
        
        mw.col.compute_memory_state(cid)

        return super().accept()

def showInputMenu():



    menu = InputDialog()

    menu.exec()

action = QAction("Import card from debug info")
action.triggered.connect(showInputMenu)

mw.form.menuTools.addAction(action)
