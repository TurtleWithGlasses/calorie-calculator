#!/usr/bin/env python3
"""
Calorie Tracker Pro - PyQt6 Version
A modern calorie tracking application built with PyQt6.
"""

import sys

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QSpinBox, QTabWidget,
    QFrame, QMessageBox, QFormLayout, QGroupBox, 
    QProgressBar, QStatusBar, QFileDialog,
    QDateEdit
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont, QAction, QKeySequence

from database import DatabaseManager
from meal_manager import MealManagerDialog
from analytics_widget import AnalyticsWidget
from meal_section_widget import MealSectionWidget


class ModernCalorieTracker(QMainWindow):
    """Main application window with modern PyQt6 interface."""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.current_date = QDate.currentDate()
        self.meal_sections = []
        self.total_calories = 0
        
        self.init_ui()
        self.setup_connections()
        self.load_data()
            
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("Calorie Tracker Pro")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(800, 600)
        
        # Apply modern styling
        self.apply_modern_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create header section
        self.create_header_section(main_layout)
        
        # Create main content area with tabs
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
    def apply_modern_theme(self):
        """Apply modern theme styling."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
                color: #2C3E50;
            }
            
            QPushButton {
                background-color: #2E86AB;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            
            QPushButton:hover {
                background-color: #A23B72;
            }
            
            QPushButton:pressed {
                background-color: #F18F01;
            }
            
            QLineEdit, QComboBox, QSpinBox {
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #2E86AB;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            
            QTabWidget::pane {
                border: 1px solid #C0C0C0;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #F0F0F0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            
            QTabBar::tab:selected {
                background-color: #2E86AB;
                color: white;
            }
        """)
        
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        export_action = QAction('&Export Data...', self)
        export_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        export_action.triggered.connect(self.export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        manage_meals_action = QAction('&Manage Meals...', self)
        manage_meals_action.triggered.connect(self.open_meal_manager)
        tools_menu.addAction(manage_meals_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_header_section(self, parent_layout):
        """Create the header section with date picker and controls."""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.Shape.Box)
        header_layout = QHBoxLayout(header_frame)
        
        # Date selection
        date_label = QLabel("Selected Date:")
        date_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        self.date_edit = QDateEdit()
        self.date_edit.setDate(self.current_date)
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        
        # Quick date buttons
        today_btn = QPushButton("Today")
        yesterday_btn = QPushButton("Yesterday")
        tomorrow_btn = QPushButton("Tomorrow")
        
        today_btn.clicked.connect(lambda: self.set_date(QDate.currentDate()))
        yesterday_btn.clicked.connect(lambda: self.set_date(QDate.currentDate().addDays(-1)))
        tomorrow_btn.clicked.connect(lambda: self.set_date(QDate.currentDate().addDays(1)))
        
        # Action buttons
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_data)
        
        manage_meals_btn = QPushButton("Manage Meals")
        manage_meals_btn.clicked.connect(self.open_meal_manager)
        
        # Add to layout
        header_layout.addWidget(date_label)
        header_layout.addWidget(self.date_edit)
        header_layout.addWidget(today_btn)
        header_layout.addWidget(yesterday_btn)
        header_layout.addWidget(tomorrow_btn)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)
        header_layout.addWidget(manage_meals_btn)
        
        parent_layout.addWidget(header_frame)
        
    def create_main_content(self, parent_layout):
        """Create the main content area with tabs."""
        self.tab_widget = QTabWidget()
        
        # Daily tracking tab
        self.daily_tab = self.create_daily_tracking_tab()
        self.tab_widget.addTab(self.daily_tab, "Daily Tracking")
        
        # Analytics tab
        self.analytics_tab = self.create_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "Analytics")
        
        # Goals tab
        self.goals_tab = self.create_goals_tab()
        self.tab_widget.addTab(self.goals_tab, "Goals")
        
        parent_layout.addWidget(self.tab_widget)
        
    def create_daily_tracking_tab(self):
        """Create the daily tracking tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Create meal sections
        self.breakfast_section = MealSectionWidget("Breakfast (6:00-11:00)", 0, self.db_manager, self)
        self.lunch_section = MealSectionWidget("Lunch (11:00-16:00)", 1, self.db_manager, self)
        self.dinner_section = MealSectionWidget("Dinner (16:00-21:00)", 2, self.db_manager, self)
        self.snacks_section = MealSectionWidget("Snacks (21:00-6:00)", 3, self.db_manager, self)
        
        self.meal_sections = [
            self.breakfast_section,
            self.lunch_section, 
            self.dinner_section,
            self.snacks_section
        ]
        
        # Add sections to layout
        for section in self.meal_sections:
            layout.addWidget(section)
            
        # Total calories display
        self.total_calories_frame = QFrame()
        total_layout = QHBoxLayout(self.total_calories_frame)
        
        self.total_calories_label = QLabel("Total Calories: 0")
        self.total_calories_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.total_calories_label.setStyleSheet("color: #2E86AB;")
        
        self.calorie_progress = QProgressBar()
        self.calorie_progress.setMaximum(3000)  # Assuming 3000 cal daily goal
        self.calorie_progress.setValue(0)
        self.calorie_progress.setFormat("Goal Progress: %p%")
        
        total_layout.addWidget(self.total_calories_label)
        total_layout.addWidget(self.calorie_progress)
        
        layout.addWidget(self.total_calories_frame)
        
        return tab
        
    def create_analytics_tab(self):
        """Create the analytics tab."""
        self.analytics_widget = AnalyticsWidget(self.db_manager, self)
        return self.analytics_widget
        
    def create_goals_tab(self):
        """Create the goals tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Daily calorie goal
        goal_group = QGroupBox("Daily Calorie Goal")
        goal_layout = QFormLayout(goal_group)
        
        self.daily_goal_spin = QSpinBox()
        self.daily_goal_spin.setRange(1000, 5000)
        self.daily_goal_spin.setValue(2000)
        
        goal_layout.addRow("Target Calories:", self.daily_goal_spin)
        
        update_goal_btn = QPushButton("Update Goal")
        update_goal_btn.clicked.connect(self.update_goal)
        goal_layout.addRow(update_goal_btn)
        
        layout.addWidget(goal_group)
        layout.addStretch()
        
        return tab
        
    def create_status_bar(self):
        """Create the status bar."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        
        # Connection status
        self.connection_label = QLabel("● Connected")
        self.connection_label.setStyleSheet("color: green;")
        self.status_bar.addPermanentWidget(self.connection_label)
        
    def setup_connections(self):
        """Setup signal connections."""
        self.date_edit.dateChanged.connect(self.on_date_changed)
        
        # Connect meal section signals
        for section in self.meal_sections:
            section.calories_changed.connect(self.update_total_calories)
            
    def load_data(self):
        """Load data for the current date."""
        date_str = self.current_date.toString("yyyy-MM-dd")
        
        # Load meals for each section
        for section in self.meal_sections:
            section.load_meals_for_date(date_str)
            
        self.update_total_calories()
        
    def refresh_meal_options(self):
        """Refresh meal options in all sections."""
        for section in self.meal_sections:
            section.refresh_meal_options()
        
    def set_date(self, date: QDate):
        """Set the current date and load data."""
        self.current_date = date
        self.date_edit.setDate(date)
        self.load_data()
        
    def on_date_changed(self, date: QDate):
        """Handle date change."""
        self.set_date(date)
        
    def update_total_calories(self):
        """Update the total calories display."""
        total = sum(section.get_total_calories() for section in self.meal_sections)
        self.total_calories = total
        
        self.total_calories_label.setText(f"Total Calories: {total}")
        self.calorie_progress.setValue(total)
        
        # Update status
        self.status_label.setText(f"Total calories: {total}")
        
    def refresh_data(self):
        """Refresh all data."""
        self.load_data()
        self.status_label.setText("Data refreshed")
        
    def open_meal_manager(self):
        """Open the meal management dialog."""
        dialog = MealManagerDialog(self.db_manager, self)
        dialog.meal_updated.connect(self.refresh_meal_options)
        dialog.exec()
        
    def export_data(self):
        """Export data to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                if self.db_manager.export_data(file_path):
                    QMessageBox.information(self, "Success", "Data exported successfully!")
                else:
                    QMessageBox.critical(self, "Error", "Failed to export data!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
        
    def update_goal(self):
        """Update daily calorie goal."""
        goal = self.daily_goal_spin.value()
        self.calorie_progress.setMaximum(goal)
        self.update_total_calories()
        QMessageBox.information(self, "Success", f"Goal updated to {goal} calories")
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
            "Calorie Tracker Pro v2.0\n\n"
            "A modern calorie tracking application built with PyQt6.\n"
            "Features include meal management, analytics, and data export."
        )


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Calorie Tracker Pro")
    app.setApplicationVersion("2.0.0")
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ModernCalorieTracker()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()