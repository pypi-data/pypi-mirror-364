
# 🚀 Robot Framework Retry Debugger

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)](https://www.python.org/)
[![Robot Framework](https://img.shields.io/badge/Robot%20Framework-6.1.1+-green.svg)](https://robotframework.org/)

A modern **GUI-based debugging tool** for **Robot Framework**, designed to **pause test execution** when a keyword fails, allowing you to **retry, skip, or run custom keywords interactively**.

Supports both **SeleniumLibrary** and **AppiumLibrary**, making it ideal for **UI testing**.

---

## ✨ Key Features

### **🔍 Failure Debugging GUI**
- **Automatic GUI Launch:** Appears when a keyword fails.
- **Failure Info Panel:**
  - Displays **failed keyword name** and **arguments**.
  - Shows the **failure message** and **call stack** (color-coded and neatly formatted).
  - Lets you **edit arguments** for a retry.

---

### **🔄 Retry & Skip Options**
- **Retry and Continue:** Retry the failed keyword with modified arguments.
  - Disables buttons during retry to prevent accidental multiple clicks.
- **Skip and Continue:** Skip the failed keyword and resume the test.
- **Skip Test:** Skip the rest of the test case.
- **Abort Suite:** Stop the entire test suite execution.

---

### **⚡ Custom Keyword Executor**
- **Run Any Keyword:** Execute any keyword from available libraries (`BuiltIn`, `SeleniumLibrary`, etc.).
- **Library & Keyword Dropdowns:** Dynamically loaded libraries with documentation and signatures.
- **Arguments Editor:** Add, edit, or remove arguments before execution.
- **Inline Documentation:** See keyword parameters and docstrings instantly.
- **Isolated Logs:** Results appear in the log window **without modifying the Retry tab**.

---

### **📦 Variable Inspector**
- **Live Variable Browser:** View all Robot Framework variables (`${}`, `@{}`, `&{}`).
- **Search and Filter:** Quickly find variables.
- **Set Variable:** Create or modify variables during test execution.

---

### **🎨 Color-Coded Logs**
- **Failures:** Red  
- **Success:** Green  
- **Call Stack:** Orange with proper indentation and wrapping for long text.

---

### **🛡 Thread-Safe GUI**
- Background threads keep the GUI **responsive**.
- **Safe updates** using `after_idle()` to avoid threading issues.

---

## 📋 Requirements
- **Python 3.10+**
- **Robot Framework 7.1.1+**
- **Tkinter** (included in most Python installations)
- **SeleniumLibrary** / **AppiumLibrary** (optional but recommended)

---

## ⚙️ Installation & Usage

### **Option 1: Add Listener in Settings**
Add `RobotRetrier` as a listener in your Robot Framework test suite:
```robotframework
*** Settings ***
Library    SeleniumLibrary
Listener   RobotRetrier.py
```

Then run your tests:
```bash
robot tests/
```

### **Option 2: Use --listener Command-Line Option**
You can also specify the listener directly when running tests:
```bash
robot --listener RobotRetrier.py tests/
```
This will automatically start the GUI debugger on failures.

---

## 📈 Future Improvements
- Advanced **call stack tree visualization**.
- **Dark/Light themes**.
- **Retry history persistence**.


