import argparse
import logging
import sys
from pathlib import Path

from Services.authentication_services import AuthenticationService
from Services.authorization import AuthorizationService
from Services.bank_services import BankService
from Services.Storage import Storage
from Services.Transaction_service import TransactionService
from GUI.app_controller import AppController


def build_backend():
    store = Storage()

    authorization = AuthorizationService(store)
    authentication = AuthenticationService(store)
    bank_service = BankService(store, authorization)
    transaction_service = TransactionService(store, authorization)
    return store, authentication, authorization, bank_service, transaction_service


def run_headless():
    _, authentication, _, bank_service, _ = build_backend()
    staff = authentication.authenticate("staff", "staff123")
    statistics = bank_service.system_statistics(staff)

    print("Bank Management System in-memory simulation initialized successfully.")
    print(f"Customers: {statistics['total_customers']}")
    print(f"Accounts: {statistics['total_accounts']}")
    print(f"Transactions: {statistics['total_transactions']}")
    print("All data exists only during this application session.")
    return 0


def run_gui():
    try:
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError:
        print(
            "PySide6 is not installed. Install dependencies with "
            "'python -m pip install -r requirements.txt'.",
            file=sys.stderr,
        )
        return 1

    _, authentication, authorization, bank_service, transaction_service = build_backend()

    application = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    controller = AppController(
        authentication,
        authorization,
        bank_service,
        transaction_service,
    )

    engine.rootContext().setContextProperty("backend", controller)
    qml_path = Path(__file__).resolve().parent / "GUI" / "Main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_path)))

    if not engine.rootObjects():
        return 1

    return application.exec()


def main():
    parser = argparse.ArgumentParser(description="In-memory Bank Management System")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Initialize a fresh in-memory session and print demo statistics.",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    if args.headless:
        return run_headless()
    return run_gui()


if __name__ == "__main__":
    raise SystemExit(main())