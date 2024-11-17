# **Yatrue Maps Backend**

This creates a RESTful backend using **FastAPI** and **MongoDB** with the **Motor** driver for asynchronous operations.

---

## **Getting Started**

Follow these steps to set up and run the project.

### **Prerequisites**

- Python 3.8+
- MongoDB installed and running locally or on the cloud.

---

### **1. Clone the Repository**

```bash
git clone https://github.com/Neural-Pirates/YaTrue-Maps.git
cd YaTrue-Maps
```

### \*\*2. Create a Virtual Environment

It’s recommended to use a virtual environment to manage dependencies.

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### **3. Install Dependencies**

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### **4. Run the server**

```bash
uvicorn main:app --reload
```

Open your browser and navigate to http://127.0.0.1:8000/docs to access the Swagger UI.
