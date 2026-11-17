from app.models import Order
from app.n_plus_one import report_eager, report_lazy, run_measured
from app.sql_counter import QueryCounter, detect_n_plus_one
from sqlalchemy import select


def test_lazy_report_has_n_plus_one(seeded):
    engine, factory = seeded
    _, qc = run_measured(engine, factory, report_lazy)
    assert qc.count > 60  # kamida har buyurtma uchun 1 ta qo'shimcha so'rov
    suspicious = detect_n_plus_one(qc.statements)
    assert suspicious and suspicious[0][1] >= 60


def test_eager_report_uses_two_queries(seeded):
    engine, factory = seeded
    _, qc = run_measured(engine, factory, report_eager)
    assert qc.count == 2
    assert detect_n_plus_one(qc.statements) == []


def test_both_reports_return_same_data(seeded):
    engine, factory = seeded
    lazy_rows, _ = run_measured(engine, factory, report_lazy)
    eager_rows, _ = run_measured(engine, factory, report_eager)
    assert lazy_rows == eager_rows and len(lazy_rows) == 60


def test_query_counter_detaches_listener(seeded):
    engine, factory = seeded
    with factory() as s:
        with QueryCounter(engine) as qc:
            s.scalars(select(Order)).all()
        before = qc.count
        s.scalars(select(Order)).all()
    assert qc.count == before


def test_detect_threshold():
    stmts = [("SELECT 1", ())] * 4 + [("SELECT 2", ())] * 5
    assert detect_n_plus_one(stmts, threshold=5) == [("SELECT 2", 5)]
