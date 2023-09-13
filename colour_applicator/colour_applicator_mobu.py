from pyfbsdk import *
import pythonidelib

from colour_applicator.colour_applicator_ui import COLOURS
from colour_applicator.colour_applicator_utilities import find_key


def mobu_print(string):
    """
    Printing to console does not work, so this is used for debugging
    :param string:
    :return:
    """
    print(string)
    pythonidelib.FlushOutput()


def set_object_colour(colour, obj):
    """
    Set new colour of the selected object
    :param colour:
    :param obj:
    :return None:
    """
    obj = FBFindModelByLabelName(obj)
    if obj:
        material = obj.Materials[0]
        if material:
            colour_values = COLOURS[colour]
            diffuse_color = FBColor(colour_values[0], colour_values[1], colour_values[2])
            material.Diffuse = diffuse_color


def check_object_colour(obj):
    """
    Check the current colour of the selected object
    :param obj:
    :rtype tuple
    :return selected_object, colour:
    """
    obj = FBFindModelByLabelName(obj)
    if obj:
        material = obj.Materials[0]
        diffuse_prop = material.PropertyList.Find('DiffuseColor')
        return obj, find_key(COLOURS, diffuse_prop.Data)


def get_object_hierarchy(obj, obj_list):
    """
    Take object and loop through the children
    :param list obj_list:
    :param obj:
    :rtype list
    :return materials:
    """
    obj_list.append(obj)
    for child in obj.Children:
        get_object_hierarchy(child, obj_list)


def set_hierarchy_colour(colour, obj):
    """
    Set Colour for materials on hierarchy of selected object
    :param obj:
    :param colour:
    :return None:
    """
    obj = FBFindModelByLabelName(obj)
    obj_list = []
    get_object_hierarchy(obj, obj_list)
    for obj in obj_list:
        set_object_colour(colour, obj.Name)