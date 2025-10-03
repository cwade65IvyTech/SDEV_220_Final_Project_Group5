#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Varner's Greenhouse & Nursery - 2025 Fall Wholesale Order Form (1 of 2)
Python/Tkinter desktop app

Features
- Peach-colored input boxes (use Tab to advance)
- Customer/contact fields
- Sales tax status (Pays Sales Tax vs Sales Tax Exempt) + configurable tax rate (default MI 6%)
- Payment terms (C.O.D. / Net 30)
- Delivery vs Pickup (+ delivery fee input; default $40 when Delivery selected)
- Product entry by mix/color with unit pricing
- Live Subtotal, Sales Tax, Delivery, and Total
- Notes field for combo requests
- Save as CSV and Save printable TXT order summary

Tested with Python 3.10+ on Windows/macOS/Linux.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from collections import OrderedDict

APP_TITLE = "Varner's Greenhouse & Nursery - 2025 Fall Wholesale Order Form"
PEACH = "#FFDAB9"  # peach puff
MONEY_FMT = "${:,.2f}"
DEFAULT_TAX_RATE = 0.06  # 6% Michigan
DEFAULT_DELIVERY_MIN = 40.00

class MoneyVar(tk.StringVar):
    """StringVar that keeps a numeric float in sync with a currency-formatted display."""
    def __init__(self, master=None, value=0.0, **kw):
        super().__init__(master, **kw)
        self._num = float(value)
        self.set(MONEY_FMT.format(self._num))

    @property
    def num(self):
        return self._num

    @num.setter
    def num(self, v):
        try:
            self._num = float(v)
        except Exception:
            self._num = 0.0
        self.set(MONEY_FMT.format(self._num))

def valid_int(s: str) -> bool:
    return s == "" or s.isdigit()

def to_int(s: str) -> int:
    try:
        return int(s)
    except Exception:
        return 0

def calc_line_total(qty: int, price: float) -> float:
    return qty * price

class OrderForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x800")
        self.minsize(1000, 750)

        self.tax_rate = tk.DoubleVar(value=DEFAULT_TAX_RATE)
        self.delivery_selected = tk.StringVar(value="PICK UP")  # "DELIVERY" or "PICK UP"
        self.delivery_fee = tk.DoubleVar(value=0.0)
        self.payment_terms = tk.StringVar(value="C.O.D.")
        self.sales_tax_status = tk.StringVar(value="PAYS SALES TAX")

        # Header / Customer info
        self.build_header()

        # Products
        canvas = tk.Canvas(self, borderwidth=0)
        canvas.pack(fill="both", expand=True, padx=12, pady=6)
        self._scroll_y = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self._scroll_y.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")
        self.product_frame = tk.Frame(canvas)
        self.product_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.product_frame, anchor="nw")
        canvas.configure(yscrollcommand=self._scroll_y.set)

        self.products = self.build_products(self.product_frame)

        # Totals + actions
        self.build_totals_area()

        # Keyboard focus traversal is automatic with Tab; ensure peach background for inputs
        self.style_entries_peach(self)

        # Recompute when relevant fields change
        self.bind_variable_updates()

        # Initial compute
        self.recompute_totals()

    def build_header(self):
        frm = ttk.LabelFrame(self, text="Customer & Order Info")
        frm.pack(fill="x", padx=12, pady=8)

        # Row 0
        ttk.Label(frm, text="Business Name:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.business_name = tk.Entry(frm, bg=PEACH)
        self.business_name.grid(row=0, column=1, sticky="we", padx=6, pady=4)

        ttk.Label(frm, text="Contact Name:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.contact_name = tk.Entry(frm, bg=PEACH)
        self.contact_name.grid(row=0, column=3, sticky="we", padx=6, pady=4)

        # Row 1
        ttk.Label(frm, text="Cell Phone #:").grid(row=1, column=0, sticky="e", padx=6, pady=4)
        self.cell_phone = tk.Entry(frm, bg=PEACH)
        self.cell_phone.grid(row=1, column=1, sticky="we", padx=6, pady=4)

        ttk.Label(frm, text="Business Phone #:").grid(row=1, column=2, sticky="e", padx=6, pady=4)
        self.business_phone = tk.Entry(frm, bg=PEACH)
        self.business_phone.grid(row=1, column=3, sticky="we", padx=6, pady=4)

        # Row 2 - Payment terms
        ttk.Label(frm, text="Payment Terms:").grid(row=2, column=0, sticky="e", padx=6, pady=4)
        terms_frame = tk.Frame(frm)
        terms_frame.grid(row=2, column=1, sticky="w", padx=6, pady=4)
        for txt in ("C.O.D.", "NET 30"):
            ttk.Radiobutton(terms_frame, text=txt, value=txt, variable=self.payment_terms).pack(side="left", padx=6)

        # Row 3 - Sales tax status
        ttk.Label(frm, text="Sales Tax Status:").grid(row=3, column=0, sticky="e", padx=6, pady=4)
        tax_frame = tk.Frame(frm)
        tax_frame.grid(row=3, column=1, sticky="w", padx=6, pady=4)
        for txt in ("PAYS SALES TAX", "SALES TAX EXEMPT"):
            ttk.Radiobutton(tax_frame, text=txt, value=txt, variable=self.sales_tax_status, command=self.recompute_totals).pack(side="left", padx=6)

        ttk.Label(frm, text="Sales Tax Rate:").grid(row=3, column=2, sticky="e", padx=6, pady=4)
        self.tax_rate_entry = tk.Entry(frm, bg=PEACH, width=8)
        self.tax_rate_entry.insert(0, f"{DEFAULT_TAX_RATE*100:.2f}")
        self.tax_rate_entry.grid(row=3, column=3, sticky="w", padx=6, pady=4)
        ttk.Label(frm, text="%").grid(row=3, column=3, sticky="w", padx=60, pady=4)

        # Row 4 - Delivery / Pickup
        ttk.Label(frm, text="Fulfillment:").grid(row=4, column=0, sticky="e", padx=6, pady=4)
        fulfill_frame = tk.Frame(frm)
        fulfill_frame.grid(row=4, column=1, sticky="w", padx=6, pady=4)
        ttk.Radiobutton(fulfill_frame, text="DELIVERY", value="DELIVERY", variable=self.delivery_selected, command=self.on_delivery_toggle).pack(side="left", padx=6)
        ttk.Radiobutton(fulfill_frame, text="PICK UP", value="PICK UP", variable=self.delivery_selected, command=self.on_delivery_toggle).pack(side="left", padx=6)

        ttk.Label(frm, text="Delivery Fee:").grid(row=4, column=2, sticky="e", padx=6, pady=4)
        self.delivery_fee_entry = tk.Entry(frm, bg=PEACH, width=10)
        self.delivery_fee_entry.insert(0, "0.00")
        self.delivery_fee_entry.grid(row=4, column=3, sticky="w", padx=6, pady=4)
        ttk.Label(frm, text="(Starts at $40.00; call for quote)").grid(row=4, column=3, sticky="w", padx=90, pady=4)

        # Row 5 - Note on combos
        ttk.Label(frm, text="Note on Combos:").grid(row=5, column=0, sticky="ne", padx=6, pady=4)
        self.notes = tk.Text(frm, height=3, width=60, bg=PEACH, wrap="word")
        self.notes.insert("1.0", "If you want specific color combos, please request on a separate document and include it with this order; otherwise we'll provide the best-looking mixed combos.")
        self.notes.grid(row=5, column=1, columnspan=3, sticky="we", padx=6, pady=4)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)

    def build_products(self, parent):
        """
        Returns an OrderedDict of product rows:
        key -> dict(unit_price, vars={color: tk.StringVar for qty})
        """
        products = OrderedDict()

        # Helper to create a titled section
        def section(title):
            lf = ttk.LabelFrame(parent, text=title)
            lf.pack(fill="x", padx=12, pady=10)
            return lf

        # Validation for integer quantities
        vcmd = (self.register(valid_int), "%P")

        # ------- PANSY MIXES (10.30) --------
        pansy_mixes = OrderedDict([
            ("AUTUMN MIX", 0),
            ("AUTUMN BLAZE MIX", 0),
            ("FRIZZLE SIZZLE MIX", 0),
            ("HALLOWEEN MIX", 0),
            ("MATRIX MIX", 0),
            ("PANOLA MIX", 0),
        ])
        products["PANSY MIXES"] = {"unit_price": 10.30, "vars": {}}
        sec = section("PANSY MIXES  — unit price $10.30")
        self.build_table(sec, pansy_mixes, products["PANSY MIXES"], vcmd)

        # ------- PANSY BLOTCHES & MULTI-COLORS (10.30) --------
        pansy_blotches = OrderedDict([
            ("FRIZZLE SIZZLE ORANGE", 0),
            ("MIDNIGHT GLOW", 0),
            ("SOLAR FLARE", 0),
            ("RED BLOTCH", 0),
            ("WHITE BLOTCH", 0),
        ])
        products["PANSY BLOTCHES & MULTI-COLORS"] = {"unit_price": 10.30, "vars": {}}
        sec = section("PANSY BLOTCHES & MULTI-COLORS  — unit price $10.30")
        self.build_table(sec, pansy_blotches, products["PANSY BLOTCHES & MULTI-COLORS"], vcmd)

        # ------- PANSY SOLID COLORS (10.30) --------
        pansy_solids = OrderedDict([
            ("BLACK", 0),
            ("ORANGE", 0),
            ("YELLOW", 0),
        ])
        products["PANSY SOLID COLORS"] = {"unit_price": 10.30, "vars": {}}
        sec = section("PANSY SOLID COLORS  — unit price $10.30")
        self.build_table(sec, pansy_solids, products["PANSY SOLID COLORS"], vcmd)

        # ------- VIOLA (10.30) --------
        viola = OrderedDict([
            ("BLACK", 0),
            ("INDIAN SUMMER MIX", 0),
            ("ORANGE", 0),
            ("YELLOW/BLUE", 0),
        ])
        products["VIOLA"] = {"unit_price": 10.30, "vars": {}}
        sec = section("VIOLA  — unit price $10.30")
        self.build_table(sec, viola, products["VIOLA"], vcmd)

        # ------- FALL DECOR --------
        fall_sec = section("FALL DECOR")
        # Corn shocks
        products["CORN SHOCKS (10-15 STALKS PER BUNDLE)"] = {"unit_price": 7.19, "vars": {}}
        self.build_table(fall_sec, OrderedDict([("BEST AVAILABLE", 0)]), products["CORN SHOCKS (10-15 STALKS PER BUNDLE)"], vcmd, subtitle="CORN SHOCKS — unit price $7.19")
        # Straw bales
        products["STRAW BALES"] = {"unit_price": 6.29, "vars": {}}
        self.build_table(fall_sec, OrderedDict([("BEST AVAILABLE", 0)]), products["STRAW BALES"], vcmd, subtitle="STRAW BALES — unit price $6.29")

        return products

    def build_table(self, parent, items_dict, product_info, vcmd, subtitle=None):
        if subtitle:
            ttk.Label(parent, text=subtitle).pack(anchor="w", padx=8, pady=(6,2))

        frame = tk.Frame(parent)
        frame.pack(fill="x", padx=8, pady=2)

        # Headers
        tk.Label(frame, text="Color / Mix", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, sticky="w", padx=4, pady=4)
        tk.Label(frame, text="Qty", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, sticky="w", padx=4, pady=4)
        tk.Label(frame, text="Unit Price", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky="w", padx=4, pady=4)
        tk.Label(frame, text="Line Total", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=3, sticky="w", padx=4, pady=4)

        product_info["vars"] = {}
        r = 1
        for name, _ in items_dict.items():
            tk.Label(frame, text=name).grid(row=r, column=0, sticky="w", padx=4, pady=2)
            v = tk.StringVar(value="0")
            ent = tk.Entry(frame, textvariable=v, validate="key", validatecommand=vcmd, bg=PEACH, width=8)
            ent.grid(row=r, column=1, sticky="w", padx=4, pady=2)
            # Store for later access
            product_info["vars"][name] = v

            tk.Label(frame, text=MONEY_FMT.format(product_info["unit_price"])).grid(row=r, column=2, sticky="w", padx=4, pady=2)
            lbl_total = tk.Label(frame, text=MONEY_FMT.format(0.0))
            lbl_total.grid(row=r, column=3, sticky="w", padx=4, pady=2)

            # Live update on change
            def make_cb(var=v, label=lbl_total, price=product_info["unit_price"]):
                def cb(*_):
                    qty = to_int(var.get())
                    label.config(text=MONEY_FMT.format(calc_line_total(qty, price)))
                    self.recompute_totals()
                return cb
            v.trace_add("write", make_cb())

            r += 1

        for c in (0,1,2,3):
            frame.grid_columnconfigure(c, weight=1)

    def build_totals_area(self):
        frm = ttk.LabelFrame(self, text="Totals & Actions")
        frm.pack(fill="x", padx=12, pady=8)

        # Subtotal, tax, delivery, total
        ttk.Label(frm, text="Subtotal:").grid(row=0, column=0, sticky="e", padx=6, pady=4)
        self.subtotal_var = MoneyVar(value=0.0)
        ttk.Label(frm, textvariable=self.subtotal_var).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Sales Tax:").grid(row=0, column=2, sticky="e", padx=6, pady=4)
        self.tax_var = MoneyVar(value=0.0)
        ttk.Label(frm, textvariable=self.tax_var).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Delivery Service:").grid(row=0, column=4, sticky="e", padx=6, pady=4)
        self.delivery_var = MoneyVar(value=0.0)
        ttk.Label(frm, textvariable=self.delivery_var).grid(row=0, column=5, sticky="w", padx=6, pady=4)

        ttk.Label(frm, text="Total:").grid(row=0, column=6, sticky="e", padx=6, pady=4)
        self.total_var = MoneyVar(value=0.0)
        total_label = ttk.Label(frm, textvariable=self.total_var, font=("TkDefaultFont", 10, "bold"))
        total_label.grid(row=0, column=7, sticky="w", padx=6, pady=4)

        # Buttons
        btnfrm = tk.Frame(frm)
        btnfrm.grid(row=1, column=0, columnspan=8, sticky="we", padx=6, pady=6)
        ttk.Button(btnfrm, text="Save CSV…", command=self.save_csv).pack(side="left", padx=4)
        ttk.Button(btnfrm, text="Save Printable Summary…", command=self.save_text_summary).pack(side="left", padx=4)
        ttk.Button(btnfrm, text="Reset Form", command=self.reset_form).pack(side="left", padx=4)

        for c in range(8):
            frm.grid_columnconfigure(c, weight=1)

    def bind_variable_updates(self):
        # recompute when tax rate or delivery fee text fields change
        def on_taxrate_change(*_):
            try:
                v = float(self.tax_rate_entry.get().strip()) / 100.0
                self.tax_rate.set(v)
            except Exception:
                pass
            self.recompute_totals()

        def on_deliveryfee_change(*_):
            try:
                v = float(self.delivery_fee_entry.get().strip())
                self.delivery_fee.set(v)
            except Exception:
                self.delivery_fee.set(0.0)
            self.recompute_totals()

        self.tax_rate_entry.bind("<KeyRelease>", lambda e: on_taxrate_change())
        self.delivery_fee_entry.bind("<KeyRelease>", lambda e: on_deliveryfee_change())

    def on_delivery_toggle(self):
        if self.delivery_selected.get() == "DELIVERY":
            # If currently 0 or less than minimum, set to default minimum
            try:
                cur = float(self.delivery_fee_entry.get().strip())
            except Exception:
                cur = 0.0
            if cur < DEFAULT_DELIVERY_MIN:
                self.delivery_fee_entry.delete(0, "end")
                self.delivery_fee_entry.insert(0, f"{DEFAULT_DELIVERY_MIN:.2f}")
        else:
            self.delivery_fee_entry.delete(0, "end")
            self.delivery_fee_entry.insert(0, "0.00")
        self.recompute_totals()

    def get_order_lines(self):
        lines = []
        for group, info in self.products.items():
            price = info["unit_price"]
            for color, var in info["vars"].items():
                qty = to_int(var.get())
                if qty > 0:
                    lines.append({
                        "group": group,
                        "item": color,
                        "qty": qty,
                        "unit_price": price,
                        "line_total": calc_line_total(qty, price)
                    })
        return lines

    def recompute_totals(self):
        subtotal = sum(l["line_total"] for l in self.get_order_lines())
        self.subtotal_var.num = subtotal

        tax = 0.0
        if self.sales_tax_status.get() == "PAYS SALES TAX":
            tax = subtotal * self.tax_rate.get()
        self.tax_var.num = tax

        deliv = 0.0
        try:
            deliv = float(self.delivery_fee_entry.get().strip())
            if self.delivery_selected.get() == "PICK UP":
                deliv = 0.0
        except Exception:
            deliv = 0.0
        self.delivery_var.num = deliv

        self.total_var.num = subtotal + tax + deliv

    def reset_form(self):
        if not messagebox.askyesno("Reset Form", "Clear all inputs and start over?"):
            return
        self.business_name.delete(0, "end")
        self.contact_name.delete(0, "end")
        self.cell_phone.delete(0, "end")
        self.business_phone.delete(0, "end")
        self.payment_terms.set("C.O.D.")
        self.sales_tax_status.set("PAYS SALES TAX")
        self.tax_rate_entry.delete(0, "end")
        self.tax_rate_entry.insert(0, f"{DEFAULT_TAX_RATE*100:.2f}")
        self.delivery_selected.set("PICK UP")
        self.delivery_fee_entry.delete(0, "end")
        self.delivery_fee_entry.insert(0, "0.00")
        self.notes.delete("1.0", "end")

        for info in self.products.values():
            for var in info["vars"].values():
                var.set("0")

        self.recompute_totals()

    def save_csv(self):
        lines = self.get_order_lines()
        if not lines:
            messagebox.showwarning("No items", "Please enter at least one quantity.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv")],
            initialfile=f"varners_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if not path:
            return
        import csv
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Business Name", self.business_name.get().strip()])
            w.writerow(["Contact Name", self.contact_name.get().strip()])
            w.writerow(["Cell Phone", self.cell_phone.get().strip()])
            w.writerow(["Business Phone", self.business_phone.get().strip()])
            w.writerow(["Payment Terms", self.payment_terms.get()])
            w.writerow(["Sales Tax Status", self.sales_tax_status.get()])
            w.writerow(["Sales Tax Rate (%)", f"{self.tax_rate.get()*100:.2f}"])
            w.writerow(["Fulfillment", self.delivery_selected.get()])
            w.writerow(["Delivery Fee", f"{self.delivery_var.num:.2f}"])
            w.writerow(["Notes", self.notes.get('1.0', 'end').strip()])
            w.writerow([])
            w.writerow(["Group","Item","Qty","Unit Price","Line Total"])
            for ln in lines:
                w.writerow([ln["group"], ln["item"], ln["qty"], f"{ln['unit_price']:.2f}", f"{ln['line_total']:.2f}"])
            w.writerow([])
            w.writerow(["Subtotal", f"{self.subtotal_var.num:.2f}"])
            w.writerow(["Sales Tax", f"{self.tax_var.num:.2f}"])
            w.writerow(["Delivery", f"{self.delivery_var.num:.2f}"])
            w.writerow(["Total", f"{self.total_var.num:.2f}"])
        messagebox.showinfo("Saved", f"Order CSV saved:\n{path}")

    def save_text_summary(self):
        lines = self.get_order_lines()
        if not lines:
            messagebox.showwarning("No items", "Please enter at least one quantity.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files","*.txt")],
            initialfile=f"varners_order_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        if not path:
            return
        linestr = []
        push = linestr.append
        push(APP_TITLE)
        push("-"*80)
        push(f"Date: {datetime.now():%Y-%m-%d %H:%M}")
        push(f"Business: {self.business_name.get().strip()}")
        push(f"Contact: {self.contact_name.get().strip()} | Cell: {self.cell_phone.get().strip()} | Business: {self.business_phone.get().strip()}")
        push(f"Terms: {self.payment_terms.get()} | Tax Status: {self.sales_tax_status.get()} ({self.tax_rate.get()*100:.2f}%)")
        push(f"Fulfillment: {self.delivery_selected.get()} | Delivery Fee: {MONEY_FMT.format(self.delivery_var.num)}")
        push("Notes on combos:")
        push(self.notes.get('1.0', 'end').strip() or "-")
        push("")
        push("{:<34}  {:<28}  {:>5}  {:>10}  {:>12}".format("Group","Item","Qty","Unit","Line Total"))
        push("-"*95)
        for ln in lines:
            push("{:<34}  {:<28}  {:>5}  {:>10}  {:>12}".format(
                ln["group"][:34], ln["item"][:28], ln["qty"], f"{ln['unit_price']:.2f}", f"{ln['line_total']:.2f}"
            ))
        push("-"*95)
        push(f"Subtotal: {MONEY_FMT.format(self.subtotal_var.num)}")
        push(f"Sales Tax: {MONEY_FMT.format(self.tax_var.num)}")
        push(f"Delivery: {MONEY_FMT.format(self.delivery_var.num)}")
        push(f"TOTAL:    {MONEY_FMT.format(self.total_var.num)}")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(linestr))
        messagebox.showinfo("Saved", f"Printable summary saved:\n{path}")

    @staticmethod
    def style_entries_peach(widget):
        for child in widget.winfo_children():
            if isinstance(child, tk.Entry) or isinstance(child, tk.Text):
                try:
                    child.config(bg=PEACH)
                except Exception:
                    pass
            OrderForm.style_entries_peach(child)

def main():
    app = OrderForm()
    app.mainloop()

if __name__ == "__main__":
    main()
