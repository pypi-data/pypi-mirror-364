import os
import pandas as pd
from datetime import datetime
from .utils import to_datetime, progress_bar
from .const import RATIO_NAMES, BAND_NAMES, FREQ_BANDS
from obspy import UTCDateTime, Stream, read
from obspy.clients.fdsn import Client as FDSNClient
from multiprocessing import Pool


class TremorData:
    """Tremor data class."""

    def __init__(
        self,
        station: str,
        channel: str,
        network: str = "VG",
        location: str = "00",
        eruptive_file: str = None,
        current_dir: str = None,
        n_jobs: int = 2,
        cleanup_temp_dir: bool = False,
        verbose: bool = False,
        debug: bool = False,
    ):
        self.station = station.upper()
        self.channel = channel.upper()
        self.network = network.upper()
        self.location = location.upper()
        self.eruptive_file = eruptive_file
        self.current_dir = current_dir
        self.n_jobs = n_jobs
        self.cleanup_temp_dir = cleanup_temp_dir
        self.verbose = verbose
        self.debug = debug

        if debug:
            print("===!! Debug Mode is set to True !!===")
            print("======================================")

        # Add additional attributes
        self.df = pd.DataFrame()
        self.nslc = f"{network}.{station}.{location}.{channel}"
        self.tmp_dir = os.path.join(os.getcwd(), "_tmp", self.nslc)

        self.output_dir = os.path.join(self.current_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.columns = (
            RATIO_NAMES
            + [f"{ratio_name}_filtered" for ratio_name in RATIO_NAMES]
            + BAND_NAMES
            + [f"{band_name}_filtered" for band_name in BAND_NAMES]
        )

        # Replace default value
        if current_dir is None:
            self.current_dir = os.getcwd()
        if eruptive_file is None:
            self.eruptive_file = os.path.join(
                self.current_dir, "input", f"{self.nslc}_eruptive_periods.txt"
            )

        # Attributes from method
        self.start_date = None
        self.end_date = None

        # Validating variable
        self.validate()

        if verbose:
            print(f":: Station: {self.nslc}")
            print(f":: Current Dir: {self.current_dir}")
            print(f":: Eruption file: {self.eruptive_file}")
            print(f":: Number of jobs: {self.n_jobs}")
            print(f":: Columns: {self.columns}")

    def validate(self):
        # Ensuring eruptive_file exists
        assert os.path.isfile(self.eruptive_file), ValueError(
            f"❌ {self.eruptive_file} does not exist."
        )

        # Create empty tremor data file if not exists

        self.df = df

        if len(self.df) > 0:
            self.start_date = self.df.index[0]
            self.end_date = self.df.index[-1]

        if self.debug:
            print(f"🔨 DataFrame located in: {self.tremor_data_file}")
            print(f"🔨 Length of DataFrame: {len(self.df)}")

    def load_tremor_data(self, tremor_data_file: str = None) -> pd.DataFrame:
        if tremor_data_file is None:
            # Replace self.tremor_data_file
            tremor_data_filename = f"{self.nslc}_tremor_data.csv"
            tremor_data_file = os.path.join(self.output_dir, tremor_data_filename)

        if not os.path.isfile(tremor_data_file):
            df = pd.DataFrame(columns=self.columns)
            df.to_csv(tremor_data_file, index_label="time")

            return df

        return pd.read_csv(
            tremor_data_file,
            index_col="time",
            parse_dates=True,
            infer_datetime_format=True,
        )

    def update(
        self, start_date: str, end_date: str, n_jobs: int = None, sds_dir: str = None
    ):
        """Update tremor data with start and end dates."""
        start_date_str = start_date
        end_date_str = end_date
        start_date = to_datetime(start_date)
        end_date = to_datetime(end_date)

        # Ensuring end date greater than start date
        assert start_date < end_date, ValueError(
            f"❌ Start date: {start_date_str} must before end date: {end_date_str}."
        )

        # Ensuring SDS directory exists
        if sds_dir is not None:
            assert os.path.exists(sds_dir), IsADirectoryError(
                f"❌ SDS dir: {sds_dir} does not exist."
            )

        # Replacing current n_jobs
        if n_jobs is None:
            n_jobs = self.n_jobs

        # Build parallels jobs
        n_days = (end_date - start_date).days
        parallels = [
            [job_id, start_date, self.nslc, sds_dir] for job_id in range(n_days)
        ]

        if self.debug:
            print(f"🔨 Parallels: {len(parallels)}")

        if self.verbose:
            print(f"ℹ️ Update data using n_jobs={n_jobs}")
            print("=" * 50)

        # Ensuring Temp directory exists
        os.makedirs(self.tmp_dir, exist_ok=True)

        if n_jobs == 1:
            for parallel in parallels:
                job_id = parallel[0]
                progress_bar(
                    current_iteration=job_id + 1,
                    total=n_days,
                    prefix=f"Job id: {job_id}",
                )
        else:
            print("Using parallel")

    def temp_file(self, job_id: int, temp_dir: str = None) -> (bool, str):
        """Get temporary file"""
        if temp_dir is None:
            temp_dir = self.tmp_dir

        filename = f"_tmp_fl_{job_id:05d}.csv"
        csv_path = os.path.join(temp_dir, filename)

        # Skip if temporary file exists
        if os.path.isfile(csv_path):
            if self.verbose:
                print(f"✅ Temp file exists :: {csv_path}")
            return True, csv_path

        return False, None

    def read_from_sds(self, date: UTCDateTime, nslc: str, sds_dir: str) -> Stream:
        utc_datetime = UTCDateTime(date)
        network, station, location, channel = nslc.split(".")

        year = utc_datetime.year
        julian_day = utc_datetime.strftime("%j")
        channel_type = f"{channel}.D"

        filename = f"{network}.{station}.{location}.{channel}.{channel_type}.{year}.{julian_day}"

        # SDS Path
        miniseed_file = os.path.join(
            sds_dir,
            str(year),
            network,
            station,
            f"{channel}.{channel_type}",
            filename,
        )

        # Checking file exists
        if not os.path.isfile(miniseed_file):
            print(f"❌ File not found :: {miniseed_file}")
            return Stream()

        # Load miniseed
        try:
            st = read(miniseed_file, format="MSEED")
            return st
        except ValueError as e:
            print(f"❌ Cannot read file {miniseed_file} :: {e}")
            return Stream()

    def stream(
        self, job_id: int, start_date: datetime, nslc: str, sds_dir: str = None
    ) -> None:
        """Download data from FDSN or SDS."""
        # Check temp file, skip download if file exists
        exists, tmp_path = self.temp_file(job_id)
        if exists:
            return None

        # stream =
        return None
