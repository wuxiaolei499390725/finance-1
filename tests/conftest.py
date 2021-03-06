from functools import partial
import os

import pytest
from typedecorator import setup_typecheck

from finance import create_app
from finance.models import (
    Account, Asset, CurrencyAsset, FundAsset, Portfolio, P2PBondAsset,
    StockAsset)
from finance.models import db as _db


setup_typecheck()


@pytest.fixture(scope='module')
def app(request):
    """Session-wide test `Flask` application."""
    settings_override = {
        'TESTING': True,
    }
    settings_override['SQLALCHEMY_DATABASE_URI'] = os.environ['TEST_DB_URL']
    app = create_app(__name__, config=settings_override)

    # Establish an application context before running the tests.
    # ctx = app.app_context()
    # ctx.push()

    # def teardown():
    #     ctx.pop()

    # request.addfinalizer(teardown)
    return app


@pytest.fixture
def testapp(app, db):
    with app.app_context():
        yield app.test_client()


@pytest.fixture(scope='module', autouse=True)
def db(app, request):
    """Session-wide test database."""
    def teardown():
        with app.app_context():
            _db.session.close()
            _db.drop_all()

    request.addfinalizer(teardown)

    _db.app = app
    with app.app_context():
        _db.create_all()

        yield _db


@pytest.fixture(scope='function')
def account_checking(request, db):
    account = Account.create(type='checking', name='신한은행 입출금')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='function')
def account_savings(request, db):
    account = Account.create(type='savings', name='신한은행 적금')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='function')
def account_8p(request, db):
    account = Account.create(type='virtual', name='8퍼센트')
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


@pytest.fixture(scope='function')
def account_stock(request, db):
    account = Account.create(type='investment', name='신한 주식')
    request.addfinalizer(partial(teardown, db=db, record=account))
    return account


@pytest.fixture(scope='module')
def asset_hf1(request, db):
    asset = P2PBondAsset.create(
        name='포트폴리오 투자상품 1호')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    assert asset.type == 'p2p_bond'
    return asset


@pytest.fixture(scope='module')
def asset_krw(request, db):
    asset = CurrencyAsset.create(
        name='KRW', description='Korean Won')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_sp500(request, db):
    asset = FundAsset.create(
        name='KB Star S&P500', description='',
        data={'code': 'KR5223941018'})
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_usd(request, db):
    asset = CurrencyAsset.create(
        name='USD', description='United States Dollar')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_stock_ncsoft(request, db):
    asset = StockAsset.create(
        name='NCsoft Corporation', code='036570.KS',
        description='NCsoft Corporation',
        data={'bps': 88772, 'eps': 12416})
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='module')
def asset_stock_nvda(request, db):
    asset = StockAsset.create(
        name='NVDA', code='NVDA', isin='US67066G1040',
        description='NVIDIA Corporation')
    request.addfinalizer(partial(teardown, db=db, record=asset))
    return asset


@pytest.fixture(scope='function')
def portfolio(request, db, asset_krw, account_checking, account_sp500):
    p = Portfolio.create(base_asset=asset_krw)
    p.add_accounts(account_checking, account_sp500)

    def teardown():
        # NOTE: The following statement is necessary because the scope of
        # `asset_krw` is a module, whereas the scope of `p` is a function.
        p.base_asset = None
        db.session.delete(p)
        db.session.commit()

    request.addfinalizer(teardown)
    return p


def teardown(db, record):
    db.session.delete(record)
    db.session.commit()
