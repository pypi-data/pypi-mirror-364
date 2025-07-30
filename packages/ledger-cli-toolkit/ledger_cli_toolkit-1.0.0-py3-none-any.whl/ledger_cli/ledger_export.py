import csv
from datetime import datetime
from typing import List, Dict, Union
from tabulate import tabulate
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas


class LedgerExports:

    def __init__(self, export_path: str):
        """
        Inicializa la clase con la ruta donde se guardarán los archivos exportados.
        """
        self.export_path = export_path
        self.exported_files = []

    def export_to_csv(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ] = None,
        account_balances: Dict[str, Dict[str, float]] = None,
        accounts: List[str] = None,
    ) -> List[str]:
        """
        Exporta las tablas de las transacciones, balance general y lista de cuentas a archivos CSV.
        Si alguna de las tablas no es proporcionada, no se exporta.
        Retorna una lista con los nombres de los archivos generados.
        """
        # Get the current date
        today = datetime.today().strftime("%Y-%m-%d")
        exported_files = []

        # Export the journal table to CSV if transactions are provided
        if transactions_json:
            journal_filename = f"journal_{today}.csv"
            journal_filepath = f"{self.export_path}/{journal_filename}"
            with open(journal_filepath, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["N°", "Fecha", "Concepto", "Debe", "Haber"])
                idx = 1
                total_debit = 0.0
                total_credit = 0.0
                for transaction in transactions_json:
                    for account in transaction["accounts"]:
                        date_time = transaction["date"]
                        if transaction.get("time"):
                            date_time += f" {transaction['time']}"
                        account_name = account["account"]
                        amount = account["amount"]
                        debit = amount if amount > 0 else 0
                        credit = -amount if amount < 0 else 0
                        writer.writerow([idx, date_time, account_name, debit, credit])
                        total_debit += debit
                        total_credit += credit
                        idx += 1
                writer.writerow(["", "", "SUMAS IGUALES", total_debit, total_credit])
            exported_files.append(journal_filepath)

        # Export the general balance table to CSV if account_balances are provided
        if account_balances:
            balance_filename = f"general_balance_{today}.csv"
            balance_filepath = f"{self.export_path}/{balance_filename}"
            with open(balance_filepath, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["N°", "Concepto", "Unidad", "Saldo"])
                idx = 1
                total_balance = 0.0
                for account, balances in account_balances.items():
                    for unit, balance in balances.items():
                        writer.writerow([idx, account, unit, f"{balance:.2f}"])
                        total_balance += balance
                        idx += 1
                writer.writerow(["", "BALANCE GENERAL", "", f"{total_balance:.2f}"])
            exported_files.append(balance_filepath)

        # Export the accounts list to CSV if accounts are provided
        if accounts:
            accounts_filename = f"accounts_list_{today}.csv"
            accounts_filepath = f"{self.export_path}/{accounts_filename}"
            with open(accounts_filepath, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["N°", "Concepto"])
                for idx, account in enumerate(accounts, start=1):
                    writer.writerow([idx, account])
            exported_files.append(accounts_filepath)

        # Save the file paths to the exported files list
        self.exported_files = exported_files

        # Return the generated file paths
        return self.exported_files

    def export_to_markdown(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ] = None,
        account_balances: Dict[str, Dict[str, float]] = None,
        accounts: List[str] = None,
    ) -> List[str]:
        """
        Exporta las tablas de las transacciones, balance general y lista de cuentas a archivos Markdown.
        Si alguna de las tablas no es proporcionada, no se exporta.
        Retorna una lista con los nombres de los archivos generados.
        """
        # Get the current date
        today = datetime.today().strftime("%Y-%m-%d")
        exported_files = []

        # Export the journal table to Markdown if transactions are provided
        if transactions_json:
            journal_filename = f"journal_{today}.md"
            journal_filepath = f"{self.export_path}/{journal_filename}"
            with open(journal_filepath, mode="w") as file:
                file.write("# Journal\n\n")
                file.write("| N° | Fecha | Concepto | Debe | Haber |\n")
                file.write("| --- | ----- | -------- | ---- | ----- |\n")
                idx = 1
                total_debit = 0.0
                total_credit = 0.0
                for transaction in transactions_json:
                    for account in transaction["accounts"]:
                        date_time = transaction["date"]
                        if transaction.get("time"):
                            date_time += f" {transaction['time']}"
                        account_name = account["account"]
                        amount = account["amount"]
                        debit = amount if amount > 0 else 0
                        credit = -amount if amount < 0 else 0
                        file.write(
                            f"| {idx} | {date_time} | {account_name} | {debit:.2f} | {credit:.2f} |\n"
                        )
                        total_debit += debit
                        total_credit += credit
                        idx += 1
                file.write(
                    f"|   |   | SUMAS IGUALES | {total_debit:.2f} | {total_credit:.2f} |\n"
                )
            exported_files.append(journal_filepath)

        # Export the general balance table to Markdown if account_balances are provided
        if account_balances:
            balance_filename = f"general_balance_{today}.md"
            balance_filepath = f"{self.export_path}/{balance_filename}"
            with open(balance_filepath, mode="w") as file:
                file.write("# Balance General\n\n")
                file.write("| N° | Concepto | Unidad | Saldo |\n")
                file.write("| --- | -------- | ------ | ----- |\n")
                idx = 1
                total_balance = 0.0
                for account, balances in account_balances.items():
                    for unit, balance in balances.items():
                        file.write(f"| {idx} | {account} | {unit} | {balance:.2f} |\n")
                        total_balance += balance
                        idx += 1
                file.write(f"|   | BALANCE GENERAL |   | {total_balance:.2f} |\n")
            exported_files.append(balance_filepath)

        # Export the accounts list to Markdown if accounts are provided
        if accounts:
            accounts_filename = f"accounts_list_{today}.md"
            accounts_filepath = f"{self.export_path}/{accounts_filename}"
            with open(accounts_filepath, mode="w") as file:
                file.write("# Lista de Cuentas\n\n")
                file.write("| N° | Concepto |\n")
                file.write("| --- | -------- |\n")
                for idx, account in enumerate(accounts, start=1):
                    file.write(f"| {idx} | {account} |\n")
            exported_files.append(accounts_filepath)

        # Save the file paths to the exported files list
        self.exported_files = exported_files

        # Return the generated file paths
        return self.exported_files

    def export_to_pdf(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ] = None,
        account_balances: Dict[str, Dict[str, float]] = None,
        accounts: List[str] = None,
    ) -> List[str]:
        """
        Exporta las tablas de las transacciones, balance general y lista de cuentas a archivos PDF.
        Si alguna de las tablas no es proporcionada, no se exporta.
        Retorna una lista con los nombres de los archivos generados.
        """
        # Get the current date
        today = datetime.today().strftime("%Y-%m-%d")
        exported_files = []

        # Export the journal table to PDF if transactions are provided
        if transactions_json:
            journal_filename = f"journal_{today}.pdf"
            journal_filepath = f"{self.export_path}/{journal_filename}"
            c = canvas.Canvas(journal_filepath, pagesize=letter)
            c.setFont("Helvetica", 10)
            c.drawString(30, 750, "Journal")
            c.drawString(30, 735, f"Fecha: {today}")
            c.drawString(30, 720, "| N° | Fecha | Concepto | Debe | Haber |")
            y_position = 705
            idx = 1
            total_debit = 0.0
            total_credit = 0.0
            for transaction in transactions_json:
                for account in transaction["accounts"]:
                    date_time = transaction["date"]
                    if transaction.get("time"):
                        date_time += f" {transaction['time']}"
                    account_name = account["account"]
                    amount = account["amount"]
                    debit = amount if amount > 0 else 0
                    credit = -amount if amount < 0 else 0
                    c.drawString(
                        30,
                        y_position,
                        f"| {idx} | {date_time} | {account_name} | {debit:.2f} | {credit:.2f} |",
                    )
                    y_position -= 15
                    total_debit += debit
                    total_credit += credit
                    idx += 1
            c.drawString(
                30,
                y_position,
                f"|   |   | SUMAS IGUALES | {total_debit:.2f} | {total_credit:.2f} |",
            )
            c.save()
            exported_files.append(journal_filepath)

        # Export the general balance table to PDF if account_balances are provided
        if account_balances:
            balance_filename = f"general_balance_{today}.pdf"
            balance_filepath = f"{self.export_path}/{balance_filename}"
            c = canvas.Canvas(balance_filepath, pagesize=letter)
            c.setFont("Helvetica", 10)
            c.drawString(30, 750, "Balance General")
            c.drawString(30, 735, f"Fecha: {today}")
            c.drawString(30, 720, "| N° | Concepto | Unidad | Saldo |")
            y_position = 705
            idx = 1
            total_balance = 0.0
            for account, balances in account_balances.items():
                for unit, balance in balances.items():
                    c.drawString(
                        30,
                        y_position,
                        f"| {idx} | {account} | {unit} | {balance:.2f} |",
                    )
                    y_position -= 15
                    total_balance += balance
                    idx += 1
            c.drawString(
                30, y_position, f"|   | BALANCE GENERAL |   | {total_balance:.2f} |"
            )
            c.save()
            exported_files.append(balance_filepath)

        # Export the accounts list to PDF if accounts are provided
        if accounts:
            accounts_filename = f"accounts_list_{today}.pdf"
            accounts_filepath = f"{self.export_path}/{accounts_filename}"
            c = canvas.Canvas(accounts_filepath, pagesize=letter)
            c.setFont("Helvetica", 10)
            c.drawString(30, 750, "Lista de Cuentas")
            c.drawString(30, 735, f"Fecha: {today}")
            c.drawString(30, 720, "| N° | Concepto |")
            y_position = 705
            for idx, account in enumerate(accounts, start=1):
                c.drawString(30, y_position, f"| {idx} | {account} |")
                y_position -= 15
            c.save()
            exported_files.append(accounts_filepath)

        # Save the file paths to the exported files list
        self.exported_files = exported_files

        # Return the generated file paths
        return self.exported_files
