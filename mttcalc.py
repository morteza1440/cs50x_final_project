import os
import matplotlib.pyplot as plt


from warnings import filterwarnings
from sys import exit
from argparse import ArgumentParser, Namespace
from pandas import DataFrame, read_csv, melt
from seaborn import boxplot, swarmplot
from anova import Anova


def main():

    # Silent FutureWarning of bioinfokit module
    filterwarnings("ignore")

    # Process arguments
    args = process_args()

    # Calculate viablities
    viablities = calc_viabilities(args.path, args.out_dir)

    # Save plots figure
    try:
        if args.barchart_file_name:
            fig_path = os.path.join(args.out_dir, args.barchart_file_name)
            draw_barchart(viablities, fig_path, title=args.title, xlabel=args.xlabel, ylabel=args.ylabel, angle=args.angle)
        if args.boxplot_file_name:
            draw_boxplot(viablities, os.path.join(args.out_dir, args.boxplot_file_name))
    except PermissionError as error:
        exit(error)

    # Create Anova object
    try:
        anova = Anova(viablities, args.out_dir)
    except ValueError as error:
        # Exit if out_dir is not valid
        exit(error)

    # Check anova assumptions
    if args.check_assumptions:
        anova.check_assumptions()

    # One-Way ANOVA Test
    anova.test()

    # Pairwise multiple comparison, as anova post hoc
    if args.multiple_comparison:
        anova.perform_tukey()


def process_args() -> Namespace:
    """ Process sys.argv using argparse"""

    # Creat a parser
    parser = ArgumentParser(description="Statistical analysis of MTT assay data using one-way ANOVA.")

    # Add arguments
    parser.add_argument("path", help="path to the csv file containing absorbance reads")

    parser.add_argument("--barchart", dest="barchart_file_name", help="draw bar chart of data.")
    parser.add_argument("-t", "--title", help="title of bar chart.")
    parser.add_argument("-x", "--xlabel", help="label of x axes for bar chart.")
    parser.add_argument("-y", "--ylabel", help="label of y axes for bar chart.")
    parser.add_argument("-a", "--angle", default=0, type=float, help="x ticks rotation in bar chart.")

    parser.add_argument("--boxplot", dest="boxplot_file_name", help="draw box plot of data.")

    parser.add_argument("--check-assumptions", action="store_true", help="check normal distribution and homogeneity.")
    parser.add_argument("--multiple-comparison", action="store_true", help="tukey pairwise multiple comparison.")

    parser.add_argument("-o", "--out-dir", default=".", help="output directory, default is current directory.")

    # Check for valid csv format
    args = parser.parse_args()
    if args.path.endswith(".csv"):
        return args

    # If file is not in sv format, raise type error
    raise TypeError("File is not in csv format")


def calc_viabilities(path: str, out_dir: str) -> DataFrame:
    """ Calculate cell viabilities using absorbances and return it """

    # Read the absorbances from csv file
    try:
        absorbances = read_csv(path)
    except (PermissionError, FileNotFoundError) as error:
        exit(error)

    # Store the name of columns and then update them (add t and b in front of treatment and blank groups, respectively)
    old_col_names = list(absorbances.columns)
    absorbances.columns = get_new_col_names(absorbances)

    # Calculate the percentage of viabilities for each group of treatments
    # Formula: (absorbance of the treatment / mean of the related blanks) * 100
    viabilities = (absorbances.filter(regex="t.+", axis=1) / absorbances.filter(regex="b.+", axis=1).mean().to_numpy()) * 100

    # Set the name of each treatments groups, using the old column names
    viabilities.columns = old_col_names[::2]

    # Insert control column into viablities and set values to 100
    viabilities.insert(0, "Control", 100)

    # Save the viabilities into the viabilities.csv file in the provided path
    try:
        viabilities.round(2).to_csv(os.path.join(out_dir, "viabilities.csv"), index=False)
    except PermissionError as error:
        exit(error)

    # Return data
    return viabilities


def get_new_col_names(absorbances: DataFrame) -> list[str]:
    """ Change and then return the column names of the absorbances"""

    # Store previous column names
    col_names = list(absorbances.columns)

    # Accumulate new column names
    new_col_names = []

    for i in range(0, len(col_names), 2):

        # For each group of treatments,
        # add "t" to the first of the every other column names, starting from 0 index
        new_col_names.append(f"t{col_names[i]}")

        # For each group of controls (i.e., blanks),
        # add "b" to the first of the every other column names, starting from 1 index
        new_col_names.append(f"b{col_names[i + 1]}")

    return new_col_names


def set_ext(name: str) -> str:
    """ Set extention of file to png """

    # Set and return new file name
    path, pre_ext = os.path.splitext(name)
    return name if pre_ext == ".png" else path + ".png"


def draw_barchart(viabilities: DataFrame, path: str, **kwargs) -> None:
    """ Draw bar chart with error bar """

    # Store group name, mean and std deviation of each group
    group_names = list(viabilities.columns)
    viabilities_means = list(viabilities.mean())
    viabilities_sd = list(viabilities.std())

    # Get subplots
    fig, ax = plt.subplots()

    # Set title, labels and xticks angle
    ax.set_title(kwargs.get("title", ""))
    ax.set_xlabel(kwargs.get("xlabel", "Groups"))
    ax.set_ylabel(kwargs.get("ylabel", "Viablity (% of control)"))
    plt.xticks(rotation=kwargs.get("angle", 0.0))

    # Plot bar chart and configure bars color
    colors = ["gray"] * len(group_names)
    colors[0] = "black"
    ax.bar(group_names, viabilities_means, color=colors)

    # Plot error bars and configure error bar cap
    _, caplines, _ = ax.errorbar(group_names[1:], viabilities_means[1:],
                                 yerr=viabilities_sd[1:], color="black", lolims=True, ls="None")
    caplines[0].set_marker("_")
    caplines[0].set_markersize(20)

    # Save bar chart figure in a png file
    fig.savefig(set_ext(path))


def draw_boxplot(viablities: DataFrame, path: str) -> None:
    """ plot boxplot and swarmplot and save fig in a png file """

    # Reshape data
    reshaped_viablities = melt(viablities.reset_index(), id_vars=["index"], value_name="unique")
    reshaped_viablities.columns = ["index", "treatments", "value"]

    # Reset matplotlib figure
    plt.clf()

    # Draw plots using seaborn
    boxplot(x="treatments", y="value", data=reshaped_viablities, color="#99c2a2")
    swarmplot(x="treatments", y="value", data=reshaped_viablities, color="#7d0013")

    # Save the plot into a png file
    plt.savefig(set_ext(path))


if __name__ == "__main__":
    main()