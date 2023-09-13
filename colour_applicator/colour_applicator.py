import PySide2.QtWidgets as QtWidgets
import random
from pyfbsdk import *
import pythonidelib


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


def mobu_print(string):
    """
    Printing to console does not work, so this is used for debugging
    :param string:
    :return:
    """
    print(string)
    pythonidelib.FlushOutput()


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
        self.set_colour_button.clicked.connect(lambda: self.set_object_colour(self.select_colour()))
        self.hierarchy_button = QtWidgets.QPushButton("Set Colour For Hierarchy")
        self.hierarchy_button.clicked.connect(lambda: self.set_hierarchy_colour(self.select_colour()))
        self.undo_button = QtWidgets.QPushButton("Undo")
        self.undo_button.clicked.connect(lambda: self.set_object_colour(*self.get_last_change()))

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

    def select_colour(self):
        """
        Select the colour at random or specifically from a predefined list
        :rtype str
        :return colour:
        """
        object_name, current_colour = self.check_object_colour()
        if self.random_colour_radio.isChecked():
            if current_colour is None:
                colour = self.random_key(COLOURS)
            else:
                while True:
                    colour = self.random_key(COLOURS)
                    if colour != current_colour:
                        break
            self.UNDO_LIST.append([object_name, colour])
            return colour
        else:
            colour = self.predefined_colour_combo.currentText()
            self.UNDO_LIST.append([object_name, colour])
            return colour

    def random_key(self, dictionary):
        """
        Select a random key from a dictionary
        :param dictionary:
        :return key:
        """
        keys = list(dictionary.keys())
        random_key = random.choice(keys)
        return random_key

    def set_object_colour(self, colour, obj=None):
        """
        Set new colour of the selected object
        :param colour:
        :param obj:
        :return None:
        """
        if obj:
            obj = FBFindModelByLabelName(obj)
        else:
            selected_object = self.object_combobox.currentText()
            obj = FBFindModelByLabelName(selected_object)
        if obj:
            material = obj.Materials[0]
            if material:
                colour_values = COLOURS[colour]
                diffuse_color = FBColor(colour_values[0], colour_values[1], colour_values[2])
                material.Diffuse = diffuse_color

    def check_object_colour(self, obj=None):
        """
        Check the current colour of the selected object
        :param obj:
        :rtype tuple
        :return selected_object, colour:
        """
        selected_object = None
        if not obj:
            selected_object = self.object_combobox.currentText()
            obj = FBFindModelByLabelName(selected_object)
        if obj:
            material = obj.Materials[0]
            diffuse_prop = material.PropertyList.Find('DiffuseColor')
            return selected_object, self.find_key(COLOURS, diffuse_prop.Data)

    def find_key(self, dictionary, value):
        """
        Given a dictionary and value, return the key
        :param dictionary:
        :param value:
        :return key:
        """
        for key, val in dictionary.items():
            if val == value:
                return key
        return None

    def get_object_hierarchy(self, obj, obj_list):
        """
        Take object and loop through the children
        :param list obj_list:
        :param obj:
        :rtype list
        :return materials:
        """
        obj_list.append(obj)
        for child in obj.Children:
            self.get_object_hierarchy(child, obj_list)

    def set_hierarchy_colour(self, colour):
        """
        Set Colour for materials on hierarchy of selected object
        :param colour:
        :return None:
        """
        selected_object = self.object_combobox.currentText()
        obj = FBFindModelByLabelName(selected_object)
        obj_list = []
        self.get_object_hierarchy(obj, obj_list)
        for obj in obj_list:
            self.set_object_colour(colour, obj.Name)


# Create and show the dialog window
dialog = ColourApplicator()
dialog.show()
