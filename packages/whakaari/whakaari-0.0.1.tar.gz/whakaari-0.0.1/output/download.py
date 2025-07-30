import os
from .utils import to_datetime, progress_bar
from obspy import UTCDateTime, Stream, read


class Download:
    """Tremor data class."""

    def __init__(
        self,
        station: str,
        channel: str,
        network: str = "VG",
        location: str = "00",
        download_dir: str = None,
        verbose: bool = False,
        debug: bool = False,
    ):
        self.station = station.upper()
        self.channel = channel.upper()
        self.network = network.upper()
        self.location = location.upper()
        self.download_dir = download_dir
        self.verbose = verbose
        self.debug = debug

        if debug:
            print("===!! Debug Mode is set to True !!===")
            print("======================================")

        # Add additional attributes
        self.nslc = f"{network}.{station}.{location}.{channel}"

        # Replace default value
        if download_dir is None:
            self.download_dir = os.path.join(os.getcwd(), "download")
            os.makedirs(self.download_dir, exist_ok=True)

        self.sds_dir = os.path.join(self.download_dir, "sds")
        os.makedirs(self.sds_dir, exist_ok=True)

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

    # def download(self, start_date: str, end_date: str, sds_dir: str = None):
