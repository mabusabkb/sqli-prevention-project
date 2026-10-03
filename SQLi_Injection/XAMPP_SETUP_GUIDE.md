# 🚀 XAMPP Setup Guide - Complete Instructions

## What is XAMPP?

XAMPP is a free, easy-to-install package that includes:
- **Apache** - Web server (runs your PHP application)
- **MySQL** - Database server (stores your data)
- **PHP** - Programming language (runs your code)
- **phpMyAdmin** - Database management tool (web interface)

---

## Step-by-Step XAMPP Installation

### Step 1: Download XAMPP

1. **Open your web browser**
2. **Go to**: https://www.apachefriends.org/
3. **Click** the big download button for Windows
4. **Choose** the latest version (PHP 7.4 or higher recommended)
5. **Save** the installer file (e.g., `xampp-windows-x64-8.2.12-0-VS16-installer.exe`)

**Download size**: ~150 MB
**Time**: 2-5 minutes (depending on internet speed)

---

### Step 2: Run the Installer

1. **Locate** the downloaded file (usually in Downloads folder)
2. **Double-click** the installer file
3. **If Windows asks** "Do you want to allow this app to make changes?" → Click **Yes**

---

### Step 3: Installation Wizard

#### Screen 1: Warning about UAC
- If you see a warning about User Account Control (UAC)
- Click **OK** to continue
- (This is normal, just a warning)

#### Screen 2: Welcome
- Click **Next**

#### Screen 3: Select Components
- **Keep all checkboxes selected** (default)
- You need at least:
  - ✅ Apache
  - ✅ MySQL
  - ✅ PHP
  - ✅ phpMyAdmin
- Click **Next**

#### Screen 4: Installation Folder
- **Default**: `C:\xampp`
- **Recommended**: Keep the default
- Click **Next**

#### Screen 5: Language
- Select **English**
- Click **Next**

#### Screen 6: Ready to Install
- Click **Next**
- Installation will begin (takes 2-5 minutes)

#### Screen 7: Completing Setup
- **Uncheck** "Do you want to start the Control Panel now?" (we'll do it manually)
- Click **Finish**

---

### Step 4: Start XAMPP Control Panel

1. **Open Start Menu**
2. **Search for**: "XAMPP Control Panel"
3. **Click** on "XAMPP Control Panel"
4. **If Windows asks** for permission → Click **Yes**

**Alternative**: Go to `C:\xampp\` and double-click `xampp-control.exe`

---

### Step 5: Start Apache and MySQL

In the XAMPP Control Panel:

1. **Find the "Apache" row**
   - Click the **Start** button next to Apache
   - Wait for it to turn **green** and say "Running"
   - Port numbers should show: 80, 443

2. **Find the "MySQL" row**
   - Click the **Start** button next to MySQL
   - Wait for it to turn **green** and say "Running"
   - Port number should show: 3306

**What you should see:**
```
Module    | Status  | Ports
----------|---------|-------------
Apache    | Running | 80, 443
MySQL     | Running | 3306
```

---

### Step 6: Verify Apache is Working

1. **Open your web browser**
2. **Go to**: http://localhost/
3. **You should see**: XAMPP welcome page with orange/yellow design

**If you see the XAMPP page** → ✅ Apache is working!

---

### Step 7: Verify MySQL is Working

1. **Open your web browser**
2. **Go to**: http://localhost/phpmyadmin
3. **You should see**: phpMyAdmin interface (database management tool)

**If you see phpMyAdmin** → ✅ MySQL is working!

---

### Step 8: Import Your Database

Now that XAMPP is running, import your project database:

1. **In phpMyAdmin** (http://localhost/phpmyadmin)
2. **Click** the "Import" tab at the top
3. **Click** "Choose File" button
4. **Navigate to**: `SQLi_Injection/Database/127_0_0_1.sql`
5. **Select** the file
6. **Click** "Go" button at the bottom
7. **Wait** for "Import has been successfully finished" message

**Verify:**
- Click "Databases" in the left sidebar
- You should see **"user_db"** in the list
- Click on "user_db"
- You should see **"users"** table
- Click on "users"
- You should see 2 rows (admin and shashank)

---

### Step 9: Copy Your Project to htdocs

1. **Open File Explorer**
2. **Navigate to**: `C:\xampp\htdocs\`
3. **Copy** your entire `SQLi_Injection` folder into this directory
4. **Final path should be**: `C:\xampp\htdocs\SQLi_Injection\`

**Verify:**
- Open browser: http://localhost/SQLi_Injection/index.html
- You should see your login page!

---

### Step 10: Run Password Migration

1. **Open Command Prompt**
   - Press `Windows + R`
   - Type: `cmd`
   - Press Enter

2. **Navigate to your project:**
   ```bash
   cd C:\xampp\htdocs\SQLi_Injection
   ```

3. **Run migration script:**
   ```bash
   php migrate_passwords.php
   ```

4. **Expected output:**
   ```
   ✓ Database connection established
   User #1 (admin): Password hashed successfully - MIGRATED
   User #2 (shashank): Password hashed successfully - MIGRATED
   ✓ SUCCESS: All plain text passwords have been migrated to bcrypt hashes.
   ```

---

### Step 11: Test Your Application

1. **Open browser**: http://localhost/SQLi_Injection/index.html
2. **You should see**: Login page
3. **Enter credentials:**
   - Username: `admin`
   - Password: `admin123`
4. **Click**: "login" button
5. **You should be redirected to**: admin_page.html

**✅ SUCCESS! Your application is now fully functional!**

---

## Troubleshooting

### Problem: Apache won't start (Port 80 in use)

**Cause**: Another program is using port 80 (often Skype or IIS)

**Solution 1 - Stop the conflicting program:**
1. Open Task Manager (Ctrl + Shift + Esc)
2. Look for "Skype" or "World Wide Web Publishing Service"
3. Right-click → End Task
4. Try starting Apache again

**Solution 2 - Change Apache port:**
1. In XAMPP Control Panel, click "Config" next to Apache
2. Select "httpd.conf"
3. Find line: `Listen 80`
4. Change to: `Listen 8080`
5. Find line: `ServerName localhost:80`
6. Change to: `ServerName localhost:8080`
7. Save and close
8. Start Apache
9. Access via: http://localhost:8080/

---

### Problem: MySQL won't start (Port 3306 in use)

**Cause**: Another MySQL service is running

**Solution:**
1. Open Services (Windows + R, type `services.msc`)
2. Look for "MySQL" or "MySQL80"
3. Right-click → Stop
4. Try starting MySQL in XAMPP again

---

### Problem: "Access forbidden" when opening localhost

**Solution:**
1. Check if Apache is running (green in XAMPP)
2. Try: http://localhost/dashboard/
3. If still not working, restart Apache

---

### Problem: phpMyAdmin shows error

**Solution:**
1. Make sure MySQL is running (green in XAMPP)
2. Wait 10 seconds after starting MySQL
3. Refresh the page
4. If still not working, restart MySQL

---

### Problem: Can't find XAMPP Control Panel

**Solution:**
1. Go to: `C:\xampp\`
2. Double-click: `xampp-control.exe`
3. Create a shortcut on desktop for easy access

---

### Problem: Database import fails

**Solution:**
1. Make sure MySQL is running
2. Check file size isn't too large (should be fine for this project)
3. Try importing again
4. If still fails, check the error message

---

## XAMPP Control Panel Tips

### Starting XAMPP Automatically

To make Apache and MySQL start automatically when Windows starts:

1. In XAMPP Control Panel
2. Click "Config" (top right)
3. Check "Apache" and "MySQL" under "Autostart of modules"
4. Click "Save"

### Stopping Services

To stop Apache or MySQL:
1. Click the "Stop" button next to the service
2. Wait for it to turn gray

### Checking Logs

If something goes wrong:
1. Click "Logs" button next to the service
2. View error messages
3. Use for troubleshooting

---

## Security Notes

**IMPORTANT**: XAMPP is for development only, not production!

Default XAMPP settings:
- MySQL root user has **no password** (empty password)
- This is fine for local development
- **Never use XAMPP for production websites**

For this project:
- We use `root` user with empty password
- This is configured in `connect.php`
- It's safe because it's only accessible from your computer

---

## Quick Reference

### XAMPP Locations
```
Installation:     C:\xampp\
Control Panel:    C:\xampp\xampp-control.exe
htdocs folder:    C:\xampp\htdocs\
Apache config:    C:\xampp\apache\conf\httpd.conf
MySQL data:       C:\xampp\mysql\data\
PHP config:       C:\xampp\php\php.ini
```

### Important URLs
```
XAMPP Dashboard:  http://localhost/
phpMyAdmin:       http://localhost/phpmyadmin
Your Project:     http://localhost/SQLi_Injection/index.html
```

### Default Credentials
```
MySQL:
  Username: root
  Password: (empty - no password)

Your Application:
  Username: admin
  Password: admin123
```

---

## Next Steps After XAMPP Setup

Once XAMPP is running and database is imported:

1. ✅ XAMPP installed and running
2. ✅ Database imported
3. ✅ Project copied to htdocs
4. ✅ Migration script run
5. ✅ Application accessible in browser

**Next:**
- Test the application thoroughly
- (Optional) Install Composer and run tests
- Read the documentation to understand the code

---

## Summary Checklist

- [ ] Downloaded XAMPP from apachefriends.org
- [ ] Installed XAMPP to C:\xampp
- [ ] Started XAMPP Control Panel
- [ ] Started Apache (green, running)
- [ ] Started MySQL (green, running)
- [ ] Verified Apache: http://localhost/
- [ ] Verified MySQL: http://localhost/phpmyadmin
- [ ] Imported database: Database/127_0_0_1.sql
- [ ] Copied project to: C:\xampp\htdocs\SQLi_Injection\
- [ ] Ran migration: php migrate_passwords.php
- [ ] Tested application: http://localhost/SQLi_Injection/index.html
- [ ] Logged in successfully with admin/admin123

**If all checked** → ✅ **Setup Complete!**

---

## Need More Help?

- **XAMPP Documentation**: https://www.apachefriends.org/faq_windows.html
- **Video Tutorials**: Search YouTube for "How to install XAMPP"
- **Project Documentation**: Read COMPLETE_SETUP.md in your project folder

---

**Time Required**: 15-30 minutes total
**Difficulty**: Easy (just follow the steps!)
**Result**: Fully working web server and database! 🚀

---

Good luck! Follow each step carefully and you'll have XAMPP running in no time!

````