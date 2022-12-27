from project import set_ext, draw_barchart, draw_boxplot, calc_viabilities, get_new_col_names
from pandas import DataFrame
from os import path, remove
from pytest import raises


# Creat a global dataframe for calc_viablities and get_new_col_names test
absorbances = DataFrame({"S1": [1, 2, 3], "B1": [4, 5, 6], "S2": [7, 8, 9], "B2":[10, 11, 12]})

# Creat global variables for draw_barchart and draw_boxplot tests
viablities = DataFrame({"A": [1, 2, 3], "B": [4, 5, 6], "C": [7, 8, 9]})
fig_name = "fig.png"


def test_set_ext():
    """ Test correct functionality of set_ext """

    # Test if there is a file name without path
    assert set_ext("name") == "name.png"

    # Test if there is a file name with path
    assert set_ext("/some/path/to/file/name") == "/some/path/to/file/name.png"


def test_calc_viabilities():
    """ Test the correct functionality of the calc_viabilities """

    # Creat a csv file from global dataframe
    absorbances.to_csv('path.csv', index=False)

    # Creat a dataframe
    viabilities = DataFrame({"Control": [100, 100, 100], "S1": [20.0, 40.0, 60.0], "S2": [63.64, 72.73, 81.82]})

    # Check correct functionality of calc_viabilities with provided data
    assert calc_viabilities("path.csv", "").round(2).equals(viabilities)
    assert path.exists("viabilities.csv")

    # Remove temporary created files
    remove("path.csv")
    remove("viabilities.csv")


def test_get_new_col_names():
    """ Test the correct functionality of the get_new_col_names """

    # Check correct functionality of get_new_col_names with global dataframe
    assert get_new_col_names(absorbances) == ["tS1", "bB1", "tS2", "bB2"]


def test_draw_barchart():
    """ test correct functionality and PermisionError raising """

    # Call function without title and labels
    draw_barchart(viablities, fig_name)

    # Check correct functionality
    assert path.exists(fig_name) == True
    remove(fig_name)

    # Call function with title and labels
    draw_barchart(viablities, fig_name, title="title", xlabel="xlabel", ylabel="ylabel", angle=20.0)

    # Check correct functionality
    assert path.exists(fig_name) == True
    remove(fig_name)

    # Check raises
    with raises((PermissionError, FileNotFoundError)):
        draw_barchart(viablities, path.join("/root", fig_name))


def test_draw_boxplot():
    """ test correct functionality and PermisionError raising """

    # Call function
    draw_boxplot(viablities, fig_name)

    # Check correct functionality
    assert path.exists(fig_name) == True

    # Delete fing.png
    remove(fig_name)

    # Check raises
    with raises((PermissionError, FileNotFoundError)):
        draw_boxplot(viablities, path.join("/root", fig_name))
