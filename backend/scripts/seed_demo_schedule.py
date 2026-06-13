from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from sqlalchemy import select

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import SessionLocal
from app.modules.master_shifts.models import MasterShift
from app.modules.master_shifts.service import _generate_admin_shift_code
from app.modules.masters.models import Master


END_DATE = date(2028, 12, 31)
DEMO_NOTE = "Demo schedule seed"


@dataclass(frozen=True)
class DemoScheduleRule:
    master_id: int
    start_time: time
    end_time: time
    every_second_day: bool = False


DEMO_RULES = (
    DemoScheduleRule(
        master_id=1,
        start_time=time(15, 0),
        end_time=time(20, 0),
    ),
    DemoScheduleRule(
        master_id=2,
        start_time=time(10, 0),
        end_time=time(18, 0),
        every_second_day=True,
    ),
    DemoScheduleRule(
        master_id=3,
        start_time=time(9, 0),
        end_time=time(20, 0),
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed demo working schedules for existing masters."
    )
    parser.add_argument(
        "--start-date",
        type=parse_date,
        default=date.today(),
        help="First date to seed in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--end-date",
        type=parse_date,
        default=END_DATE,
        help="Last date to seed in YYYY-MM-DD format. Defaults to 2028-12-31.",
    )
    return parser.parse_args()


def parse_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"Invalid date '{value}'. Use YYYY-MM-DD."
        ) from exc


def iter_dates(start_date: date, end_date: date):
    for offset in range((end_date - start_date).days + 1):
        yield start_date + timedelta(days=offset)


def should_seed_day(
    day: date,
    start_date: date,
    rule: DemoScheduleRule,
) -> bool:
    if day.weekday() == 6:
        return False

    if rule.every_second_day:
        return (day - start_date).days % 2 == 0

    return True


def shift_matches_rule(shift: MasterShift, rule: DemoScheduleRule) -> bool:
    return (
        shift.status == "working"
        and shift.start_time == rule.start_time
        and shift.end_time == rule.end_time
        and shift.note == DEMO_NOTE
    )


def seed_demo_schedule(start_date: date, end_date: date) -> dict[str, int]:
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    stats = {
        "created": 0,
        "updated": 0,
        "skipped": 0,
        "missing_masters": 0,
        "duplicate_existing_rows": 0,
    }

    with SessionLocal() as db:
        masters_by_id = {
            master.id: master
            for master in db.scalars(
                select(Master).where(
                    Master.id.in_([rule.master_id for rule in DEMO_RULES])
                )
            ).all()
        }

        existing_by_master_date: dict[tuple[int, date], list[MasterShift]] = {}
        existing_shifts = db.scalars(
            select(MasterShift)
            .where(
                MasterShift.master_id.in_(
                    [rule.master_id for rule in DEMO_RULES]
                ),
                MasterShift.date >= start_date,
                MasterShift.date <= end_date,
            )
            .order_by(MasterShift.master_id, MasterShift.date, MasterShift.id)
        ).all()

        for shift in existing_shifts:
            existing_by_master_date.setdefault(
                (shift.master_id, shift.date),
                [],
            ).append(shift)

        for rule in DEMO_RULES:
            master = masters_by_id.get(rule.master_id)
            if master is None:
                stats["missing_masters"] += 1
                print(f"Master {rule.master_id}: not found, skipped")
                continue

            for day in iter_dates(start_date, end_date):
                if not should_seed_day(day, start_date, rule):
                    continue

                shift_code = _generate_admin_shift_code(
                    master=master,
                    shift_date=day,
                    status_value="working",
                    start_time=rule.start_time,
                )
                key = (rule.master_id, day)
                same_day_shifts = existing_by_master_date.get(key, [])

                if same_day_shifts:
                    if len(same_day_shifts) > 1:
                        stats["duplicate_existing_rows"] += (
                            len(same_day_shifts) - 1
                        )

                    shift = next(
                        (
                            existing_shift
                            for existing_shift in same_day_shifts
                            if existing_shift.shift_code == shift_code
                        ),
                        same_day_shifts[0],
                    )

                    if shift_matches_rule(shift, rule):
                        stats["skipped"] += 1
                        continue

                    shift.shift_code = shift_code
                    shift.status = "working"
                    shift.start_time = rule.start_time
                    shift.end_time = rule.end_time
                    shift.note = DEMO_NOTE
                    stats["updated"] += 1
                    continue

                shift = MasterShift(
                    shift_code=shift_code,
                    master_id=rule.master_id,
                    date=day,
                    status="working",
                    start_time=rule.start_time,
                    end_time=rule.end_time,
                    note=DEMO_NOTE,
                )
                db.add(shift)
                existing_by_master_date[key] = [shift]
                stats["created"] += 1

        db.commit()

    return stats


def main() -> None:
    args = parse_args()
    stats = seed_demo_schedule(args.start_date, args.end_date)

    print("Demo schedule seed complete")
    print(f"Date range: {args.start_date.isoformat()} to {args.end_date.isoformat()}")
    print("Masters affected: 1, 2, 3")
    print(f"Created: {stats['created']}")
    print(f"Updated: {stats['updated']}")
    print(f"Skipped unchanged: {stats['skipped']}")
    print(f"Missing masters: {stats['missing_masters']}")
    print(f"Pre-existing duplicate date rows noticed: {stats['duplicate_existing_rows']}")


if __name__ == "__main__":
    main()
