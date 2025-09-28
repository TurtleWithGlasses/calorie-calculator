"""
Modern meal section widget for tracking meals in different time periods.
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QComboBox, QSpinBox, QTableWidget,
    QHeaderView, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Dict
import logging

from database import DatabaseManager

logger = logging.getLogger(__name__)


class MealSectionWidget(QGroupBox):
    """Widget for managing meals in a specific time period."""
    
    calories_changed = pyqtSignal()
    
    def __init__(self, title: str, section_index: int, db_manager: DatabaseManager, parent=None):
        super().__init__(title, parent)
        self.section_index = section_index
        self.db_manager = db_manager
        self.meal_rows = []
        self.meal_options = []
        
        self.setup_ui()
        self.load_meal_options()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header with total calories
        header_layout = QHBoxLayout()
        
        self.total_label = QLabel("Total: 0 calories")
        self.total_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #2E86AB;")
        
        self.add_meal_btn = QPushButton("+ Add Meal")
        self.add_meal_btn.clicked.connect(self.add_meal_row)
        self.add_meal_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        self.clear_btn = QPushButton("Clear All")
        self.clear_btn.clicked.connect(self.clear_all)
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        
        header_layout.addWidget(self.total_label)
        header_layout.addStretch()
        header_layout.addWidget(self.add_meal_btn)
        header_layout.addWidget(self.clear_btn)
        
        layout.addLayout(header_layout)
        
        # Meals table
        self.meals_table = QTableWidget()
        self.meals_table.setColumnCount(5)
        self.meals_table.setHorizontalHeaderLabels([
            "Meal", "Quantity (g)", "Calories", "Protein", "Actions"
        ])
        
        # Configure table
        header = self.meals_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        # Set row height to accommodate widgets properly
        self.meals_table.verticalHeader().setDefaultSectionSize(40)
        self.meals_table.setAlternatingRowColors(True)
        self.meals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # Set minimum row height and ensure proper spacing
        self.meals_table.setMinimumHeight(200)
        self.meals_table.setVerticalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        self.meals_table.setHorizontalScrollMode(QTableWidget.ScrollMode.ScrollPerPixel)
        
        layout.addWidget(self.meals_table)
        
        # Add initial empty row
        self.add_meal_row()
        
    def load_meal_options(self):
        """Load available meals from database."""
        try:
            meals = self.db_manager.search_meals("", limit=1000)
            self.meal_options = [meal['name'] for meal in meals]
        except Exception as e:
            logger.error(f"Failed to load meal options: {e}")
            self.meal_options = []
            
    def refresh_meal_options(self):
        """Refresh meal options from database."""
        self.load_meal_options()
        self.update_meal_combos()
        
    def add_meal_row(self):
        """Add a new meal row to the table."""
        row = self.meals_table.rowCount()
        self.meals_table.insertRow(row)
        
        # Meal selection combo
        meal_combo = QComboBox()
        meal_combo.setEditable(True)
        meal_combo.addItems(self.meal_options)
        meal_combo.setCurrentText("")
        meal_combo.setMinimumHeight(30)
        meal_combo.currentTextChanged.connect(lambda: self.on_meal_changed(row))
        meal_combo.editTextChanged.connect(lambda: self.search_meals(meal_combo))
        
        # Quantity spinbox
        quantity_spin = QSpinBox()
        quantity_spin.setRange(1, 10000)
        quantity_spin.setValue(100)
        quantity_spin.setSuffix(" g")
        quantity_spin.setMinimumHeight(30)
        quantity_spin.valueChanged.connect(lambda: self.calculate_calories(row))
        
        # Calories label
        calories_label = QLabel("0")
        calories_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        calories_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        
        # Protein label
        protein_label = QLabel("0")
        protein_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        protein_label.setStyleSheet("color: #27AE60;")
        
        # Delete button
        delete_btn = QPushButton("×")
        delete_btn.setMaximumWidth(30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                color: white;
                border: none;
                border-radius: 3px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_meal_row(row))
        
        # Add widgets to table
        self.meals_table.setCellWidget(row, 0, meal_combo)
        self.meals_table.setCellWidget(row, 1, quantity_spin)
        self.meals_table.setCellWidget(row, 2, calories_label)
        self.meals_table.setCellWidget(row, 3, protein_label)
        self.meals_table.setCellWidget(row, 4, delete_btn)
        
        # Store row data
        self.meal_rows.append({
            'meal_combo': meal_combo,
            'quantity_spin': quantity_spin,
            'calories_label': calories_label,
            'protein_label': protein_label,
            'delete_btn': delete_btn
        })
        
    def delete_meal_row(self, row: int):
        """Delete a meal row from the table."""
        if row < self.meals_table.rowCount():
            self.meals_table.removeRow(row)
            if row < len(self.meal_rows):
                del self.meal_rows[row]
            self.calculate_total_calories()
            
    def clear_all(self):
        """Clear all meal rows."""
        reply = QMessageBox.question(
            self, "Clear All",
            "Are you sure you want to clear all meals in this section?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.meals_table.setRowCount(0)
            self.meal_rows.clear()
            self.add_meal_row()  # Add one empty row
            self.calculate_total_calories()
            
    def search_meals(self, combo: QComboBox):
        """Search for meals as user types."""
        search_text = combo.currentText().lower()
        if len(search_text) >= 2:
            try:
                meals = self.db_manager.search_meals(search_text, limit=20)
                meal_names = [meal['name'] for meal in meals]
                combo.clear()
                combo.addItems(meal_names)
                combo.showPopup()
            except Exception as e:
                logger.error(f"Failed to search meals: {e}")
                
    def on_meal_changed(self, row: int):
        """Handle meal selection change."""
        if row < len(self.meal_rows):
            self.calculate_calories(row)
            
    def calculate_calories(self, row: int):
        """Calculate calories for a specific row."""
        if row >= len(self.meal_rows):
            return
            
        row_data = self.meal_rows[row]
        meal_name = row_data['meal_combo'].currentText().strip()
        quantity = row_data['quantity_spin'].value()
        
        if meal_name:
            try:
                meal_data = self.db_manager.get_meal(meal_name)
                if meal_data:
                    # Calculate calories per 100g
                    calories_per_100g = meal_data['calories']
                    total_calories = (calories_per_100g * quantity) / 100
                    
                    # Calculate protein per 100g
                    protein_per_100g = meal_data.get('protein', 0)
                    total_protein = (protein_per_100g * quantity) / 100
                    
                    row_data['calories_label'].setText(f"{total_calories:.0f}")
                    row_data['protein_label'].setText(f"{total_protein:.1f}g")
                else:
                    row_data['calories_label'].setText("0")
                    row_data['protein_label'].setText("0g")
            except Exception as e:
                logger.error(f"Failed to calculate calories: {e}")
                row_data['calories_label'].setText("0")
                row_data['protein_label'].setText("0g")
        else:
            row_data['calories_label'].setText("0")
            row_data['protein_label'].setText("0g")
            
        self.calculate_total_calories()
        
    def calculate_total_calories(self):
        """Calculate total calories for this section."""
        total_calories = 0
        total_protein = 0
        
        for row_data in self.meal_rows:
            try:
                calories_text = row_data['calories_label'].text()
                protein_text = row_data['protein_label'].text()
                
                if calories_text and calories_text != "0":
                    total_calories += float(calories_text)
                    
                if protein_text and protein_text != "0g":
                    protein_value = float(protein_text.replace('g', ''))
                    total_protein += protein_value
            except (ValueError, AttributeError):
                continue
                
        self.total_label.setText(f"Total: {total_calories:.0f} calories, {total_protein:.1f}g protein")
        self.calories_changed.emit()
        
    def get_total_calories(self) -> float:
        """Get total calories for this section."""
        total = 0
        for row_data in self.meal_rows:
            try:
                calories_text = row_data['calories_label'].text()
                if calories_text and calories_text != "0":
                    total += float(calories_text)
            except (ValueError, AttributeError):
                continue
        return total
        
    def get_meals_data(self) -> List[Dict]:
        """Get meals data for saving to database."""
        meals = []
        
        for row_data in self.meal_rows:
            meal_name = row_data['meal_combo'].currentText().strip()
            quantity = row_data['quantity_spin'].value()
            calories_text = row_data['calories_label'].text()
            
            if meal_name and calories_text and calories_text != "0":
                try:
                    calories = float(calories_text)
                    meals.append({
                        'name': meal_name,
                        'grams': quantity,
                        'calories': calories,
                        'section_index': self.section_index
                    })
                except ValueError:
                    continue
                    
        return meals
        
    def load_meals_for_date(self, date: str):
        """Load meals for a specific date."""
        try:
            # Clear existing meals
            self.meals_table.setRowCount(0)
            self.meal_rows.clear()
            
            # Get meals for this section and date
            all_meals = self.db_manager.get_daily_meals(date)
            section_meals = [meal for meal in all_meals if meal['section_index'] == self.section_index]
            
            # Add meals to table
            for meal in section_meals:
                self.add_meal_row()
                row = len(self.meal_rows) - 1
                
                if row < len(self.meal_rows):
                    row_data = self.meal_rows[row]
                    row_data['meal_combo'].setCurrentText(meal['name'])
                    row_data['quantity_spin'].setValue(int(meal['grams']))
                    self.calculate_calories(row)
                    
            # If no meals, add one empty row
            if not section_meals:
                self.add_meal_row()
                
        except Exception as e:
            logger.error(f"Failed to load meals for date: {e}")
            # Ensure at least one empty row
            if not self.meal_rows:
                self.add_meal_row()
                
    def update_meal_combos(self):
        """Update all meal combo boxes with new options."""
        for row_data in self.meal_rows:
            current_text = row_data['meal_combo'].currentText()
            row_data['meal_combo'].clear()
            row_data['meal_combo'].addItems(self.meal_options)
            row_data['meal_combo'].setCurrentText(current_text)
