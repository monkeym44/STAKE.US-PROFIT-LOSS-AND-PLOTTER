import customtkinter as ctk
import csv
from tkinter import filedialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Transaction Profit/Loss Viewer")
        self.geometry("950x650")

        self.purchase_file = None
        self.redeem_file = None

        # ===== TOP =====
        top_frame = ctk.CTkFrame(self)
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(top_frame, text="Upload Purchases CSV",
                      command=self.load_purchase).pack(side="left", padx=5)

        ctk.CTkButton(top_frame, text="Upload Redeems CSV",
                      command=self.load_redeem).pack(side="left", padx=5)

        ctk.CTkButton(top_frame, text="Process",
                      command=self.process_files).pack(side="left", padx=5)

        # ===== SUMMARY =====
        self.summary_label = ctk.CTkLabel(
            self, text="Upload both CSV files and click Process",
            font=("Arial", 16)
        )
        self.summary_label.pack(pady=10)

        # ===== LOG =====
        self.textbox = ctk.CTkTextbox(self)
        self.textbox.pack(fill="both", expand=True, padx=10, pady=10)

    # ===== FILE LOAD =====
    def load_purchase(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.purchase_file = file
            self.summary_label.configure(text="Purchases file loaded")

    def load_redeem(self):
        file = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file:
            self.redeem_file = file
            self.summary_label.configure(text="Redeems file loaded")

    # ===== CSV READER WITH DEBUG =====
    def read_csv(self, file_path, tx_type):
        transactions = []
        skipped = 0

        with open(file_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for line_num, row in enumerate(reader, start=2):  # header = line 1
                try:
                    # Validate required fields
                    if not row.get("amount") or not row.get("currency"):
                        raise ValueError("Missing amount or currency")

                    amount = float(row["amount"])

                    tx = {
                        "amount": amount,
                        "currency": row["currency"],
                        "type": tx_type,
                    }
                    transactions.append(tx)

                except Exception as e:
                    skipped += 1
                    self.textbox.insert(
                        "end",
                        f"[SKIPPED] Line {line_num} | {e}\nRow: {row}\n\n"
                    )

        return transactions, skipped

    # ===== PROCESS =====
    def process_files(self):
        if not self.purchase_file or not self.redeem_file:
            self.summary_label.configure(text="Please upload both CSV files")
            return

        self.textbox.delete("1.0", "end")

        purchases, skipped_p = self.read_csv(self.purchase_file, "purchase")
        redeems, skipped_r = self.read_csv(self.redeem_file, "redeem")

        all_tx = purchases + redeems

        total_purchased = 0.0
        total_redeemed = 0.0

        self.textbox.insert("end", "=== TRANSACTIONS ===\n\n")

        for tx in all_tx:
            if tx["type"] == "purchase":
                total_purchased += tx["amount"]
                self.textbox.insert(
                    "end",
                    f"[BUY ] +{tx['amount']} {tx['currency']}\n"
                )
            else:
                total_redeemed += tx["amount"]
                self.textbox.insert(
                    "end",
                    f"[SELL] -{tx['amount']} {tx['currency']}\n"
                )

        profit_loss = total_redeemed - total_purchased
        total_skipped = skipped_p + skipped_r

        summary = (
            f"Total Purchased : {total_purchased}\n"
            f"Total Redeemed  : {total_redeemed}\n"
            f"Net P/L         : {profit_loss}\n"
            f"Transactions    : {len(all_tx)}\n"
            f"Skipped Rows    : {total_skipped} "
            f"(Purchases: {skipped_p}, Redeems: {skipped_r})"
        )

        self.summary_label.configure(text=summary)

        if total_skipped > 0:
            self.textbox.insert(
                "end",
                f"\n⚠️ WARNING: {total_skipped} rows were skipped. "
                f"Scroll up to review.\n"
            )


if __name__ == "__main__":
    app = App()
    app.mainloop()
