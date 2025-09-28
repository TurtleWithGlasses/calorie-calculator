"""
Enhanced meal management dialog with modern UI and advanced features.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
    QPushButton, QLineEdit, QSpinBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QTabWidget, QWidget, QGroupBox,
    QFormLayout, QComboBox, QCheckBox, QTextEdit, QSplitter,
    QFrame, QScrollArea, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from typing import List, Dict, Optional
import logging

from database_improved import DatabaseManager

logger = logging.getLogger(__name__)


class MealManagerDialog(QDialog):
    """Enhanced meal management dialog with modern UI."""
    
    meal_updated = pyqtSignal()
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_meals = []
        self.setup_ui()
        self.load_meals()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Meal Manager")
        self.setModal(True)
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Browse meals tab
        self.browse_tab = self.create_browse_tab()
        self.tab_widget.addTab(self.browse_tab, "Browse Meals")
        
        # Add meal tab
        self.add_tab = self.create_add_meal_tab()
        self.tab_widget.addTab(self.add_tab, "Add Meal")
        
        # Import/Export tab
        self.import_tab = self.create_import_tab()
        self.tab_widget.addTab(self.import_tab, "Import/Export")
        
        layout.addWidget(self.tab_widget)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_meals)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def create_browse_tab(self):
        """Create the browse meals tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Search and filter section
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search meals...")
        self.search_edit.textChanged.connect(self.filter_meals)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "High Protein", "Low Calorie", "High Fiber"])
        self.filter_combo.currentTextChanged.connect(self.filter_meals)
        
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_edit)
        search_layout.addWidget(QLabel("Filter:"))
        search_layout.addWidget(self.filter_combo)
        search_layout.addStretch()
        
        layout.addWidget(search_frame)
        
        # Meals table
        self.meals_table = QTableWidget()
        self.meals_table.setColumnCount(8)
        self.meals_table.setHorizontalHeaderLabels([
            "Name", "Calories", "Protein", "Carbs", "Fat", 
            "Fiber", "Sugar", "Sodium"
        ])
        
        # Configure table
        header = self.meals_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 8):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        
        self.meals_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.meals_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.meals_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.edit_selected_meal)
        self.edit_btn.setEnabled(False)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected_meal)
        self.delete_btn.setEnabled(False)
        
        self.duplicate_btn = QPushButton("Duplicate Selected")
        self.duplicate_btn.clicked.connect(self.duplicate_selected_meal)
        self.duplicate_btn.setEnabled(False)
        
        action_layout.addWidget(self.edit_btn)
        action_layout.addWidget(self.delete_btn)
        action_layout.addWidget(self.duplicate_btn)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # Connect table selection
        self.meals_table.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        return tab
        
    def create_add_meal_tab(self):
        """Create the add meal tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Basic information group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(basic_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter meal name...")
        
        self.calories_spin = QSpinBox()
        self.calories_spin.setRange(0, 10000)
        self.calories_spin.setValue(100)
        
        basic_layout.addRow("Name:", self.name_edit)
        basic_layout.addRow("Calories (per 100g):", self.calories_spin)
        
        layout.addWidget(basic_group)
        
        # Macronutrients group
        macro_group = QGroupBox("Macronutrients (per 100g)")
        macro_layout = QGridLayout(macro_group)
        
        self.protein_spin = QSpinBox()
        self.protein_spin.setRange(0, 1000)
        self.protein_spin.setSuffix(" g")
        
        self.carbs_spin = QSpinBox()
        self.carbs_spin.setRange(0, 1000)
        self.carbs_spin.setSuffix(" g")
        
        self.fat_spin = QSpinBox()
        self.fat_spin.setRange(0, 1000)
        self.fat_spin.setSuffix(" g")
        
        self.fiber_spin = QSpinBox()
        self.fiber_spin.setRange(0, 1000)
        self.fiber_spin.setSuffix(" g")
        
        self.sugar_spin = QSpinBox()
        self.sugar_spin.setRange(0, 1000)
        self.sugar_spin.setSuffix(" g")
        
        self.sodium_spin = QSpinBox()
        self.sodium_spin.setRange(0, 10000)
        self.sodium_spin.setSuffix(" mg")
        
        macro_layout.addWidget(QLabel("Protein:"), 0, 0)
        macro_layout.addWidget(self.protein_spin, 0, 1)
        macro_layout.addWidget(QLabel("Carbs:"), 0, 2)
        macro_layout.addWidget(self.carbs_spin, 0, 3)
        
        macro_layout.addWidget(QLabel("Fat:"), 1, 0)
        macro_layout.addWidget(self.fat_spin, 1, 1)
        macro_layout.addWidget(QLabel("Fiber:"), 1, 2)
        macro_layout.addWidget(self.fiber_spin, 1, 3)
        
        macro_layout.addWidget(QLabel("Sugar:"), 2, 0)
        macro_layout.addWidget(self.sugar_spin, 2, 1)
        macro_layout.addWidget(QLabel("Sodium:"), 2, 2)
        macro_layout.addWidget(self.sodium_spin, 2, 3)
        
        layout.addWidget(macro_group)
        
        # Add meal button
        self.add_meal_btn = QPushButton("Add Meal")
        self.add_meal_btn.clicked.connect(self.add_meal)
        self.add_meal_btn.setStyleSheet("""
            QPushButton {
                background-color: #27AE60;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        layout.addWidget(self.add_meal_btn)
        layout.addStretch()
        
        return tab
        
    def create_import_tab(self):
        """Create the import/export tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Export section
        export_group = QGroupBox("Export Meals")
        export_layout = QVBoxLayout(export_group)
        
        export_info = QLabel("Export all meals to a file for backup or sharing.")
        export_info.setWordWrap(True)
        export_layout.addWidget(export_info)
        
        self.export_btn = QPushButton("Export to CSV")
        self.export_btn.clicked.connect(self.export_meals)
        export_layout.addWidget(self.export_btn)
        
        layout.addWidget(export_group)
        
        # Import section
        import_group = QGroupBox("Import Meals")
        import_layout = QVBoxLayout(import_group)
        
        import_info = QLabel("Import meals from a JSON file.")
        import_info.setWordWrap(True)
        import_layout.addWidget(import_info)
        
        self.import_btn = QPushButton("Import from JSON")
        self.import_btn.clicked.connect(self.import_meals)
        import_layout.addWidget(self.import_btn)
        
        layout.addWidget(import_group)
        
        # Statistics section
        stats_group = QGroupBox("Database Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Loading statistics...")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        # Load statistics
        self.load_statistics()
        
        return tab
        
    def load_meals(self):
        """Load meals from database."""
        try:
            # Get all meals (simplified for now)
            meals = self.db_manager.search_meals("", limit=1000)
            self.current_meals = meals
            
            # Populate table
            self.meals_table.setRowCount(len(meals))
            
            for row, meal in enumerate(meals):
                self.meals_table.setItem(row, 0, QTableWidgetItem(meal['name']))
                self.meals_table.setItem(row, 1, QTableWidgetItem(str(meal['calories'])))
                self.meals_table.setItem(row, 2, QTableWidgetItem(str(meal.get('protein', 0))))
                self.meals_table.setItem(row, 3, QTableWidgetItem(str(meal.get('carbs', 0))))
                self.meals_table.setItem(row, 4, QTableWidgetItem(str(meal.get('fat', 0))))
                self.meals_table.setItem(row, 5, QTableWidgetItem(str(meal.get('fiber', 0))))
                self.meals_table.setItem(row, 6, QTableWidgetItem(str(meal.get('sugar', 0))))
                self.meals_table.setItem(row, 7, QTableWidgetItem(str(meal.get('sodium', 0))))
                
        except Exception as e:
            logger.error(f"Failed to load meals: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load meals: {str(e)}")
            
    def filter_meals(self):
        """Filter meals based on search and filter criteria."""
        search_text = self.search_edit.text().lower()
        filter_type = self.filter_combo.currentText()
        
        filtered_meals = []
        for meal in self.current_meals:
            # Apply search filter
            if search_text and search_text not in meal['name'].lower():
                continue
                
            # Apply type filter
            if filter_type == "High Protein" and meal.get('protein', 0) < 20:
                continue
            elif filter_type == "Low Calorie" and meal['calories'] > 200:
                continue
            elif filter_type == "High Fiber" and meal.get('fiber', 0) < 5:
                continue
                
            filtered_meals.append(meal)
            
        # Update table
        self.meals_table.setRowCount(len(filtered_meals))
        for row, meal in enumerate(filtered_meals):
            self.meals_table.setItem(row, 0, QTableWidgetItem(meal['name']))
            self.meals_table.setItem(row, 1, QTableWidgetItem(str(meal['calories'])))
            self.meals_table.setItem(row, 2, QTableWidgetItem(str(meal.get('protein', 0))))
            self.meals_table.setItem(row, 3, QTableWidgetItem(str(meal.get('carbs', 0))))
            self.meals_table.setItem(row, 4, QTableWidgetItem(str(meal.get('fat', 0))))
            self.meals_table.setItem(row, 5, QTableWidgetItem(str(meal.get('fiber', 0))))
            self.meals_table.setItem(row, 6, QTableWidgetItem(str(meal.get('sugar', 0))))
            self.meals_table.setItem(row, 7, QTableWidgetItem(str(meal.get('sodium', 0))))
            
    def on_selection_changed(self):
        """Handle table selection change."""
        has_selection = len(self.meals_table.selectedItems()) > 0
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.duplicate_btn.setEnabled(has_selection)
        
    def edit_selected_meal(self):
        """Edit the selected meal."""
        current_row = self.meals_table.currentRow()
        if current_row >= 0:
            meal_name = self.meals_table.item(current_row, 0).text()
            self.edit_meal(meal_name)
            
    def edit_meal(self, meal_name: str):
        """Edit a specific meal."""
        # Get meal data
        meal_data = self.db_manager.get_meal(meal_name)
        if not meal_data:
            QMessageBox.warning(self, "Error", "Meal not found!")
            return
            
        # Create edit dialog
        dialog = MealEditDialog(meal_data, self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_meals()
            self.meal_updated.emit()
            
    def delete_selected_meal(self):
        """Delete the selected meal."""
        current_row = self.meals_table.currentRow()
        if current_row >= 0:
            meal_name = self.meals_table.item(current_row, 0).text()
            
            reply = QMessageBox.question(
                self, "Confirm Delete",
                f"Are you sure you want to delete '{meal_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db_manager.delete_meal(meal_name):
                    QMessageBox.information(self, "Success", "Meal deleted successfully!")
                    self.load_meals()
                    self.meal_updated.emit()
                else:
                    QMessageBox.critical(self, "Error", "Failed to delete meal!")
                    
    def duplicate_selected_meal(self):
        """Duplicate the selected meal."""
        current_row = self.meals_table.currentRow()
        if current_row >= 0:
            meal_name = self.meals_table.item(current_row, 0).text()
            meal_data = self.db_manager.get_meal(meal_name)
            
            if meal_data:
                # Pre-fill add form with duplicated data
                self.tab_widget.setCurrentIndex(1)  # Switch to add tab
                self.name_edit.setText(f"{meal_data['name']} (Copy)")
                self.calories_spin.setValue(meal_data['calories'])
                self.protein_spin.setValue(meal_data.get('protein', 0))
                self.carbs_spin.setValue(meal_data.get('carbs', 0))
                self.fat_spin.setValue(meal_data.get('fat', 0))
                self.fiber_spin.setValue(meal_data.get('fiber', 0))
                self.sugar_spin.setValue(meal_data.get('sugar', 0))
                self.sodium_spin.setValue(meal_data.get('sodium', 0))
                
    def add_meal(self):
        """Add a new meal."""
        name = self.name_edit.text().strip()
        calories = self.calories_spin.value()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a meal name!")
            return
            
        # Collect macro data
        macros = {
            'protein': self.protein_spin.value(),
            'carbs': self.carbs_spin.value(),
            'fat': self.fat_spin.value(),
            'fiber': self.fiber_spin.value(),
            'sugar': self.sugar_spin.value(),
            'sodium': self.sodium_spin.value()
        }
        
        if self.db_manager.add_meal(name, calories, **macros):
            QMessageBox.information(self, "Success", "Meal added successfully!")
            self.clear_form()
            self.load_meals()
            self.meal_updated.emit()
        else:
            QMessageBox.critical(self, "Error", "Failed to add meal! It may already exist.")
            
    def clear_form(self):
        """Clear the add meal form."""
        self.name_edit.clear()
        self.calories_spin.setValue(100)
        self.protein_spin.setValue(0)
        self.carbs_spin.setValue(0)
        self.fat_spin.setValue(0)
        self.fiber_spin.setValue(0)
        self.sugar_spin.setValue(0)
        self.sodium_spin.setValue(0)
        
    def export_meals(self):
        """Export meals to file."""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Meals", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            if self.db_manager.export_data(file_path):
                QMessageBox.information(self, "Success", "Meals exported successfully!")
            else:
                QMessageBox.critical(self, "Error", "Failed to export meals!")
                
    def import_meals(self):
        """Import meals from file."""
        from PyQt6.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Meals", "", "JSON Files (*.json)"
        )
        
        if file_path:
            if self.db_manager.import_data(file_path):
                QMessageBox.information(self, "Success", "Meals imported successfully!")
                self.load_meals()
                self.meal_updated.emit()
            else:
                QMessageBox.critical(self, "Error", "Failed to import meals!")
                
    def load_statistics(self):
        """Load database statistics."""
        try:
            # This would be implemented with actual statistics
            stats_text = f"""
            <b>Database Statistics:</b><br>
            • Total Meals: {len(self.current_meals)}<br>
            • Average Calories: {sum(m['calories'] for m in self.current_meals) / len(self.current_meals) if self.current_meals else 0:.1f}<br>
            • High Protein Meals: {len([m for m in self.current_meals if m.get('protein', 0) > 20])}<br>
            • Low Calorie Meals: {len([m for m in self.current_meals if m['calories'] < 200])}
            """
            self.stats_label.setText(stats_text)
        except Exception as e:
            self.stats_label.setText(f"Error loading statistics: {str(e)}")


class MealEditDialog(QDialog):
    """Dialog for editing an existing meal."""
    
    def __init__(self, meal_data: Dict, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.meal_data = meal_data
        self.original_name = meal_data['name']
        self.setup_ui()
        self.load_data()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Edit Meal")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.calories_spin = QSpinBox()
        self.calories_spin.setRange(0, 10000)
        
        self.protein_spin = QSpinBox()
        self.protein_spin.setRange(0, 1000)
        self.protein_spin.setSuffix(" g")
        
        self.carbs_spin = QSpinBox()
        self.carbs_spin.setRange(0, 1000)
        self.carbs_spin.setSuffix(" g")
        
        self.fat_spin = QSpinBox()
        self.fat_spin.setRange(0, 1000)
        self.fat_spin.setSuffix(" g")
        
        self.fiber_spin = QSpinBox()
        self.fiber_spin.setRange(0, 1000)
        self.fiber_spin.setSuffix(" g")
        
        self.sugar_spin = QSpinBox()
        self.sugar_spin.setRange(0, 1000)
        self.sugar_spin.setSuffix(" g")
        
        self.sodium_spin = QSpinBox()
        self.sodium_spin.setRange(0, 10000)
        self.sodium_spin.setSuffix(" mg")
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Calories (per 100g):", self.calories_spin)
        form_layout.addRow("Protein:", self.protein_spin)
        form_layout.addRow("Carbs:", self.carbs_spin)
        form_layout.addRow("Fat:", self.fat_spin)
        form_layout.addRow("Fiber:", self.fiber_spin)
        form_layout.addRow("Sugar:", self.sugar_spin)
        form_layout.addRow("Sodium:", self.sodium_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_meal)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
    def load_data(self):
        """Load meal data into the form."""
        self.name_edit.setText(self.meal_data['name'])
        self.calories_spin.setValue(self.meal_data['calories'])
        self.protein_spin.setValue(self.meal_data.get('protein', 0))
        self.carbs_spin.setValue(self.meal_data.get('carbs', 0))
        self.fat_spin.setValue(self.meal_data.get('fat', 0))
        self.fiber_spin.setValue(self.meal_data.get('fiber', 0))
        self.sugar_spin.setValue(self.meal_data.get('sugar', 0))
        self.sodium_spin.setValue(self.meal_data.get('sodium', 0))
        
    def save_meal(self):
        """Save the edited meal."""
        name = self.name_edit.text().strip()
        calories = self.calories_spin.value()
        
        if not name:
            QMessageBox.warning(self, "Error", "Please enter a meal name!")
            return
            
        macros = {
            'protein': self.protein_spin.value(),
            'carbs': self.carbs_spin.value(),
            'fat': self.fat_spin.value(),
            'fiber': self.fiber_spin.value(),
            'sugar': self.sugar_spin.value(),
            'sodium': self.sodium_spin.value()
        }
        
        if self.db_manager.update_meal(self.original_name, name, calories, **macros):
            QMessageBox.information(self, "Success", "Meal updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to update meal!")
