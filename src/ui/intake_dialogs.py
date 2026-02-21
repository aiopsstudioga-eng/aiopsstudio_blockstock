"""
Intake dialogs for purchases and donations with color-coded UI.

Architecture:
    BaseIntakeDialog  — shared SKU autocomplete, item lookup, and form scaffolding
    PurchaseDialog    — blue theme, quantity + unit cost, calls process_purchase()
    DonationDialog    — green theme, quantity + FMV, calls process_donation()

Includes SKU type-ahead (QCompleter) for quick item lookup by SKU or name prefix.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDoubleSpinBox, QPushButton,
    QTextEdit, QMessageBox, QCompleter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem

from services.inventory_service import InventoryService


class BaseIntakeDialog(QDialog):
    """
    Abstract base class for Purchase and Donation intake dialogs.

    Provides all shared SKU autocomplete logic so subclasses only need to
    define their theme colour, their specific form fields, and their save
    method.  Any bugfix to SKU autocomplete automatically applies to both
    dialogs.

    Subclass contract:
        THEME_COLOR (str)   — hex colour used in header and primary button
        HEADER_EMOJI (str)  — emoji prefix shown in dialog header
        HEADER_TITLE (str)  — text shown after the emoji in the header

    Subclass must implement:
        _build_specific_form_rows(form)  — add dialog-specific QFormLayout rows
        _save()                          — validate + call the service method
    """

    THEME_COLOR: str = "#000000"
    HEADER_EMOJI: str = ""
    HEADER_TITLE: str = ""

    def __init__(self, service: InventoryService, parent=None):
        """
        Initialise the dialog.

        Args:
            service: InventoryService instance used for item lookup and saving.
            parent:  Optional parent widget.
        """
        super().__init__(parent)

        self.service = service
        self.selected_item_id = None
        self._categories = {c.id: c.name for c in service.get_all_categories()}

        self._build_ui()
        self._setup_sku_completer()

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        """Build the common dialog chrome (header, shared fields, buttons)."""
        self.setMinimumWidth(550)
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #ecf0f1;
            }}
            QLabel#header {{
                background-color: {self.THEME_COLOR};
                color: white;
                padding: 20px;
                font-size: 18pt;
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Coloured header bar
        header = QLabel(f"{self.HEADER_EMOJI} {self.HEADER_TITLE}")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Form container
        form_container = QVBoxLayout()
        form_container.setContentsMargins(30, 30, 30, 30)

        # Optional info banner (subclass can override _build_info_banner)
        banner = self._build_info_banner()
        if banner:
            form_container.addWidget(banner)
            form_container.addSpacing(20)

        # Form rows
        form = QFormLayout()
        form.setSpacing(15)

        # ---- Shared fields ----
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("Type 2+ chars for suggestions, or scan SKU")
        self.sku_input.returnPressed.connect(self.search_item)
        self.sku_input.editingFinished.connect(self.search_item)
        form.addRow("SKU*:", self.sku_input)

        self.item_name_display = QLineEdit()
        self.item_name_display.setReadOnly(True)
        self.item_name_display.setPlaceholderText("Item name will appear here")
        self.item_name_display.setStyleSheet("background-color: #f0f0f0; color: #7f8c8d;")
        form.addRow("Item Name:", self.item_name_display)

        self.category_display = QLineEdit()
        self.category_display.setReadOnly(True)
        self.category_display.setPlaceholderText("Category will appear here")
        self.category_display.setStyleSheet("background-color: #f0f0f0; color: #7f8c8d;")
        form.addRow("Category:", self.category_display)

        self.stock_label = QLabel("-")
        self.stock_label.setStyleSheet("font-weight: bold;")
        form.addRow("Current Stock:", self.stock_label)

        # ---- Subclass-specific fields ----
        self._build_specific_form_rows(form)

        # Notes (shared by all intake types)
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Optional notes...")
        self.notes_input.setMaximumHeight(80)
        form.addRow("Notes:", self.notes_input)

        form_container.addLayout(form)
        layout.addLayout(form_container)

        # Button bar
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(30, 0, 30, 30)
        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton(self._save_button_label())
        save_btn.setDefault(True)
        save_btn.clicked.connect(self._save)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.THEME_COLOR};
                color: white;
                padding: 10px 30px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self._hover_color()};
            }}
        """)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _build_info_banner(self):
        """Return an optional QLabel info banner, or None. Override in subclasses."""
        return None

    def _save_button_label(self) -> str:
        """Return the label for the primary save button. Override in subclasses."""
        return "Save"

    def _hover_color(self) -> str:
        """Return a slightly darker shade of THEME_COLOR for hover state."""
        # Provide a sensible default; subclasses override if needed
        return self.THEME_COLOR

    def _build_specific_form_rows(self, form: QFormLayout):
        """
        Add dialog-specific form rows to ``form``.

        Must be overridden by subclasses.

        Args:
            form: The QFormLayout to add rows to.
        """
        raise NotImplementedError("Subclasses must implement _build_specific_form_rows()")

    def _save(self):
        """
        Validate and persist the transaction.

        Must be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _save()")

    # ------------------------------------------------------------------
    # SKU Autocomplete (shared — single implementation)
    # ------------------------------------------------------------------

    def _setup_sku_completer(self):
        """Set up the QCompleter for SKU type-ahead suggestions."""
        self._completer_model = QStandardItemModel()
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(10)
        self._completer.activated.connect(self._on_sku_selected)
        self.sku_input.setCompleter(self._completer)
        self.sku_input.textChanged.connect(self._on_sku_text_changed)

    def _on_sku_text_changed(self, text: str):
        """Rebuild completer model when user has typed 2+ characters."""
        text = text.strip()
        if len(text) < 2:
            self._completer_model.clear()
            return

        items = self.service.search_items_by_prefix(text)
        self._completer_model.clear()

        for item in items:
            display = f"{item.sku}  —  {item.name}"
            std_item = QStandardItem(display)
            std_item.setData(item.sku, Qt.ItemDataRole.UserRole)       # raw SKU
            std_item.setData(item.id,  Qt.ItemDataRole.UserRole + 1)   # item ID
            self._completer_model.appendRow(std_item)

    def _on_sku_selected(self, text: str):
        """Handle a completer selection — extract SKU and trigger field population."""
        sku = text.split("  —  ")[0].strip() if "  —  " in text else text.strip()
        self.sku_input.setText(sku)
        self.search_item()

    # ------------------------------------------------------------------
    # Item lookup and field population (shared)
    # ------------------------------------------------------------------

    def _populate_item_fields(self, item):
        """Populate shared display fields from the resolved InventoryItem."""
        self.selected_item_id = item.id
        self.item_name_display.setText(item.name)
        self.stock_label.setText(f"{item.quantity_on_hand:,.1f} units")
        self.stock_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        cat_name = self._categories.get(item.category_id, "") if item.category_id else ""
        self.category_display.setText(cat_name)

    def _clear_item_fields(self):
        """Clear all shared display fields when SKU is not found."""
        self.selected_item_id = None
        self.item_name_display.setText("❌ Item not found")
        self.stock_label.setText("-")
        self.stock_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.category_display.setText("")

    def search_item(self):
        """Look up the item by the current SKU input value."""
        text = self.sku_input.text().strip()
        # P1 Fix: Handle case where input contains the full "SKU — Name" string
        # This happens if the user selects a completion but the text isn't cleared,
        # or if specific signal timing causes search to run on the full string.
        sku = text.split("  —  ")[0].strip() if "  —  " in text else text
        
        if not sku:
            return

        item = self.service.get_item_by_sku(sku)
        if item:
            self.sku_input.setText(item.sku)  # Ensure field shows just the SKU
            self._populate_item_fields(item)
            self.quantity_spin.setFocus()
            self.quantity_spin.selectAll()
        else:
            self._clear_item_fields()


# ==============================================================================
# PurchaseDialog
# ==============================================================================

class PurchaseDialog(BaseIntakeDialog):
    """Dialog for recording inventory purchases (BLUE theme)."""

    THEME_COLOR = "#3498db"
    HEADER_EMOJI = "💰"
    HEADER_TITLE = "Purchase Entry"

    def __init__(self, service: InventoryService, parent=None):
        super().__init__(service, parent)
        self.setWindowTitle("Record Purchase")

    def _save_button_label(self) -> str:
        return "Record Purchase"

    def _hover_color(self) -> str:
        return "#2980b9"

    def _build_specific_form_rows(self, form: QFormLayout):
        """Add purchase-specific form rows: quantity, unit cost, tax rate, cost breakdown, supplier."""
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100_000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" units")
        self.quantity_spin.valueChanged.connect(self._update_total)
        form.addRow("Quantity*:", self.quantity_spin)

        # Unit Cost (pre-tax, per unit)
        self.unit_cost_spin = QDoubleSpinBox()
        self.unit_cost_spin.setRange(0.00, 100_000)
        self.unit_cost_spin.setDecimals(2)
        self.unit_cost_spin.setPrefix("$")
        self.unit_cost_spin.valueChanged.connect(self._update_total)
        form.addRow("Unit Cost* (pre-tax):", self.unit_cost_spin)

        # Tax Rate — spinbox + quick-select preset combo side by side
        tax_row_widget = QHBoxLayout()

        self.tax_rate_spin = QDoubleSpinBox()
        self.tax_rate_spin.setRange(0.00, 100.00)
        self.tax_rate_spin.setDecimals(2)
        self.tax_rate_spin.setValue(0.00)
        self.tax_rate_spin.setSuffix("%")
        self.tax_rate_spin.valueChanged.connect(self._update_total)
        tax_row_widget.addWidget(self.tax_rate_spin)

        self.tax_preset_combo = QComboBox()
        self.tax_preset_combo.addItems(["0%", "2%", "4%", "6%", "8%", "Custom"])
        self.tax_preset_combo.setFixedWidth(70)
        self.tax_preset_combo.currentTextChanged.connect(self._on_tax_preset_changed)
        tax_row_widget.addWidget(self.tax_preset_combo)

        tax_container = QHBoxLayout()
        tax_container.setContentsMargins(0, 0, 0, 0)
        tax_container.addLayout(tax_row_widget)
        tax_container.addStretch()

        from PyQt6.QtWidgets import QWidget
        tax_wrapper = QWidget()
        tax_wrapper.setLayout(tax_container)
        form.addRow("Tax Rate:", tax_wrapper)

        # Cost breakdown — three read-only display labels
        separator_style = "color: #7f8c8d; font-size: 10pt;"
        bold_style = f"font-size: 14pt; font-weight: bold; color: {self.THEME_COLOR};"

        self.subtotal_label = QLabel("$0.00")
        self.subtotal_label.setStyleSheet(separator_style)
        form.addRow("Subtotal:", self.subtotal_label)

        self.tax_amount_label = QLabel("$0.00")
        self.tax_amount_label.setStyleSheet(separator_style)
        form.addRow("Tax Amount:", self.tax_amount_label)

        self.grand_total_label = QLabel("$0.00")
        self.grand_total_label.setStyleSheet(bold_style)
        form.addRow("Grand Total:", self.grand_total_label)

        # Supplier dropdown
        self.supplier_combo = QComboBox()
        self.supplier_combo.addItems([
            "Dollar Tree",
            "Restaurant Depot",
            "Sam's Club",
            "Walmart",
            "Other"
        ])
        self.supplier_combo.setEditable(True)
        self.supplier_combo.lineEdit().setPlaceholderText("Select or type supplier...")
        form.addRow("Supplier:", self.supplier_combo)

    def _on_tax_preset_changed(self, text: str):
        """Load a preset tax rate into the spinbox when a preset is selected."""
        preset_map = {"0%": 0.0, "2%": 2.0, "4%": 4.0, "6%": 6.0, "8%": 8.0}
        if text in preset_map:
            # Block signals to avoid double-triggering _update_total
            self.tax_rate_spin.blockSignals(True)
            self.tax_rate_spin.setValue(preset_map[text])
            self.tax_rate_spin.blockSignals(False)
            self._update_total()
        # If "Custom" is chosen the user edits the spinbox directly — nothing to do.

    def _update_total(self):
        """Recalculate and display the three-part cost breakdown."""
        qty = self.quantity_spin.value()
        unit_cost = self.unit_cost_spin.value()
        tax_rate_pct = self.tax_rate_spin.value()

        subtotal = qty * unit_cost
        tax_amount = subtotal * (tax_rate_pct / 100.0)
        grand_total = subtotal + tax_amount

        self.subtotal_label.setText(f"${subtotal:,.2f}")
        self.tax_amount_label.setText(f"${tax_amount:,.2f}")
        self.grand_total_label.setText(f"${grand_total:,.2f}")

    def _save(self):
        """Validate inputs and record the purchase transaction.

        Tax is folded into the per-unit cost before calling the service so that
        the weighted average COGS reflects the true tax-inclusive cost paid.
        See rounding_strategy.md for the full rounding decision table.
        """
        if not self.selected_item_id:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid SKU")
            return

        quantity = self.quantity_spin.value()
        unit_cost = self.unit_cost_spin.value()
        tax_rate_pct = self.tax_rate_spin.value()
        supplier = self.supplier_combo.currentText().strip() or None
        notes = self.notes_input.toPlainText().strip() or None

        # Fold tax into the per-unit cost.  The service's int() conversion then
        # truncates to the nearest cent (see rounding_strategy.md — Step 3).
        tax_inclusive_unit_cost = unit_cost * (1.0 + tax_rate_pct / 100.0)

        # Grand total for the success message (float display, not stored directly)
        grand_total = quantity * tax_inclusive_unit_cost

        try:
            item, transaction = self.service.process_purchase(
                item_id=self.selected_item_id,
                quantity=quantity,
                unit_cost_dollars=tax_inclusive_unit_cost,
                supplier=supplier,
                notes=notes,
            )

            tax_line = (
                f"Tax Rate: {tax_rate_pct:.2f}%\n"
                f"Grand Total Paid: ${grand_total:,.2f}\n"
            ) if tax_rate_pct > 0 else ""

            QMessageBox.information(
                self,
                "Purchase Recorded",
                f"Item: {item.name}\n"
                f"Units Added: {quantity:,.2f}\n"
                f"{tax_line}"
                f"New Avg Unit Cost (COGS): ${item.current_unit_cost_dollars:.2f}\n"
                f"New Quantity On Hand: {item.quantity_on_hand:,.1f}",
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record purchase: {e}")


# ==============================================================================
# DonationDialog
# ==============================================================================

class DonationDialog(BaseIntakeDialog):
    """Dialog for recording inventory donations (GREEN theme)."""

    THEME_COLOR = "#27ae60"
    HEADER_EMOJI = "🎁"
    HEADER_TITLE = "Donation Entry"

    def __init__(self, service: InventoryService, parent=None):
        super().__init__(service, parent)
        self.setWindowTitle("Record Donation")

    def _save_button_label(self) -> str:
        return "Record Donation"

    def _hover_color(self) -> str:
        return "#229954"

    def _build_info_banner(self):
        """Return the donation-specific info banner."""
        info = QLabel(
            "💡 Donations are recorded at $0 cost but track fair market value "
            "for impact reporting"
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background-color: #d5f4e6; padding: 10px; border-radius: 4px; "
            f"color: {self.THEME_COLOR};"
        )
        return info

    def _build_specific_form_rows(self, form: QFormLayout):
        """Add donation-specific form rows: quantity, FMV, donor."""
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0.01, 100_000)
        self.quantity_spin.setDecimals(2)
        self.quantity_spin.setValue(1.0)
        self.quantity_spin.setSuffix(" units")
        self.quantity_spin.valueChanged.connect(self._update_total)
        form.addRow("Quantity*:", self.quantity_spin)

        # Fair Market Value (per unit)
        self.fmv_spin = QDoubleSpinBox()
        self.fmv_spin.setRange(0.00, 100_000)
        self.fmv_spin.setDecimals(2)
        self.fmv_spin.setPrefix("$")
        self.fmv_spin.valueChanged.connect(self._update_total)
        form.addRow("Fair Market Value (per unit):", self.fmv_spin)

        # Calculated total FMV (read-only display)
        self.total_label = QLabel("$0.00")
        self.total_label.setStyleSheet(
            f"font-size: 14pt; font-weight: bold; color: {self.THEME_COLOR};"
        )
        form.addRow("Total Impact Value:", self.total_label)

        # Donor name
        self.donor_input = QLineEdit()
        self.donor_input.setPlaceholderText("e.g., Local Church")
        form.addRow("Donor:", self.donor_input)

    def _update_total(self):
        """Recalculate and display total fair market value."""
        total = self.quantity_spin.value() * self.fmv_spin.value()
        self.total_label.setText(f"${total:,.2f}")

    def _save(self):
        """Validate inputs and record the donation transaction."""
        if not self.selected_item_id:
            QMessageBox.warning(self, "Validation Error", "Please enter a valid SKU")
            return

        quantity = self.quantity_spin.value()
        fmv = self.fmv_spin.value()
        donor = self.donor_input.text().strip() or None
        notes = self.notes_input.toPlainText().strip() or None

        try:
            item, transaction = self.service.process_donation(
                item_id=self.selected_item_id,
                quantity=quantity,
                fair_market_value_dollars=fmv,
                donor=donor,
                notes=notes,
            )

            QMessageBox.information(
                self,
                "Success",
                f"Donation recorded!\n\n"
                f"Item: {item.name}\n"
                f"New Quantity: {item.quantity_on_hand:.1f}\n"
                f"New Unit Cost: ${item.current_unit_cost_dollars:.2f}\n"
                f"Impact Value: ${transaction.fair_market_value_dollars:.2f}",
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to record donation: {e}")
