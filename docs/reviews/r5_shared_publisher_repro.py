"""Synthetic BUG006 probe; requires installed R5 packages and matching public test helpers."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import threading

PUBLISHER = None
FOREIGN = None
PRODUCER_ERRORS = []


def calculate(task, batches):
    from equity_feature_workers.commands import compute_session_inputs

    def submit():
        try:
            PUBLISHER.submit(FOREIGN.task, compute_session_inputs(FOREIGN.task, FOREIGN.batches))
        except Exception as error:
            PRODUCER_ERRORS.append(type(error).__name__)

    producer = threading.Thread(target=submit)
    producer.start()
    producer.join()
    return compute_session_inputs(task, batches)


def main():
    global PUBLISHER, FOREIGN
    parser = argparse.ArgumentParser()
    parser.add_argument('--worker-tests', required=True, type=Path)
    parser.add_argument('--sink', required=True, choices=['parquet', 'duckdb'])
    args = parser.parse_args()
    sys.path.insert(0, str(args.worker_tests.resolve()))
    from test_supervisor import work
    from test_publication import sink_for, SCOPE
    from equity_feature_example_extensions.sink import LIMITS
    from equity_feature_workers import BoundedSupervisor, SerialPublisher, PublicationLimits
    from equity_feature_workers.commands import compute_session_inputs
    from equity_feature_io_sdk import prepare_publication, idempotency_key

    primary, _ = work('A', calculate)
    FOREIGN, _ = work('B')
    with tempfile.TemporaryDirectory() as temporary, sink_for(args.sink, Path(temporary)) as sink:
        PUBLISHER = SerialPublisher(sink, SCOPE, limits=PublicationLimits(), requirements=LIMITS)
        outcome = BoundedSupervisor().run((primary,), publisher=PUBLISHER)
        envelope = prepare_publication(
            compute_session_inputs(FOREIGN.task, FOREIGN.batches),
            destination_scope=FOREIGN.task.destination_scope,
            generation_id=FOREIGN.task.generation_id,
            job_id=FOREIGN.task.job_id,
            partition_id=FOREIGN.task.partition_id,
            limits=LIMITS,
        )
        print(json.dumps({
            'producer_errors': PRODUCER_ERRORS,
            'supervisor_reason': outcome.tasks[0].reason,
            'supervisor_output': outcome.tasks[0].output is not None,
            'pending': PUBLISHER.pending,
            'foreign_storage_state': sink.lookup(idempotency_key(envelope.identity)).state.value,
            'explicit_drain_count': len(PUBLISHER.drain()),
        }))


if __name__ == '__main__':
    main()
