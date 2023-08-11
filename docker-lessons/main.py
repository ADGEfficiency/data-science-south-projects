import datetime
import pathlib


def save_data_to_volume():
    stamp = datetime.datetime.now().isoformat()
    print(stamp)
    pathlib.Path("/data/output.txt").write_text(stamp)


if __name__ == "__main__":
    save_data_to_volume()
