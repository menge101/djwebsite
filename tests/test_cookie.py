from datetime import datetime, timedelta, timezone
from pytest import fixture, mark, raises
from lib import cookie


@fixture
def domain():
    return "example.com"


@fixture
def expiration():
    return datetime(year=2025, month=1, day=1, hour=0, minute=0, second=0, tzinfo=timezone.utc)


@fixture
def expiration_as_str(expiration):
    return expiration.strftime("%a, %d %b %Y %H:%M:%S GMT")


@fixture
def name():
    return "test"


@fixture
def value():
    return "yolo"


def test_simple(name, value):
    observed = cookie.Cookie(name, value)
    expected = f"{name}={value}"
    assert str(observed) == expected


def test_domain(domain, name, value):
    observed = cookie.Cookie(name, value, domain=domain)
    expected = f"{name}={value}; Domain={domain}"
    assert str(observed) == expected


def test_expires(expiration, expiration_as_str, name, value):
    observed = cookie.Cookie(name, value, expires=expiration)
    expected = f"{name}={value}; Expires={expiration_as_str}"
    assert str(observed) == expected


def test_http_only(name, value):
    observed = cookie.Cookie(name, value, http_only=True)
    expected = f"{name}={value}; HttpOnly"
    assert str(observed) == expected


def test_max_age(name, value):
    observed = cookie.Cookie(name, value, max_age=3600)
    expected = f"{name}={value}; Max-Age=3600"
    assert str(observed) == expected


def test_partitioned(name, value):
    observed = cookie.Cookie(name, value, partitioned=True)
    expected = f"{name}={value}; Partitioned"
    assert str(observed) == expected


def test_path(name, value):
    observed = cookie.Cookie(name, value, path="/yolo")
    expected = f"{name}={value}; Path=/yolo"
    assert str(observed) == expected


def test_secure(name, value):
    observed = cookie.Cookie(name, value, secure=True)
    expected = f"{name}={value}; Secure"
    assert str(observed) == expected


@mark.parametrize(
    "samesite,expectation",
    [
        ("Strict", "Strict"),
        ("Lax", "Lax"),
        ("None", "None"),
    ],
)
def test_same_site(expectation, name, samesite, value):
    observed = cookie.Cookie(name, value, same_site=samesite, secure=True)
    expected = f"{name}={value}; Secure; SameSite={expectation}"
    assert str(observed) == expected


def test_same_site_invalid(name, value):
    with raises(ValueError):
        cookie.Cookie(name, value, same_site="yolo")


def test_same_site_insecure(name, value):
    with raises(ValueError):
        cookie.Cookie(name, value, same_site="None")


def test_expiration_time(expiration, mocker):
    test_setup_time = expiration - timedelta(seconds=100)
    datetime_mock = mocker.patch("lib.cookie.datetime")
    datetime_mock.now.return_value = test_setup_time
    assert cookie.expiration_time(100) == expiration


def test_expiration_as_ttl(expiration):
    assert cookie.expiration_as_ttl(expiration) == 1735689600
