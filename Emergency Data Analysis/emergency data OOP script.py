import numpy as np
import pandas as pd

# Duration of Leave
class EmergencyData:
    """create a data frame and compute duration of leave with some statistics"""

    def __init__(self, emergency_data_file, visit_date, discharge_date):
        """create"""
        self.data = self._creating_data_frame(emergency_data_file)
        self.duration_of_leave = self._computing_duration_of_leave(
            self.data, visit_date, discharge_date
        )
        self.duration_of_leave_statistics = (
            self._computing_duration_of_leave_statistics(self.duration_of_leave)
        )
        self.percentage_of_duration_specific_hours = (
            self._percentage_durations_less_than_four_hours(self.duration_of_leave)
        )
        self.percentage_of_duration_within_10_20_30_minutes = (
            self._percentage_duration_within_10_20_30_minutes(self.duration_of_leave)
        )

    def _creating_data_frame(self, file):
        """create data frame"""
        self.df = pd.read_excel(file)
        return self.df

    def _computing_duration_of_leave(self, df, col1, col2):
        """compute duration of leave"""
        self.df["DURATION_OF_LEAVE"] = df[col2] - df[col1]
        return self.df["DURATION_OF_LEAVE"]

    def _computing_duration_of_leave_statistics(self, series):
        """compute basic statistics"""
        self.stats = pd.DataFrame(series.describe())
        return self.stats

    def _percentage_durations_less_than_four_hours(self, series):
        """compute percentage of leave duration for patients who left less than or within and more than four hours"""
        less_than_four_hours = round(
            series[series < "0 days 4:00:00"].shape[0] / series.shape[0] * 100
        )
        more_than_or_equal_four_hours = round(
            series[series >= "0 days 4:00:00"].shape[0] / series.shape[0] * 100
        )

        self.df = pd.DataFrame(
            [str(less_than_four_hours) + "%", str(more_than_or_equal_four_hours) + "%"],
            index=["Less than four hours", "More than four hours"],
            columns=["Percentage"],
        ).transpose()
        return self.df

    def _percentage_duration_within_10_20_30_minutes(self, series):
        """compute percentage of leave duration within specific times"""
        within_10_minutes = round(
            series[series <= "0 days 00:10:00"].shape[0] / series.shape[0] * 100
        )
        within_20_minutes = round(
            series[series <= "0 days 00:20:00"].shape[0] / series.shape[0] * 100
        )
        within_30_minutes = round(
            series[series <= "0 days 00:30:00"].shape[0] / series.shape[0] * 100
        )

        self.df = pd.DataFrame(
            [
                str(within_10_minutes) + "%",
                str(within_20_minutes) + "%",
                str(within_30_minutes) + "%",
            ],
            index=["within_10_minutes", "within_20_minutes", "within_30_minutes"],
            columns=["Percentage"],
        ).transpose()
        return self.df


class AnlyzingFeature:
    """
    Analyzing the following features:
    - Consultations
    - Lab Tests
    - Radilogy
    - Pharmach

    """

    def __init__(self, data, feature):
        """create variables which can give us specific value/s"""
        self.single_feature = self._get_feature(data, feature)
        self.series_without_null_vals = self._ignore_null_values(self.single_feature)
        self.vals_as_lst = self._split_text(self.series_without_null_vals)
        self.order_counts_df = self._find_length_text(self.vals_as_lst, feature)
        self.lst_len_orders = self._compute_length(self.vals_as_lst)
        self.lst_dates_times = self._extract_dates_times(self.vals_as_lst)
        self.duration = self._compute_durations(self.lst_dates_times)
        self.unique_no = self._unique_of_length_or_duration_stat(self.lst_len_orders)
        self.duration_stats = self._unique_of_length_or_duration_stat(self.duration)

    def _get_feature(self, df, column_name):
        """get feature from dataframe"""
        series = df.data[column_name]
        return series

    def _ignore_null_values(self, series):
        """ignore null values"""
        mask = series.isna()
        series = series[~mask]
        return series

    def _split_text(self, series):
        """split each order in the series"""
        series_with_lsts = series.apply(lambda x: x.split(";"))
        return series_with_lsts

    def _find_length_text(self, series, column_name):
        """compute number of orders for each patient to find frequent of orders"""
        series_number = series.apply(lambda x: len(x)).value_counts()
        frequent_orders_df = pd.DataFrame(series_number).rename(
            columns={str(column_name): "Frquent"}
        )
        return frequent_orders_df

    def _compute_length(self, series):
        """find length of each order"""
        len_orders = series.apply(lambda x: [len(n) for n in x])
        return len_orders

    def _unique_of_length_or_duration_stat(self, series):
        """
        find length of text and count of orders as well as date time
        with and without Reply or End "Invalid Value" and duration statistics
        """
        total_lst = []
        for lst in series:
            total_lst.extend(lst)

        if str(series) != str(self.duration):
            if self.single_feature.name == "CONSULTATIONS":
                num = 47
            else:
                num = 58

            len_of_text = pd.Series(total_lst).unique()

            len_without_reply = len([n for n in total_lst if n < num])
            len_with_reply = len([n for n in total_lst if n == num])

            per_without_reply = (
                str(
                    round(len([n for n in total_lst if n < num]) / len(total_lst) * 100)
                )
                + "%"
            )
            per_with_reply = (
                str(
                    round(
                        len([n for n in total_lst if n == num]) / len(total_lst) * 100
                    )
                )
                + "%"
            )

            try:
                without_with_reply_details = pd.DataFrame(
                    [
                        (len_of_text[1], len_of_text[0]),
                        (len_without_reply, len_with_reply),
                        (per_without_reply, per_with_reply),
                    ],
                    columns=['Without Reply/End"Invalid Value', "With Reply/End"],
                    index=[
                        'Length of Text "Characters"',
                        "Count of consultations",
                        "Percentage of consultations",
                    ],
                )
                return without_with_reply_details

            except:

                without_with_reply_details = pd.DataFrame(
                    [
                        len_of_text,
                        (len_without_reply, len_with_reply),
                        (per_without_reply, per_with_reply),
                    ],
                    columns=["With Reply/End", 'Without Reply/End "Invalid Value"'],
                    index=[
                        'Length of Text "Characters"',
                        "Count of consultations",
                        "Percentage of consultations",
                    ],
                )
                return without_with_reply_details
        else:
            return pd.DataFrame(pd.Series(total_lst).describe(), columns=["Statistics"])

    def _extract_dates_times(self, series):
        """extract dates and times for all orders"""
        if self.single_feature.name == "CONSULTATIONS":
            series_date_time = series.apply(
                lambda x: [x[i][8:25] + "  " + x[i][31:] for i in range(len(x))]
            )
            return series_date_time

        else:
            series_date_time = series.apply(lambda x: " ".join(x).split("START: ,")[1:])
            return series_date_time

    def _compute_durations(self, series):
        """compute durations by subtract Reply or End date time from Request or Start date time"""
        if self.single_feature.name == "CONSULTATIONS":
            series_durations = series.apply(
                lambda x: [
                    pd.to_datetime(x[i][19:], errors="coerce", dayfirst=True)
                    - pd.to_datetime(x[i][:16], errors="coerce", dayfirst=True)
                    for i in range(len(x))
                ]
            )
            return series_durations

        else:

            series_durations = series.apply(
                lambda x: [
                    pd.to_datetime(x[i][24:40], dayfirst=True)
                    - pd.to_datetime(x[i][:16], dayfirst=True)
                    for i in range(len(x))
                ]
            )
            return series_durations


if __name__ == "__main__":

    # define variables
    _file = "emergency_data.xlsx"
    visit_date = "VISIT_DATE"
    discharge_date = "DISCHARGE_DATE"
    consultations = "CONSULTATIONS"
    lab_tests = "LAB_TEST"
    radilogy = "RADIOLOGY"
    pharmacy = "PHARMECY"

    # specify class of EmergencyData with three arguments file, visist_date and discharge_date
    duration_of_leave = EmergencyData(_file, visit_date, discharge_date)

    # compute duration of leave
    duration_of_leave.duration_of_leave

    # duration of leave "statistics"
    duration_of_leave.duration_of_leave_statistics

    # Percentage of patients who left an emergency department within less or more than and equals four hours
    duration_of_leave.percentage_of_duration_specific_hours

    # Percentage of patients who left an emergency department within specific times
    duration_of_leave.percentage_of_duration_within_10_20_30_minutes

    # ------------------------
    # Analyzing Consultaions |
    # ------------------------
    # specify class of AnalyzingFeature with two arguments consulatioans and duration of leave for inheratencing variables and methods
    consultations = AnlyzingFeature(duration_of_leave, consultations)

    # consulations feature with null values
    consultations.single_feature

    # consulations feature without null values
    consultations.series_without_null_vals

    # consulations feature each order seperated for others
    consultations.vals_as_lst

    # Only dates and times for each order
    consultations.lst_dates_times

    # lenght of text for each order
    consultations.lst_len_orders

    # frequents for each consultation count
    consultations.order_counts_df

    # all orders with and without replies"Invalid values"
    consultations.unique_no

    # compute durations for each order
    consultations.duration

    # consultations statistics
    consultations.duration_stats

    # ---------------------
    # Analyzing Lab Tests|
    # ---------------------

    lab_tests = AnlyzingFeature(duration_of_leave, lab_tests)

    # lab_tests feature with null values
    lab_tests.single_feature

    # lab_tests feature without null values
    lab_tests.series_without_null_vals

    # lab_tests feature each order seperated for others
    lab_tests.vals_as_lst

    # Only dates and times for each order
    lab_tests.lst_dates_times

    # lenght of text for each order
    lab_tests.lst_len_orders

    # frequents for each lab tests count
    lab_tests.order_counts_df

    # all orders with and without replies"Invalid values"
    lab_tests.unique_no

    # compute durations for each order
    lab_tests.duration

    # lab tests statistics
    lab_tests.duration_stats

    # --------------------
    # Analyzing Radiolgy |
    # --------------------

    # create an radiology object
    radilogy = AnlyzingFeature(duration_of_leave, radilogy)

    # radilogy feature with null values
    radilogy.single_feature

    # radilogy feature without null values
    radilogy.series_without_null_vals

    # radilogy feature each order seperated for others
    radilogy.vals_as_lst

    # Only dates and times for each order
    radilogy.lst_dates_times

    # lenght of text for each order
    radilogy.lst_len_orders

    # frequents for each radilogy count
    radilogy.order_counts_df

    # all orders with and without replies"Invalid values"
    radilogy.unique_no

    # compute durations for each order
    radilogy.duration

    # radilogy statistics
    radilogy.duration_stats

    # ---------------------
    # Analyzing Pharmacy |
    # ---------------------

    # create a pharmacy object
    pharmacy = AnlyzingFeature(duration_of_leave, pharmacy)

    # pharmacy feature with null values
    pharmacy.single_feature

    # pharmacys feature without null values
    pharmacy.series_without_null_vals

    # pharmacys feature each order seperated for others
    pharmacy.vals_as_lst

    # Only dates and times for each order
    pharmacy.lst_dates_times

    # lenght of text for each order
    pharmacy.lst_len_orders

    # frequents for each pharmacy count
    pharmacy.order_counts_df

    # all orders with and without replies"Invalid values"
    pharmacy.unique_no

    # compute durations for each order
    pharmacy.duration

    # pharmacy statistics
    pharmacy.duration_stats
