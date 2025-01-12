from aqt import mw, QAction, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QDialog
from anki.notes import Note
from anki.decks import Deck
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

        mw.checkpoint("Import note from debug data")

        did = mw.col.decks.id(f"DEBUG_CARDS::${data['config']['id']}")

        model = mw.col.models.by_name("Basic")
        note = Note(mw.col, model)

        note.fields[0] = self.get_input_text()

        mw.col.add_note(note, did)

        return super().accept()

def showInputMenu():
    menu = InputDialog()

    menu.exec()

action = QAction("Import card from debug info")
action.triggered.connect(showInputMenu)

mw.form.menuTools.addAction(action)
