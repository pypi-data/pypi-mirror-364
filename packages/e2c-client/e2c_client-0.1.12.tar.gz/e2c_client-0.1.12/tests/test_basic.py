from nmapper import nmapper
import pytest

@pytest.fixture(scope="module")
def dummy_nmapper():
    # print("making dummy student")
    return nmapper.Nmapper()

def test_instance(dummy_nmapper):
    # nm = nmapper.Nmapper()
    nm = dummy_nmapper
    assert nm.APP_NAME == "nmapper"


class TestSettings:
    def test_settings_exist(self, dummy_nmapper):
        # nm = nmapper.Nmapper()
        nm = dummy_nmapper
        assert nm.settings is not None

    @pytest.mark.skip(reason="Not particularly useful")
    def test_settings_attempts_int(self, dummy_nmapper):
        # nm = nmapper.Nmapper()
        nm = dummy_nmapper
        with pytest.raises(TypeError) as exc_info:
            assert nm.attempts > 0
        print(str(exc_info))


