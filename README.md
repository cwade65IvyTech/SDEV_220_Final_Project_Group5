# Varners Greenhouse & Nursery Inventory System
## This is the repository for the Varners Greenhouse & Nursery inventory system during the Fall Wholesale Program. This program allows customers to purchase plants and other agricultural products. It displays the products as well as their prices. Then, the customer can input the quantity for each product to calculate their overall price, depending on sales tax and pickup/delivery.
### SetUp + Installation Steps:
1. Clone the github Repository:
   ```bash
   git clone https://github.com/your-name/SDEV_220_Final_Project_Group5.git
2. Enter the Project Folder:
   ```bash
   cd your-folder-name
3. 
### How to Use/Test:
How to Use/Test:
Make sure Python 3 it’s installed on your system. (Tip: It may be useful to verify the version is 3.6)
Save the script as varners_order_form.py (Or the name of your choosing).
Open a terminal or open a prompt.
You can run the script by using; python varners_order_form.py (Or the name of your choosing). 
A window should open. 
### Feature Summary:
Summary:
This application is a desktop-based wholesale order form designed for Varner’s Greenhouse & Nursery’s 2025 Fall season. It offers dynamic data entry with real-time calculation of totals, including support for Michigan sales tax and optional delivery fees. The interference is responsive and scrollable, allowing for easy navigation of product sections. Input fields are color coded for clarity, and the form includes built-in validation to ensure numeric input. Users can export orders as CSV files or printable text summaries, making it easy to process or archive orders. The application is designed with compatibility in mind, supporting both legacy and modern versions of python ‘trace’ methods for live updates.
### Technology Stack:
Technology Stack:
Programming Language: Python 3
GUI Framework: Tkinter 
Core library used:
Tkinter, tkinter.ttk
Datetime
Csv
collections.OrderedDict
Sys, os
File Outputs:
.csv
.txt
### Team Roles:
 - Calvin Ryan Alexander Wade was the project leader who led conversations and focused on the structure and organization of the program.
 - Jason P Winowiecki was the developer who focused on the structure and organization of the program.
 - Sahara Smith created the documentation, provided feedback on the structure and organization of the program, and initiated collaboration between team members.
 - Kimberly Quintero created the documentation for the program and offered help throughout the project.
 - Feda Rahman Bigzad did the testing, debugging, desk checking, and revising of the program to ensure that the code ran smoothly.


### Screenshots or Demo:

### Comments for Complex Sections:
The more complex sections of the code are carefully documented online, especially those that handle dynamic behaviors such as the use of ‘trace_add’ for live updating totals. The ‘MoneyVar’ class abstracts currency formatting while keeping the underlying float value accessible for calculations. Within ‘build_table’, nested functions are used to safely bind real time UI updates to entry fields that involve closures and compatibility handling for both ‘trace_add’ (Python 3.6+) and legacy ‘trace’. The ‘recompute_totals()’ function is another key section that performs conditional logic for tax calculations, delivery fees, and total updates. Additionally, layout logic ensures that the product list resizes with the window and remains scrollable, which is achieved by dynamically binding the canvas size to its frame contents. These areas are commented to clarify purpose and structure, aiding readability and future maintenance.
### requirements.txt

### Class Diagram Overview:

