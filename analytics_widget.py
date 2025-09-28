"""
Analytics widget with charts and data visualization for calorie tracking.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QComboBox, QFrame, QGridLayout, QGroupBox,
    QScrollArea, QTabWidget
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCharts import (
    QChart, QChartView, QLineSeries, QBarSeries, QBarSet,
    QValueAxis, QDateTimeAxis, QPieSeries, QPieSlice
)
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

from database_improved import DatabaseManager

logger = logging.getLogger(__name__)


class AnalyticsWidget(QWidget):
    """Widget for displaying analytics and charts."""
    
    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setup_ui()
        self.load_analytics()
        
    def setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Header with date range selection
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Date range selection
        header_layout.addWidget(QLabel("From:"))
        self.start_date = QDateEdit()
        self.start_date.setDate(QDate.currentDate().addDays(-30))
        self.start_date.setCalendarPopup(True)
        self.start_date.dateChanged.connect(self.load_analytics)
        
        header_layout.addWidget(self.start_date)
        header_layout.addWidget(QLabel("To:"))
        
        self.end_date = QDateEdit()
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.dateChanged.connect(self.load_analytics)
        
        header_layout.addWidget(self.end_date)
        
        # Quick range buttons
        self.last_week_btn = QPushButton("Last Week")
        self.last_week_btn.clicked.connect(self.set_last_week)
        
        self.last_month_btn = QPushButton("Last Month")
        self.last_month_btn.clicked.connect(self.set_last_month)
        
        self.last_3months_btn = QPushButton("Last 3 Months")
        self.last_3months_btn.clicked.connect(self.set_last_3months)
        
        header_layout.addWidget(self.last_week_btn)
        header_layout.addWidget(self.last_month_btn)
        header_layout.addWidget(self.last_3months_btn)
        
        header_layout.addStretch()
        
        layout.addWidget(header_frame)
        
        # Create tab widget for different analytics views
        self.tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self.create_overview_tab()
        self.tab_widget.addTab(self.overview_tab, "Overview")
        
        # Trends tab
        self.trends_tab = self.create_trends_tab()
        self.tab_widget.addTab(self.trends_tab, "Trends")
        
        # Meals tab
        self.meals_tab = self.create_meals_tab()
        self.tab_widget.addTab(self.meals_tab, "Meals")
        
        layout.addWidget(self.tab_widget)
        
    def create_overview_tab(self):
        """Create the overview tab with summary statistics."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Summary cards
        cards_layout = QGridLayout()
        
        # Total calories card
        self.total_calories_card = self.create_summary_card(
            "Total Calories", "0", "#2E86AB"
        )
        cards_layout.addWidget(self.total_calories_card, 0, 0)
        
        # Average daily calories card
        self.avg_calories_card = self.create_summary_card(
            "Avg Daily Calories", "0", "#27AE60"
        )
        cards_layout.addWidget(self.avg_calories_card, 0, 1)
        
        # Highest day card
        self.highest_day_card = self.create_summary_card(
            "Highest Day", "0", "#E74C3C"
        )
        cards_layout.addWidget(self.highest_day_card, 0, 2)
        
        # Lowest day card
        self.lowest_day_card = self.create_summary_card(
            "Lowest Day", "0", "#F39C12"
        )
        cards_layout.addWidget(self.lowest_day_card, 0, 3)
        
        layout.addLayout(cards_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        
        # Daily calories chart
        self.daily_calories_chart = self.create_daily_calories_chart()
        charts_layout.addWidget(self.daily_calories_chart)
        
        # Macro distribution pie chart
        self.macro_chart = self.create_macro_distribution_chart()
        charts_layout.addWidget(self.macro_chart)
        
        layout.addLayout(charts_layout)
        
        return tab
        
    def create_trends_tab(self):
        """Create the trends tab with line charts."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Weekly average chart
        self.weekly_avg_chart = self.create_weekly_average_chart()
        layout.addWidget(self.weekly_avg_chart)
        
        return tab
        
    def create_meals_tab(self):
        """Create the meals tab with meal frequency analysis."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Most consumed meals chart
        self.popular_meals_chart = self.create_popular_meals_chart()
        layout.addWidget(self.popular_meals_chart)
        
        return tab
        
    def create_summary_card(self, title: str, value: str, color: str) -> QFrame:
        """Create a summary card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
        
    def create_daily_calories_chart(self) -> QChartView:
        """Create daily calories bar chart."""
        chart = QChart()
        chart.setTitle("Daily Calories")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create bar series
        series = QBarSeries()
        bar_set = QBarSet("Calories")
        
        # This will be populated with actual data
        bar_set.append([0] * 30)  # Placeholder
        series.append(bar_set)
        chart.addSeries(series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Days")
        axis_x.setRange(1, 30)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Calories")
        axis_y.setRange(0, 3000)
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
        
    def create_macro_distribution_chart(self) -> QChartView:
        """Create macro distribution pie chart."""
        chart = QChart()
        chart.setTitle("Macro Distribution")
        
        series = QPieSeries()
        series.append("Protein", 30)
        series.append("Carbs", 50)
        series.append("Fat", 20)
        
        # Customize slices
        for slice in series.slices():
            slice.setLabelVisible(True)
            slice.setLabelFormat("{label}: {percentage:.1f}%")
            
        chart.addSeries(series)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
        
    def create_weekly_average_chart(self) -> QChartView:
        """Create weekly average line chart."""
        chart = QChart()
        chart.setTitle("Weekly Average Calories")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create line series
        series = QLineSeries()
        series.setName("Weekly Average")
        
        # This will be populated with actual data
        for i in range(4):
            series.append(i, 2000 + (i * 100))
            
        chart.addSeries(series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Weeks")
        axis_x.setRange(0, 4)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Calories")
        axis_y.setRange(0, 3000)
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
        
    def create_popular_meals_chart(self) -> QChartView:
        """Create popular meals bar chart."""
        chart = QChart()
        chart.setTitle("Most Consumed Meals")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        
        # Create bar series
        series = QBarSeries()
        bar_set = QBarSet("Frequency")
        
        # This will be populated with actual data
        bar_set.append([5, 4, 3, 2, 1])  # Placeholder
        series.append(bar_set)
        chart.addSeries(series)
        
        # Create axes
        axis_x = QValueAxis()
        axis_x.setTitleText("Meals")
        axis_x.setRange(0, 5)
        
        axis_y = QValueAxis()
        axis_y.setTitleText("Times Consumed")
        axis_y.setRange(0, 10)
        
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        series.attachAxis(axis_x)
        series.attachAxis(axis_y)
        
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        return chart_view
        
    def set_last_week(self):
        """Set date range to last week."""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-7)
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        
    def set_last_month(self):
        """Set date range to last month."""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-30)
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        
    def set_last_3months(self):
        """Set date range to last 3 months."""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-90)
        self.start_date.setDate(start_date)
        self.end_date.setDate(end_date)
        
    def load_analytics(self):
        """Load analytics data for the selected date range."""
        try:
            start_date = self.start_date.date().toString("yyyy-MM-dd")
            end_date = self.end_date.date().toString("yyyy-MM-dd")
            
            # Get analytics data from database
            data = self.db_manager.get_analytics_data(start_date, end_date)
            
            # Update summary cards
            self.update_summary_cards(data)
            
            # Update charts
            self.update_daily_calories_chart(data['daily_data'])
            self.update_popular_meals_chart(data['meal_frequency'])
            
        except Exception as e:
            logger.error(f"Failed to load analytics: {e}")
            
    def update_summary_cards(self, data: Dict):
        """Update summary cards with data."""
        daily_data = data.get('daily_data', [])
        
        if not daily_data:
            return
            
        # Calculate statistics
        total_calories = sum(day['calories'] for day in daily_data)
        avg_calories = total_calories / len(daily_data) if daily_data else 0
        highest_day = max(daily_data, key=lambda x: x['calories'])['calories'] if daily_data else 0
        lowest_day = min(daily_data, key=lambda x: x['calories'])['calories'] if daily_data else 0
        
        # Update cards
        self.total_calories_card.findChild(QLabel, "value").setText(f"{total_calories:.0f}")
        self.avg_calories_card.findChild(QLabel, "value").setText(f"{avg_calories:.0f}")
        self.highest_day_card.findChild(QLabel, "value").setText(f"{highest_day:.0f}")
        self.lowest_day_card.findChild(QLabel, "value").setText(f"{lowest_day:.0f}")
        
    def update_daily_calories_chart(self, daily_data: List[Dict]):
        """Update daily calories chart with data."""
        # This would update the bar chart with actual data
        # Implementation depends on the specific chart library being used
        pass
        
    def update_popular_meals_chart(self, meal_frequency: List[Dict]):
        """Update popular meals chart with data."""
        # This would update the bar chart with actual meal frequency data
        # Implementation depends on the specific chart library being used
        pass
