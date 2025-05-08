from lib import banner


def test_act():
    session_data = {"yo:lo"}
    observed = banner.act("datatable", session_data, {})
    expected = session_data, []
    assert observed == expected


def test_build_no_env():
    observed = banner.build()
    expected = {
        "body": '<div class="banner invisible">Environment name not set</div>',
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 200,
    }
    assert observed == expected


def test_build_with_env(mocker):
    mocker.patch("lib.banner.os.environ.get", return_value="test")
    observed = banner.build()
    expected = {
        "body": '<div class="banner">This is the test environment</div>',
        "multiValueHeaders": {"Content-Type": ["text/html"]},
        "statusCode": 200,
    }
    assert observed == expected
