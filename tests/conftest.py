from functools import partial

import pytest

from finance import create_app
from finance.models import Account, Asset
from finance.models import db as _db


@pytest.fixture(scope='module')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
    }
    app = create_app(__name__, config=settings_override)

    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app


@pytest.fixture(scope='module')
def db(app, request):
    """Session-wide test database."""
    def teardown():
        _db.drop_all()

    _db.app = app
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture(scope='function')
def account_checking(request, db):
    account = Account.create(type='checking', name='Shinhan Checking')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='function')
def account_hf(request, db):
    account = Account.create(type='virtual', name='어니스트펀드')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='function')
def account_sp500(request, db):
    account = Account.create(type='investment', name='S&P500 Fund')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='module')
def asset_hf1(request, db):
    asset = Asset.create(
        type='bond', name='포트폴리오 투자상품 1호')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_krw(request, db):
    asset = Asset.create(
        type='currency', name='KRW', description='Korean Won')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_sp500(request, db):
    asset = Asset.create(
        type='security', name='S&P 500', description='')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


def teardown(db, record):
    db.session.delete(record)
    db.session.commit()
