# Calorie Tracker Pro - PyQt6 Version

A modern, feature-rich calorie tracking application built with PyQt6, offering significant improvements over the original Tkinter version.

## 🚀 Key Improvements

### **Modern UI/UX**
- **PyQt6 Interface**: Professional, native-looking interface
- **Modern Styling**: CSS-like theming with custom colors and animations
- **Responsive Design**: Better scaling and window management
- **Tabbed Interface**: Organized features in separate tabs

### **Enhanced Features**
- **Advanced Meal Management**: Search, filter, edit, duplicate meals
- **Macro Tracking**: Protein, carbs, fat, fiber, sugar, sodium
- **Data Analytics**: Charts, trends, and statistics
- **Export/Import**: Backup and share your data
- **Better Database**: Improved error handling and performance

### **Security & Configuration**
- **Environment Variables**: Secure credential management
- **Better Error Handling**: Comprehensive logging and user feedback
- **Database Optimization**: Indexes and connection pooling

## 📦 Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup Environment**:
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env with your database credentials
   DB_HOST=localhost
   DB_NAME=calorie_tracker_db
   DB_USER=postgres
   DB_PASSWORD=your_password_here
   DB_PORT=5432
   ```

3. **Run the Application**:
   ```bash
   python main_pyqt.py
   ```

## 🎯 Features

### **Daily Tracking**
- **Time-based Sections**: Breakfast, Lunch, Dinner, Snacks
- **Smart Search**: Type-ahead meal search with 3+ characters
- **Real-time Calculations**: Automatic calorie and macro calculations
- **Quantity Tracking**: Track amounts in grams with automatic scaling

### **Meal Management**
- **Comprehensive Database**: Store meals with full nutritional information
- **Search & Filter**: Find meals by name or nutritional criteria
- **Edit/Delete**: Full CRUD operations for meal management
- **Duplicate Meals**: Easy meal copying for variations

### **Analytics & Insights**
- **Daily Overview**: Summary cards with key statistics
- **Trend Analysis**: Weekly and monthly calorie trends
- **Popular Meals**: Most frequently consumed foods
- **Macro Distribution**: Visual breakdown of macronutrients

### **Data Management**
- **Export Data**: Save to CSV or JSON format
- **Import Data**: Restore from backup files
- **Date Navigation**: Easy date selection with quick buttons
- **Persistent Storage**: All data saved to PostgreSQL

## 🏗️ Architecture

### **File Structure**
```
calorie-calculator/
├── main_pyqt.py              # Main PyQt6 application
├── database_improved.py      # Enhanced database manager
├── meal_manager.py           # Meal management dialogs
├── meal_section_widget.py    # Individual meal section widgets
├── analytics_widget.py       # Analytics and charts
├── config.py                 # Configuration management
├── requirements.txt          # Python dependencies
└── env_example.txt          # Environment variables template
```

### **Key Components**

1. **ModernCalorieTracker**: Main application window
2. **DatabaseManager**: Enhanced database operations
3. **MealManagerDialog**: Advanced meal management
4. **MealSectionWidget**: Time-based meal tracking
5. **AnalyticsWidget**: Data visualization and insights

## 🎨 UI Improvements

### **Modern Design Elements**
- **Color Scheme**: Professional blue/green theme
- **Typography**: Clean, readable fonts
- **Spacing**: Proper padding and margins
- **Animations**: Smooth transitions and hover effects

### **Enhanced User Experience**
- **Intuitive Navigation**: Clear menu structure
- **Quick Actions**: One-click date selection
- **Visual Feedback**: Progress bars and status indicators
- **Error Handling**: User-friendly error messages

## 📊 Database Schema

### **Enhanced Tables**
- **meals**: Extended with macro nutrients
- **daily_calories**: Tracks daily totals with macros
- **daily_meals**: Individual meal entries with full nutrition
- **user_goals**: Personal goal tracking

### **Performance Optimizations**
- **Indexes**: Optimized queries for better performance
- **Connection Pooling**: Efficient database connections
- **Batch Operations**: Reduced database round trips

## 🔧 Configuration

### **Environment Variables**
```env
DB_HOST=localhost
DB_NAME=calorie_tracker_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

### **App Settings**
- Window size and positioning
- Theme colors and styling
- Default values and limits

## 🚀 Usage

### **Getting Started**
1. Launch the application
2. Select a date using the date picker
3. Add meals to different time sections
4. View analytics in the Analytics tab
5. Manage meals using the Manage Meals button

### **Adding Meals**
1. Click "Add Meal" in any section
2. Search for existing meals or type new ones
3. Enter quantity in grams
4. Calories and macros calculate automatically

### **Managing Meals**
1. Click "Manage Meals" button
2. Browse, search, and filter meals
3. Edit, delete, or duplicate meals
4. Import/export meal data

## 🔄 Migration from Tkinter Version

### **Data Migration**
The new version uses the same database schema with enhancements, so your existing data will be preserved and enhanced with new features.

### **Feature Comparison**
| Feature | Tkinter Version | PyQt6 Version |
|---------|----------------|---------------|
| UI Framework | Basic Tkinter | Modern PyQt6 |
| Styling | Limited | CSS-like theming |
| Charts | None | Built-in charts |
| Search | Basic | Advanced with filters |
| Macros | Calories only | Full nutrition |
| Export | None | CSV/JSON export |
| Analytics | None | Comprehensive |

## 🐛 Troubleshooting

### **Common Issues**
1. **Database Connection**: Check PostgreSQL is running and credentials are correct
2. **Missing Dependencies**: Run `pip install -r requirements.txt`
3. **Permission Errors**: Ensure database user has proper permissions

### **Logging**
The application includes comprehensive logging. Check console output for detailed error information.

## 🔮 Future Enhancements

- **Mobile App**: React Native or Flutter companion
- **Cloud Sync**: Multi-device synchronization
- **Recipe Integration**: Meal planning and recipes
- **Social Features**: Sharing and community
- **AI Recommendations**: Smart meal suggestions

## 📝 License

This project is open source. Feel free to modify and distribute according to your needs.

---

**Note**: This PyQt6 version represents a complete modernization of the original Tkinter application, offering professional-grade features and user experience while maintaining compatibility with existing data.
