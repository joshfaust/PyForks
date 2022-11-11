from PyForks.region import Region
import pytest
import os
import pandas as pd


def test_nonexistant_region():
    region = Region()
    assert region.is_valid_region(region="bullcrap_region") == False


def test_existant_region():
    region = Region()
    assert region.is_valid_region(region="buck-hill-52165") == True


def test_check_bad_region():
    region = Region()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        region.check_region("fake_004957856934")
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_check_good_region():
    region = Region()
    check = region.check_region("lebanon-hills")
    assert check == True


def test_get_region_info():
    region = Region()
    check = region._get_region_info("lebanon-hills")
    assert isinstance(check, dict)


def test_ridelogcount_download_auth_fail():
    region = Region()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        region.download_region_ridecounts("west-lake-marion-park")
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_trails_download_auth_fail():
    region = Region()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        region.download_all_region_trails("west-lake-marion-park", "20367")
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_ridelogs_download_auth_fail():
    region = Region()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        region.download_all_region_ridelogs("west-lake-marion-park")
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_ridelogcount_download_lowpriv_user():
    region = Region(username="apress001", password="FakePassword123")
    region.login()
    download_result = region.download_region_ridecounts("west-lake-marion-park")
    assert isinstance(download_result, pd.DataFrame)


def test_trails_download_lowpriv_user():
    region = Region(username="apress001", password="FakePassword123")
    region.login()
    download_result = region.download_all_region_trails(
        "west-lake-marion-park", "20367"
    )
    assert isinstance(download_result, pd.DataFrame)


def test_ridelogs_download_lowpriv_user():
    region = Region(username="apress001", password="FakePassword123")
    region.login()
    download_result = region.download_all_region_ridelogs("west-lake-marion-park")
    assert isinstance(download_result, pd.DataFrame)
