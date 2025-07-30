import pandas as pd
import numpy as np

# Add filepath
def load_csv_file(filepath):
    """
    Reads a CSV file into a pandas DataFrame and converts specific columns 
    into appropriate datetime or time-of-day formats. It assumes the following columns 
    are present in the CSV: 'start_time', 'end_time', 'start_date', 'end_date', 
    'start_time_of_day', and 'end_time_of_day'.

    Parameters:
        filepath (str): Path to the CSV file.
    Returns:
        pd.DataFrame: DataFrame with parsed datetime, date, and time-of-day columns.
    
    Notes:
        - Datetime conversion uses `errors="coerce"` for 'start_time' and 'end_time',
          so invalid values will become NaT.
        - 'start_date' and 'end_date' are converted to `datetime.date` objects.
        - 'start_time_of_day' and 'end_time_of_day' must follow the format '%H:%M:%S'.
    """
    df = pd.read_csv(filepath)
    # Converting into datetime
    df['start_time'] = pd.to_datetime(df['start_time'], errors="coerce")
    df['end_time'] = pd.to_datetime(df['end_time'], errors="coerce")
    # Keep as dates
    df['start_date'] = pd.to_datetime(df['start_date']).dt.date
    df['end_date'] = pd.to_datetime(df['end_date']).dt.date
    # Show only time of day (hour, min, sec)
    df['start_time_of_day'] = pd.to_datetime(df['start_time_of_day'], format = '%H:%M:%S').dt.time
    df['end_time_of_day'] = pd.to_datetime(df['end_time_of_day'], format = '%H:%M:%S').dt.time
    
    return df

class SleepFeaturesExtractor:
    def __init__(self, df: pd.DataFrame, verbose=False, filter_verbose=False):
        self.df = df
        self.verbose = verbose
        self.filter_verbose = filter_verbose

    # ----------------------------------------------------------------------------------------------------------------------------
    # Filtering functions

    def _filter(self, **kwargs):
        """
        Filter the DataFrame based on one or more column-value conditions.
        
        Each keyword argument specifies a column name and the value(s) to filter by. 
        If the value is a list, the method filters rows where the column's value is in the list.

        Parameters:
            **kwargs: Column-value pairs to filter the DataFrame by.

        Returns:
            pd.DataFrame: A filtered copy of the original DataFrame.

        Raises:
            ValueError: If any specified column does not exist in the DataFrame.
        """
        if self.filter_verbose:
            print(f"Filtering with: {kwargs}")
        # Checking if the input columns exist in the dataframe
        missing_cols = [col for col in kwargs if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing columns in dataframe: {missing_cols}.")

        df = self.df.copy()
        for col, val in kwargs.items():
            df = df[df[col].isin(val) if isinstance(val, list) else df[col] == val]
        return df
    
    def get_sleep_stage_data(self, participant_id=None, day_number=None, sleep_stage_state=None):
        """
        Retrieve rows from the DataFrame that match the given participant ID, day number, 
        and/or sleep stage state.

        This is a convenience method that filters sleep stage data based on one or more 
        of the provided parameters.

        Parameters:
            participant_id (int or str, optional): ID of the participant to filter by.
            day_number (int, optional): Experimental or recorded day number.
            sleep_stage_state (str or int, optional): Sleep stage label (e.g., "REM", "Light", 1, 2, etc.).

        Returns:
            pd.DataFrame: A filtered DataFrame containing rows that match the provided criteria.

        """
        filters = {}
        if participant_id is not None:
            filters["participant_id"] = participant_id
        if day_number is not None:
            filters["day_number"] = day_number
        if sleep_stage_state is not None:
            filters["sleep_stage_state"] = sleep_stage_state
        return self._filter(**filters)
    
    def get_participant_day_data(self, participant_id, day_number):
        """
        Retrieve data for a specific participant on a given day.

        This method filters the internal DataFrame to return all rows matching the 
        given participant ID and day number. Raises an error if no such data exists.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to filter by.

        Returns:
            pd.DataFrame: A filtered DataFrame containing the participant's data for that day.

        Raises:
            AssertionError: If `participant_id` or `day_number` is not an integer.
            ValueError: If no matching data is found for the given inputs.
        """
        assert isinstance(participant_id, int), f"participant_id input has to be an integer!"
        assert isinstance(day_number, int), f"day_number input has to be an integer!"

        df = self._filter(participant_id=participant_id, day_number=day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")

        return df

    # ----------------------------------------------------------------------------------------------------------------------------
    # Feature functions

    def compute_bedtime(self, participant_id, day_number):
        """
        Compute the bedtime for a given participant on a specific day.

        This method retrieves the participant's data for the given day and returns 
        the 'start_time' value from the first row, which is assumed to represent bedtime.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute bedtime for.

        Returns:
            pd.Timestamp: The bedtime as a pandas Timestamp.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        or if the bedtime value is missing (NaT).
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assumes the bedtime will be the first row
        bedtime = df["start_time"].iloc[0]

        if pd.isnull(bedtime):
            raise ValueError(f"Bedtime is missing for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Bedtime for participant {participant_id} on day {day_number}: {bedtime}")

        return bedtime
    
    def compute_risetime(self, participant_id, day_number):
        """
        Compute the risetime for a given participant on a specific day.

        This method retrieves the participant's data for the given day and returns 
        the 'end_time' value from the last row, which is assumed to represent risetime.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute risetime for.

        Returns:
            pd.Timestamp: The risetime as a pandas Timestamp.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        or if the risetime value is missing (NaT).
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assumes risetime will be the last row
        risetime = df["end_time"].iloc[-1]

        if pd.isnull(risetime):
            raise ValueError(f"Risetime is missing for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Risetime for participant {participant_id} on day {day_number}: {risetime}")

        return risetime
    
    def compute_tib_minutes(self, participant_id, day_number):
        """
        Compute Time In Bed (TIB) in minutes for a given participant on a specific day.

        TIB is defined as the sum of durations between the first recorded start time 
        (assumed to be bedtime) and the last recorded end time (assumed to be risetime) 
        for the specified day. Rows outside this range are excluded from the calculation.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute TIB for.

        Returns:
            float: Total time in bed in minutes.

        Raises:
            ValueError: If no data is found for the given participant and day,
                        if bedtime is after or equal to risetime,
                        or if either bedtime or risetime is missing.
        
        Notes:
            - Assumes bedtime corresponds to the first row's 'start_time',
            and risetime to the last row's 'end_time'.
            - TIB is calculated by summing the 'duration_minutes' of rows 
            within the bedtime-to-risetime interval.
        """
        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        # Assuming bedtime is first row in data for specific night and
        # that risetime is the last recorded time
        bedtime = df["start_time"].iloc[0]
        risetime = df["end_time"].iloc[-1]

        if bedtime >= risetime:
            raise ValueError(f"Invalid time range: bedtime >= risetime for participant {participant_id} on day {day_number}.")

        if pd.isnull(bedtime) or pd.isnull(risetime):
            raise ValueError(f"Missing bedtime or risetime for participant {participant_id} on day {day_number}.")
        
        df = df[(df["start_time"] >= bedtime) & (df["end_time"] <= risetime)]

        tib = df["duration_minutes"].sum(skipna=True)
        
        if self.verbose:
            print(f"Time In Bed (TIB) for participant {participant_id} on day {day_number}: {tib} minutes")

        return tib
    
    def compute_sleep_onset_time(self, participant_id, day_number):
        """
        Compute the sleep onset time for a participant on a specific day.

        Sleep onset time is defined as the start time of the first recorded 
        sleep stage classified as "light", "deep", or "REM".

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute sleep onset time for.

        Returns:
            pd.Timestamp: The timestamp when the participant first enters sleep.

        Raises:
            ValueError: If no sleep stage data is found for the given participant and day,
                        or if the sleep onset time is missing (NaT).
        
        Notes:
            - Sleep onset is identified as the earliest occurrence of a sleep stage 
            labeled "light", "deep", or "REM".
            - Data is assumed to be sorted chronologically by start time.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        sleep_onset_time = df["start_time"].iloc[0]

        if pd.isnull(sleep_onset_time):
            raise ValueError(f"Missing data for sleep onset time for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Sleep onset time for participant {participant_id} on day {day_number}: {sleep_onset_time}")
        
        return sleep_onset_time
    
    def compute_wake_time(self, participant_id, day_number):
        """
        Compute the wake time for a participant on a specific day.

        Wake time is defined as the end time of the last recorded 
        sleep stage classified as "light", "deep", or "REM".

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute wake time for.

        Returns:
            pd.Timestamp: The timestamp when the participant last exits a sleep stage.

        Raises:
            ValueError: If no sleep stage data is found for the given participant and day,
                        or if the wake time value is missing (NaT).
        
        Notes:
            - Wake time is determined as the `end_time` of the last qualifying sleep stage.
            - Assumes sleep stages are chronologically ordered.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        wake_time = df["end_time"].iloc[-1]

        if pd.isnull(wake_time):
            raise ValueError(f"Missing data for calculating wake up time for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Wake time for participant {participant_id} on day {day_number}: {wake_time}")

        return wake_time
    
    def compute_tst_minutes(self, participant_id, day_number):
        """
        Compute Total Sleep Time (TST) in minutes for a participant on a specific day.

        TST is calculated as the sum of all durations spent in recognized sleep stages:
        "light", "deep", or "REM". Wake and unknown states are excluded.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute TST for.

        Returns:
            float: Total sleep time in minutes.

        Raises:
            ValueError: If no valid sleep stage data is found for the given participant and day,
                        or if TST is zero or missing.
        
        Notes:
            - Assumes sleep stages are already classified and labeled in the data.
            - Uses the 'duration_minutes' column for calculation.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")

        # Sums up the duration of hours where participant is in a sleep stage       
        tst = df["duration_minutes"].sum(skipna=True)

        if pd.isnull(tst) or tst == 0:
            raise ValueError(f"TST could not be computed for participant {participant_id} on day {day_number}, missing data...")

        if self.verbose:
            print(f"Total Sleep Time (TST) for participant {participant_id} on day {day_number}: {tst} minutes")

        return tst
    
    def compute_midpoint_sleep(self, participant_id, day_number):
        """
        Compute the midpoint of sleep for a participant on a specific day.

        The sleep midpoint is calculated as the halfway point between 
        sleep onset and wake time. This metric can be used to infer 
        chronotype or sleep phase timing.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the midpoint for.

        Returns:
            pd.Timestamp: The midpoint of the participant's sleep period.

        Raises:
            ValueError: If sleep onset or wake time cannot be computed.
        
        Notes:
            - Relies on `compute_sleep_onset_time` and `compute_wake_time`.
            - Assumes both onset and wake times are valid and timezone-consistent.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)

        midpoint = sleep_onset + (wake_time - sleep_onset) / 2

        if self.verbose:
            print(f"Midpoint of sleep for participant {participant_id} on day {day_number}: {midpoint}")

        return midpoint
    
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Architecture

    def compute_time_in_sleep_stage_minutes(self, participant_id, day_number, sleep_stage_state):
        """
        Compute the total time spent in a specific sleep stage for a participant on a given day.

        This method filters sleep stage data by participant ID, day number, and the 
        specified sleep stage, and sums the total duration in minutes.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.
            sleep_stage_state (str or list[str]): The sleep stage(s) to include 
                (e.g., "REM", "deep", "light", or a list of them).

        Returns:
            float: Total time spent in the specified sleep stage(s), in minutes.

        Raises:
            ValueError: If no matching sleep stage data is found for the given inputs.

        Notes:
            - The duration is computed from the 'duration_minutes' column.
            - Accepts either a single sleep stage as a string or a list of stages.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id,
                                       day_number=day_number,
                                       sleep_stage_state=sleep_stage_state)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        duration = df["duration_minutes"].sum(skipna=True)

        if self.verbose:
            print(f"Time in stage '{sleep_stage_state}' for participant {participant_id} on day {day_number}: {duration:.2f} minutes")
        
        return duration
    
    def compute_time_light_sleep(self, participant_id, day_number):
        """
        Compute total time spent in light sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of light sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="light")
    

    def compute_time_deep_sleep(self, participant_id, day_number):
        """
        Compute total time spent in deep sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of deep sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="deep")
    

    def compute_time_rem_sleep(self, participant_id, day_number):
        """
        Compute total time spent in REM sleep for a participant on a specific day.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Total duration of REM sleep in minutes.
        """
        return self.compute_time_in_sleep_stage_minutes(participant_id=participant_id, day_number=day_number, sleep_stage_state="rem")
    
    def compute_percentage_sleep_stage_of_tst(self, participant_id, day_number, sleep_stage_state):
        """
        Compute the percentage of Total Sleep Time (TST) spent in a specific sleep stage.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.
            sleep_stage_state (str or list[str]): The sleep stage(s) to include 
                (e.g., "REM", "deep", "light", or a list of them).

        Returns:
            float: Percentage of TST spent in the specified sleep stage(s).

        Raises:
            ValueError: If TST or sleep stage duration cannot be computed.

        Notes:
            - This value is calculated as: (time_in_stage / TST) * 100.
            - TST includes only "light", "deep", and "REM" stages.
        """
        tst = self.compute_tst_minutes(participant_id, day_number)
        time_in_sleep_stage = self.compute_time_in_sleep_stage_minutes(participant_id, day_number, sleep_stage_state)

        pct_time_spent_in_sleep_stage = time_in_sleep_stage / tst * 100
        
        if self.verbose:
            print(f"Time in TST spent in {sleep_stage_state} for participant {participant_id} on day {day_number}: {pct_time_spent_in_sleep_stage:.2f}%")
        
        return pct_time_spent_in_sleep_stage
        

    def compute_percentage_light_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in light sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in light sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="light")
    
    def compute_percentage_deep_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in deep sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in deep sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="deep")
    
    def compute_percentage_rem_sleep(self, participant_id, day_number):
        """
        Compute the percentage of Total Sleep Time (TST) spent in REM sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Percentage of TST spent in REM sleep.
        """
        return self.compute_percentage_sleep_stage_of_tst(participant_id, day_number, sleep_stage_state="rem")
    
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Continuity (Fragmentation)

    def compute_waso_minutes(self, participant_id, day_number):
        """
        Compute Wake After Sleep Onset (WASO) in minutes for a participant on a specific day.

        WASO is defined as the total time spent awake between sleep onset and final wake time.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute WASO for.

        Returns:
            float: Total duration of wakefulness after sleep onset, in minutes.

        Raises:
            ValueError: If no awake data is found in the sleep period,
                        or if WASO is missing or zero.

        Notes:
            - Sleep onset is determined by the first occurrence of "light", "deep", or "REM".
            - Wake time is the end of the last such sleep stage.
            - Only "awake" stages occurring between these two times are included in WASO.
        """
        sleep_onset_time = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)
        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        df = df[(df["start_time"] >= sleep_onset_time) & (df["start_time"] < wake_time)]
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        waso = df["duration_minutes"].sum(skipna=True)

        if pd.isnull(waso) or waso == 0:
            raise ValueError(f"WASO could not be computed for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"WASO for participant {participant_id} on day {day_number}: {waso} minutes")

        return waso
    
    def compute_num_awakenings(self, participant_id, day_number):
        """
        Compute the number of awakenings during the sleep period for a participant on a specific day.

        An awakening is defined as any "awake" stage that occurs between sleep onset and the final wake time,
        excluding the final wake episode.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            int: Number of discrete awakenings during the sleep period.

        Raises:
            ValueError: If the number of awakenings cannot be computed (e.g., due to missing data).

        Notes:
            - Sleep onset is the start of the first "light", "deep", or "REM" stage.
            - Wake time is the end of the last such sleep stage.
            - Awake stages occurring entirely within this window are counted.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_up_time = self.compute_wake_time(participant_id, day_number)

        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        # Exlcudes the final wake if the last recorded sleep stage is "awake"
        df = df[(df["start_time"] >= sleep_onset) & (df["end_time"] < wake_up_time)]

        num_awakenings = len(df)
        if pd.isnull(num_awakenings):
            raise ValueError(f"Could not compute the number of awakenings for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Number of awakenings for participant {participant_id} on day {day_number}: {num_awakenings}")

        return num_awakenings
    
    def compute_avg_duration_awakenings(self, participant_id, day_number):
        """
        Compute the average duration of awakenings during the sleep period for a participant on a specific day.

        Only "awake" stages occurring between sleep onset and final wake time are considered.
        The final wake episode is excluded.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Average duration of awakenings in minutes.

        Raises:
            ValueError: If no qualifying awakenings are found,
                        or if duration data is missing.

        Notes:
            - Sleep onset is the first occurrence of a "light", "deep", or "REM" stage.
            - Wake time is the end of the last such stage.
            - Only durations of awakenings within this window are included.
        """
        sleep_onset = self.compute_sleep_onset_time(participant_id, day_number)
        wake_time = self.compute_wake_time(participant_id, day_number)

        df = self.get_sleep_stage_data(participant_id=participant_id, day_number=day_number, sleep_stage_state="awake")
        df = df[(df["start_time"] >= sleep_onset) & (df["start_time"] < wake_time)]

        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        if df["duration_minutes"].count() == 0:
            raise ValueError(f"Could not compute average duration of awkenings for participant {participant_id} on day {day_number}.")

        avg_duration_awakenings = df["duration_minutes"].mean()

        if self.verbose:
            print(f"Average duration of awakenings for participant {participant_id} on day {day_number}: {avg_duration_awakenings:.2f} minutes")

        return avg_duration_awakenings
    
    def compute_sleep_frag_index(self, participant_id, day_number):
        """
        Compute the Sleep Fragmentation Index for a participant on a specific day.

        The Sleep Fragmentation Index is calculated as the number of awakenings divided by Total Sleep Time (TST),
        representing the frequency of sleep interruptions.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Sleep Fragmentation Index (awakenings per minute of sleep).

        Raises:
            ValueError: If the index cannot be computed due to missing data.

        Notes:
            - A higher index indicates more fragmented sleep.
            - TST includes only "light", "deep", and "REM" sleep.
            - The final awakening at the end of sleep is excluded from the count.
        """
        num_awakenings = self.compute_num_awakenings(participant_id, day_number)
        tst = self.compute_tst_minutes(participant_id, day_number)

        sleep_frag_index = num_awakenings / tst

        if pd.isnull(sleep_frag_index):
            raise ValueError(f"Could not compute sleep fragmentation index for participant {participant_id} on day {day_number}.")
        
        if self.verbose:
            print(f"Sleep Fragmentation Index for participant {participant_id} on day {day_number}: {sleep_frag_index:.2f}")

        return sleep_frag_index
        
    # ----------------------------------------------------------------------------------------------------------------------------
    # Sleep Efficiency and Quality

    def compute_sleep_efficiency(self, participant_id, day_number):
        """
        Compute the sleep efficiency for a participant on a specific day.

        Sleep efficiency is defined as the percentage of Time In Bed (TIB) spent asleep,
        calculated as (TST / TIB) * 100.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute the metric for.

        Returns:
            float: Sleep efficiency as a percentage.

        Raises:
            ValueError: If participant data is missing or TST/TIB cannot be computed.

        Notes:
            - TST (Total Sleep Time) includes only "light", "deep", and "REM" stages.
            - TIB is the duration from bedtime to risetime.
            - A higher sleep efficiency indicates more consolidated sleep.
        """
        tst = self.compute_tst_minutes(participant_id, day_number)
        tib = self.compute_tib_minutes(participant_id, day_number)

        df = self.get_participant_day_data(participant_id, day_number)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id} on day {day_number}.")
        
        sleep_efficiency = tst / tib * 100

        if self.verbose:
            print(f"Sleep effiency (% of time in bed spent asleep) for participant {participant_id} on day {day_number}: {sleep_efficiency:.2f}%")

        return sleep_efficiency
    
    def compute_sleep_onset_reg(self, participant_id):
        """
        Compute sleep onset regularity (circular standard deviation) for a participant across all days.

        This metric quantifies how consistent a participant's sleep onset times are from day to day,
        using circular statistics to account for the 24-hour cycle.

        Parameters:
            participant_id (int): The ID of the participant.

        Returns:
            float: Sleep onset regularity, expressed as the circular standard deviation in minutes.

        Raises:
            ValueError: If less than two valid onset times are available for the participant.

        Notes:
            - Converts each sleep onset time to an angle on the 24-hour clock.
            - Uses the length of the mean resultant vector (R) to compute circular std dev.
            - A lower value indicates more consistent sleep onset timing.
            - Days with missing or invalid sleep onset times are skipped.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id, sleep_stage_state=["light", "deep", "rem"])
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")
        
        days = df["day_number"].unique()
        angles = []
        
        for day in days:
            try:
                onset_time = self.compute_sleep_onset_time(participant_id, day)
                minutes = onset_time.hour * 60 + onset_time.minute + onset_time.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing time.")
                continue

        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute onset regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)
        
        onset_std_minutes = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))

        if self.verbose:
            print(f"Sleep Onset Regularity for participant {participant_id}: {onset_std_minutes:.2f} minutes")
        
        return onset_std_minutes
    
    def compute_wake_time_reg(self, participant_id):
        """
        Compute wake time regularity (circular standard deviation) for a participant across all days.

        This metric quantifies how consistent a participant's wake times are day-to-day,
        accounting for the circular nature of time over a 24-hour cycle.

        Parameters:
            participant_id (int): The ID of the participant.

        Returns:
            float: Wake time regularity, expressed as the circular standard deviation in minutes.

        Raises:
            ValueError: If fewer than two valid wake times are available for the participant.

        Notes:
            - Each wake time is converted into an angle on a 24-hour circle.
            - Regularity is computed using the length of the mean resultant vector (R).
            - A smaller value indicates more consistent wake timing across days.
            - Days with invalid or missing wake times are skipped.
        """
        df = self.get_sleep_stage_data(participant_id=participant_id)
        if df.empty:
            raise ValueError(f"No data found for participant {participant_id}.")
        
        days = df["day_number"].unique()
        angles = []
        
        for day in days:
            try:
                wake_time = self.compute_wake_time(participant_id, day)
                minutes = wake_time.hour * 60 + wake_time.minute + wake_time.second / 60
                angle = 2 * np.pi * (minutes / 1440)
                angles.append(angle)
            except ValueError:
                if self.verbose:
                    print(f"Skipping day {day} due to missing time.")
                continue

        if len(angles) < 2:
            raise ValueError(f"Not enough valid sleep data to compute wake time regularity for participant {participant_id}.")
        
        sin_sum = np.sum(np.sin(angles))
        cos_sum = np.sum(np.cos(angles))
        R = np.sqrt(sin_sum**2 + cos_sum**2) / len(angles)

        wake_time_std_minutes = np.sqrt(-2 * np.log(R)) * (1440 / (2 * np.pi))
        
        if self.verbose:
            print(f"Wake Time Regularity for participant {participant_id}: {wake_time_std_minutes:.2f} minutes")

        return wake_time_std_minutes
    
    # ----------------------------------------------------------------------------------------------------------------------------
    # Computing several features at once

    def compute_sleep_timing_functions(self, participant_id, day_number):
        """
        Compute a set of core sleep timing metrics for a participant on a specific day.

        This method aggregates key temporal features related to sleep, including bedtime,
        risetime, time in bed (TIB), sleep onset and wake time, total sleep time (TST),
        and midpoint of sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute timing metrics for.

        Returns:
            dict or None:
                A dictionary with the following keys (values may be None if unavailable):
                    - "bedtime" (pd.Timestamp or None)
                    - "risetime" (pd.Timestamp or None)
                    - "tib_minutes" (float or None)
                    - "sleep_onset_time" (pd.Timestamp or None)
                    - "wake_time" (pd.Timestamp or None)
                    - "tst_minutes" (float or None)
                    - "midpoint_sleep" (pd.Timestamp or None)

                Returns None if none of the metrics can be computed.

        Notes:
            - If an individual metric cannot be computed (e.g., due to missing data),
            its value will be None.
            - Use `self.verbose = True` to log skipped metrics.
            """
        features = {}

        for name, function in [
            ("bedtime", self.compute_bedtime),
            ("risetime", self.compute_risetime),
            ("tib_minutes", self.compute_tib_minutes),
            ("sleep_onset_time", self.compute_sleep_onset_time),
            ("wake_time", self.compute_wake_time),
            ("tst_minutes", self.compute_tst_minutes),
            ("midpoint_sleep", self.compute_midpoint_sleep),
        ]:
            try:
                features[name] = function(participant_id, day_number)
            except ValueError as e:
                if self.verbose:
                    print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
                features[name] = None
            
        return features if any(v is not None for v in features.values()) else None

    def compute_sleep_architecture_features(self, participant_id, day_number):
        """
        Compute sleep architecture metrics for a participant on a specific day.

        This method calculates both absolute and relative durations of different sleep stages,
        including light, deep, and REM sleep.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute architecture metrics for.

        Returns:
            dict or None:
                A dictionary with the following keys (values may be None if unavailable):
                    - "time_in_light_sleep" (float or None): Minutes spent in light sleep.
                    - "time_in_deep_sleep" (float or None): Minutes spent in deep sleep.
                    - "time_in_rem_sleep" (float or None): Minutes spent in REM sleep.
                    - "pct_light_sleep" (float or None): % of TST spent in light sleep.
                    - "pct_deep_sleep" (float or None): % of TST spent in deep sleep.
                    - "pct_rem_sleep" (float or None): % of TST spent in REM sleep.

                Returns None if none of the metrics can be computed.

        Notes:
            - If a specific sleep stage is missing or TST cannot be computed, the corresponding
            value will be None.
            - Use `self.verbose = True` to log individual feature-level errors.
        """
        features = {}

        for name, function in [
            ("time_in_light_sleep", self.compute_time_light_sleep),
            ("time_in_deep_sleep", self.compute_time_deep_sleep),
            ("time_in_rem_sleep", self.compute_time_rem_sleep),
            ("pct_light_sleep", self.compute_percentage_light_sleep),
            ("pct_deep_sleep", self.compute_percentage_deep_sleep),
            ("pct_rem_sleep", self.compute_percentage_rem_sleep),
        ]:
            try:
                features[name] = function(participant_id, day_number)
            except ValueError as e:
                if self.verbose:
                    print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
                features[name] = None

        return features if any(v is not None for v in features.values()) else None

    def compute_sleep_continuity_features(self, participant_id, day_number):
        """
        Compute sleep continuity metrics for a participant on a specific day.

        This method calculates features related to how fragmented or uninterrupted the sleep is.
        It includes time awake after sleep onset, the number and duration of awakenings,
        and a sleep fragmentation index.

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute continuity metrics for.

        Returns:
            dict or None:
                A dictionary containing:
                    - "waso_minutes" (float or None): Wake After Sleep Onset in minutes.
                    - "num_awakenings" (int or None): Number of awakening episodes.
                    - "avg_awake_duration" (float or None): Average duration of awakenings in minutes.
                    - "sleep_frag_index" (float or None): Sleep fragmentation index (awakenings per TST minute).
                Returns None if all metrics fail to compute.

        Notes:
            - Each metric is computed independently. Failures in one do not prevent others.
            - Metrics may be None if data is missing or an error occurs.
            - Set `self.verbose = True` to enable logging of any skipped metrics.
        """
        features = {}

        for name, function in [
            ("waso_minutes", self.compute_waso_minutes),
            ("num_awakenings", self.compute_num_awakenings),
            ("avg_awake_duration", self.compute_avg_duration_awakenings),
            ("sleep_frag_index", self.compute_sleep_frag_index),
        ]:
            try:
                features[name] = function(participant_id, day_number)
            except ValueError as e:
                print(f"Skipping {name} for participant {participant_id} on day {day_number}: {e}.")
            features[name] = None
        return features if any(v is not None for v in features.values()) else None
        
    def compute_sleep_efficiency_and_regularity(self, participant_id, day_number):
        """
        Compute sleep efficiency and regularity metrics for a participant.

        This method returns a mix of within-day and across-day sleep quality measures, including:
        - Sleep efficiency (per day)
        - Sleep onset regularity (across days)
        - Wake time regularity (across days)

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute sleep efficiency for.

        Returns:
            dict: A dictionary containing the following keys:
                - "sleep_efficiency" (float or None): % of time in bed spent asleep on the given day.
                - "sleep_onset_regularity" (float or None): Circular std deviation of sleep onset time across days.
                - "wake_time_regularity" (float or None): Circular std deviation of wake time across days.

        Notes:
            - Any metric that cannot be computed due to missing or insufficient data is returned as None.
            - Verbose mode will print debug messages for skipped metrics.
        """
        features = {}

        # Per-day metric
        try:
            features["sleep_efficiency"] = self.compute_sleep_efficiency(participant_id, day_number)
        except ValueError as e:
            if self.verbose:
                print(f"Skipping sleep efficiency for {participant_id} on day {day_number}: {e}")
            features["sleep_efficiency"] = None

        # Across-day metrics
        try:
            features["sleep_onset_regularity"] = self.compute_sleep_onset_reg(participant_id)
        except ValueError as e:
            if self.verbose:
                print(f"Skipping sleep onset regularity for {participant_id}: {e}")
            features["sleep_onset_regularity"] = None

        try:
            features["wake_time_regularity"] = self.compute_wake_time_reg(participant_id)
        except ValueError as e:
            if self.verbose:
                print(f"Skipping wake time regularity for {participant_id}: {e}")
            features["wake_time_regularity"] = None

        return features
    
    def compute_all_features(self, participant_id, day_number):
        """
        Compute and aggregate all sleep features for a participant on a specific day.

        This method compiles metrics from four major domains:
        - Sleep timing
        - Sleep architecture
        - Sleep continuity
        - Sleep efficiency and regularity

        Parameters:
            participant_id (int): The ID of the participant.
            day_number (int): The day number to compute features for.

        Returns:
            dict or None: A dictionary containing all computed features, including:
                - "participant_id" (int)
                - "day_number" (int)
                - Plus flattened key-value pairs from each feature domain.
            Returns None if all feature sections fail (i.e., no data available).

        Notes:
            - Each section may return None if underlying data is missing or insufficient.
            - Section results are flattened into a single dictionary for downstream analysis.
        """
        features = {
            "participant_id": participant_id,
            "day_number": day_number,
        }
        # Compute section-wise features
        sections = {
            "timing": self.compute_sleep_timing_functions(participant_id, day_number),
            "architecture": self.compute_sleep_architecture_features(participant_id, day_number),
            "continuity": self.compute_sleep_continuity_features(participant_id, day_number),
            "efficiency": self.compute_sleep_efficiency_and_regularity(participant_id, day_number)
        }

        # If all sections returned None, treat as missing data
        if all(section is None for section in sections.values()):
            return None

        # Flatten sections into top-level keys
        for section_dict in sections.values():
            if section_dict is not None:
                features.update(section_dict)

        return features