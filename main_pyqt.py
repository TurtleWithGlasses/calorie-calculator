#!/usr/bin/env python3
"""
Calorie Tracker Pro - Modern PyQt6 Version
A comprehensive calorie tracking application with modern UI and advanced features.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox, 
    QSpinBox, QTableWidget, QTableWidgetItem, QTabWidget,
    QSplitter, QFrame, QScrollArea, QMessageBox, QDialog,
    QDialogButtonBox, QFormLayout, QGroupBox, QProgressBar,
    QStatusBar, QMenuBar, QMenu, QFileDialog, QCalendarWidget,
    QDateEdit, QTextEdit, QCheckBox, QSlider, QProgressDialog
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QDate, QSize, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSettings
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter, 
    QLinearGradient, QBrush, QAction, QKeySequence
)
from PyQt6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet

from database_improved import DatabaseManager
from config import APP_CONFIG, THEME_CONFIG, DB_CONFIG
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
        self.setWindowTitle(f"{APP_CONFIG['title']} v{APP_CONFIG['version']}")
        self.setGeometry(100, 100, APP_CONFIG['window_width'], APP_CONFIG['window_height'])
        self.setMinimumSize(APP_CONFIG['min_width'], APP_CONFIG['min_height'])
        
        # Apply modern styling
        self.apply_modern_theme()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create header section
        self.create_header_section(main_layout)
        
        # Create main content area with tabs
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
    def apply_modern_theme(self):
        """Apply modern dark/light theme styling."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {THEME_CONFIG['background_color']};
                color: {THEME_CONFIG['text_color']};
            }}
            
            QPushButton {{
                background-color: {THEME_CONFIG['primary_color']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}
            
            QPushButton:hover {{
                background-color: {THEME_CONFIG['secondary_color']};
                transform: translateY(-1px);
            }}
            
            QPushButton:pressed {{
                background-color: {THEME_CONFIG['accent_color']};
            }}
            
            QLineEdit, QComboBox, QSpinBox {{
                padding: 8px;
                border: 2px solid #E0E0E0;
                border-radius: 4px;
                background-color: white;
                font-size: 12px;
            }}
            
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border-color: {THEME_CONFIG['primary_color']};
            }}
            
            QGroupBox {{
                font-weight: bold;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            QTabWidget::pane {{
                border: 1px solid #C0C0C0;
                background-color: white;
            }}
            
            QTabBar::tab {{
                background-color: #F0F0F0;
                padding: 8px 16px;
                margin-right: 2px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {THEME_CONFIG['primary_color']};
                color: white;
            }}
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
        
        import_action = QAction('&Import Data...', self)
        import_action.triggered.connect(self.import_data)
        file_menu.addAction(import_action)
        
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
        
        settings_action = QAction('&Settings...', self)
        settings_action.triggered.connect(self.open_settings)
        tools_menu.addAction(settings_action)
        
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
        self.analytics_tab = AnalyticsWidget(self.db_manager)
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
        self.breakfast_section = MealSectionWidget("Breakfast", 0, self.db_manager)
        self.lunch_section = MealSectionWidget("Lunch", 1, self.db_manager)
        self.dinner_section = MealSectionWidget("Dinner", 2, self.db_manager)
        self.snacks_section = MealSectionWidget("Snacks", 3, self.db_manager)
        
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
        self.total_calories_label.setStyleSheet(f"color: {THEME_CONFIG['primary_color']};")
        
        self.calorie_progress = QProgressBar()
        self.calorie_progress.setMaximum(3000)  # Assuming 3000 cal daily goal
        self.calorie_progress.setValue(0)
        self.calorie_progress.setFormat("Goal Progress: %p%")
        
        total_layout.addWidget(self.total_calories_label)
        total_layout.addWidget(self.calorie_progress)
        
        layout.addWidget(self.total_calories_frame)
        
        return tab
        
    def create_goals_tab(self):
        """Create the goals and settings tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Daily calorie goal
        goal_group = QGroupBox("Daily Calorie Goal")
        goal_layout = QFormLayout(goal_group)
        
        self.daily_goal_spin = QSpinBox()
        self.daily_goal_spin.setRange(1000, 5000)
        self.daily_goal_spin.setValue(2000)
        
        goal_layout.addRow("Target Calories:", self.daily_goal_spin)
        
        # Macro goals
        macro_group = QGroupBox("Macro Goals")
        macro_layout = QFormLayout(macro_group)
        
        self.protein_goal = QSpinBox()
        self.protein_goal.setRange(0, 500)
        self.protein_goal.setValue(150)
        
        self.carbs_goal = QSpinBox()
        self.carbs_goal.setRange(0, 500)
        self.carbs_goal.setValue(250)
        
        self.fat_goal = QSpinBox()
        self.fat_goal.setRange(0, 200)
        self.fat_goal.setValue(65)
        
        macro_layout.addRow("Protein (g):", self.protein_goal)
        macro_layout.addRow("Carbs (g):", self.carbs_goal)
        macro_layout.addRow("Fat (g):", self.fat_goal)
        
        layout.addWidget(goal_group)
        layout.addWidget(macro_group)
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
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Refresh meal options in all sections
            for section in self.meal_sections:
                section.refresh_meal_options()
                
    def export_data(self):
        """Export data to file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Data", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.db_manager.export_data(file_path)
                QMessageBox.information(self, "Success", "Data exported successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")
                
    def import_data(self):
        """Import data from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Import Data", "", "CSV Files (*.csv);;JSON Files (*.json)"
        )
        
        if file_path:
            try:
                self.db_manager.import_data(file_path)
                QMessageBox.information(self, "Success", "Data imported successfully!")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import data: {str(e)}")
                
    def open_settings(self):
        """Open settings dialog."""
        QMessageBox.information(self, "Settings", "Settings dialog coming soon!")
        
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", 
            f"{APP_CONFIG['title']} v{APP_CONFIG['version']}\n\n"
            "A modern calorie tracking application built with PyQt6.\n"
            "Features include meal management, analytics, and data export."
        )


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_CONFIG['title'])
    app.setApplicationVersion(APP_CONFIG['version'])
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = ModernCalorieTracker()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
