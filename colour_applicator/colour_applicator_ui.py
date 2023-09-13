import PySide2.QtWidgets as QtWidgets
from pyfbsdk import *

from colour_applicator.colour_applicator_mobu import set_object_colour, set_hierarchy_colour
from colour_applicator_utilities import random_key


# Dictionary of predefined colors
COLOURS = {
    'Red': (1.0, 0.0, 0.0),
    'Green': (0.0, 1.0, 0.0),
    'Blue': (0.0, 0.0, 1.0),
    'Yellow': (1.0, 1.0, 0.0),
    'Cyan': (0.0, 1.0, 1.0),
    'Magenta': (1.0, 0.0, 1.0),
    'Orange': (1.0, 0.5, 0.0),
    'Purple': (0.5, 0.0, 1.0),
    'Pink': (1.0, 0.0, 0.5),
    'Brown': (0.6, 0.3, 0.1),
    'Gray': (0.5, 0.5, 0.5),
    'White': (1.0, 1.0, 1.0)
}


class ColourApplicator(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(ColourApplicator, self).__init__(parent)
        self.setWindowTitle("Colour Applicator")
        self.setFixedHeight(300)
        self.setFixedWidth(500)

        # Store values on startup for objects in the scene
        self.UNDO_LIST = []

        # Create the UI elements
        self.layout = QtWidgets.QVBoxLayout()

        # Object Selection Combo Box
        self.object_combobox = QtWidgets.QComboBox()
        self.object_combobox.currentIndexChanged.connect(self.update_selection)

        # Predefined colours setup
        self.predefined_colour_combo = QtWidgets.QComboBox()
        for k in COLOURS:
            self.predefined_colour_combo.addItem(k)

        # Buttons
        self.random_colour_radio = QtWidgets.QRadioButton("Random Colour")
        self.random_colour_radio.setChecked(True)
        self.predefined_colour_radio = QtWidgets.QRadioButton("Predefined Colour")
        self.set_colour_button = QtWidgets.QPushButton("Set Colour")
        self.set_colour_button.clicked.connect(lambda: set_object_colour(self.select_colour()),
                                                                         self.object_combobox.currentText())
        self.hierarchy_button = QtWidgets.QPushButton("Set Colour For Hierarchy")
        self.hierarchy_button.clicked.connect(lambda: set_hierarchy_colour(self.select_colour()),
                                                                           self.object_combobox.currentText())
        self.undo_button = QtWidgets.QPushButton("Undo")
        self.undo_button.clicked.connect(lambda: set_object_colour(*self.get_last_change()),
                                                                    self.object_combobox.currentText())

        # Add widgets to layout
        self.layout.addWidget(self.object_combobox)
        self.layout.addWidget(self.random_colour_radio)
        self.layout.addWidget(self.predefined_colour_radio)
        self.layout.addWidget(self.predefined_colour_combo)
        self.layout.addWidget(self.set_colour_button)
        self.layout.addWidget(self.hierarchy_button)
        self.layout.addWidget(self.undo_button)
        self.setLayout(self.layout)

        # Populate dropdown with user-created objects
        self.populate_objects()

    def populate_objects(self):
        """
        Find all user created objects in the scene and add them to the combo box
        :return None:
        """
        scene = FBSystem().Scene
        objects = [obj for obj in scene.Components if obj.ClassName() == 'FBModel']
        self.object_combobox.clear()
        self.object_combobox.addItem("-- Select Object --")
        for obj in objects:
            if obj.Name != 'Scene':
                self.object_combobox.addItem(obj.Name)

    def get_last_change(self):
        """
        Get the last change made from the UNDO_LIST to revert to it
        :rtype tuple
        :return colour, obj:
        """
        last_change = []
        if len(self.UNDO_LIST) > 1:
            last_change = self.UNDO_LIST[-2]
            del self.UNDO_LIST[-1]
        elif len(self.UNDO_LIST) == 1:
            last_change = self.UNDO_LIST[0]
        return last_change[1], last_change[0]

    def update_selection(self):
        """
        Update the object selected
        :rtype str
        :return selection:
        """
        return self.object_combobox.currentText()

    def select_colour(self, obj):
        """
        Select the colour at random or specifically from a predefined list
        :rtype str
        :return colour:
        """
        object_name, current_colour = self.check_object_colour(obj)
        if self.random_colour_radio.isChecked():
            if current_colour is None:
                colour = random_key(COLOURS)
            else:
                while True:
                    colour = random_key(COLOURS)
                    if colour != current_colour:
                        break
            self.UNDO_LIST.append([object_name, colour])
            return colour
        else:
            colour = self.predefined_colour_combo.currentText()
            self.UNDO_LIST.append([object_name, colour])
            return colour


# Create and show the dialog window
dialog = ColourApplicator()
dialog.show()
