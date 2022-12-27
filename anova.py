import os

from pandas import DataFrame
from bioinfokit.analys import stat
from statsmodels.formula.api import ols
from scipy.stats import shapiro
from numpy import seterr


class Anova(stat):
    def __init__(self, data: DataFrame, out_dir: str, *args, **kwargs):
        """ Initilize the anova class """

        self._out_dir = out_dir
        self._data = data

        super(stat, self).__init__(*args, **kwargs)

    @property
    def out_dir(self):
        return self.__out_dir

    @out_dir.setter
    def _out_dir(self, value: str):

        # If value is an existing directory, set out_dir to value
        if os.path.isdir(value):
            self.__out_dir = value
            self._out_file_path = os.path.join(self.out_dir, "out.dat")

        # Else if value exists but is not a directory, raise value error
        elif os.path.exists(value):
            raise ValueError(f"{value} is not a directory.")

        # If {value} directory does not exists, raise value error
        else:
            raise ValueError(f"{value} directory does not exist.")

    @property
    def out_file_path(self):
        return self._out_file_path

    @property
    def data(self):
        return self.__data

    @data.setter
    def _data(self, value: DataFrame):
        if type(value) is not DataFrame:
            raise TypeError("Only pandas.DataFrame data type is acceptable")

        self.__data = value

        # Reshape data and set columns name
        self.__reshaped_data = value.reset_index().melt(id_vars="index")
        self.__reshaped_data.columns = ["index", "treatments", "value"]

    @property
    def reshaped_data(self):
        return self.__reshaped_data

    def check_assumptions(self):
        """ Check normal distribution and homogeneity of data"""

        # Create model
        model = ols('value ~ C(treatments)', data=self.reshaped_data).fit()

        # Ignore "RuntimeWarning: divide by zero encountered in log"
        seterr(divide = "ignore")

        # Check normal distribution using scipy.stats.shapiro()
        shapiro_static, shapiro_pval = shapiro(model.resid)

        # Check homogeneity using bioinfokit.analys.stat
        self.bartlett(df=self.reshaped_data, res_var="value", xfac_var="treatments")
        self.levene(df=self.reshaped_data, res_var="value", xfac_var="treatments")

        # Warn "RuntimeWarning: divide by zero encountered in log"
        seterr(divide = "warn")

        # Write results to output file
        with open(self.out_file_path, "w") as out_file:
            out_file.write("-" * 20 + "\n")
            out_file.write("Shapiro-Wilk test summary (normal distribution):\n")
            out_file.write(f"{'Parameter':>26}{'Value':>8}\n")
            out_file.write(f"0{'static':>25}{float(shapiro_static):>8.4f}\n")
            out_file.write(f"1{'p-value':>25}{float(shapiro_pval):>8.4f}\n\n")

            out_file.write("Bartlett's test (homogeneity):\n")
            out_file.write(f"{self.bartlett_summary}\n\n")

            out_file.write("Levene's test (homogeneity):\n")
            out_file.write(f"{self.levene_summary}\n\n")

    def test(self):
        """ one-way ANOVA analysis on data and append summary to output file """

        # One-Way ANOVA
        self.anova_stat(df=self.reshaped_data, res_var="value", anova_model="value ~ C(treatments)")

        # Write result to output file
        with open(self.out_file_path, "a") as out_file:
            out_file.write("-" * 20 + "\n")
            out_file.write("One-Way ANOVA test:\n")
            out_file.write(f"{self.anova_summary}\n\n")

    def perform_tukey(self):
        """
        perform multiple pairwise comparison using Tukey's HSD/Kramer
        and append summary to output file
        """

        # Tukey
        self.tukey_hsd(df=self.reshaped_data, res_var="value", xfac_var="treatments", anova_model="value ~ C(treatments)")

        # Write result to output file
        with open(self.out_file_path, "a") as out_file:
            out_file.write("-" * 20 + "\n")
            out_file.write("Tukey multiple comparison test:\n")
            out_file.write(f"{self.tukey_summary}\n")
