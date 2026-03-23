# **Smart Support Desk – README (Short Version)**

## 📌 What is this?

**Smart Support Desk** is an internal support tool for a SaaS company where:

* **Support Agents** can:

  * Create and manage customers
  * Create and manage tickets
  * View their own ticket summary dashboard

* **Admins / Team Leads** can:

  * View and manage all customers and tickets
  * See an overall system-wide dashboard

The frontend is built in **Streamlit**, and the backend is a **Flask API** with **MySQL** as the database.

---

## 🛠️ Tech Stack

* **Frontend:** Streamlit
* **Backend:** Flask
* **Database:** MySQL
* **Caching:** Redis
* **Validation:** Pydantic
* **Auth:** JWT
* **API Docs:** Swagger / OpenAPI

---

## ✅ Features

### Customers

* Create, update, delete, and view customers
* Agents see only their own customers
* Admins see all customers

### Tickets

* Create, update, delete, and view tickets
* Each ticket is linked to a customer
* Tickets have priority and status

### Dashboard

* Shows:

  * Total tickets
  * Tickets by status
  * Tickets by priority
  * Top customers
* **Role-based view:**

  * Agents → only their data
  * Admins → overall summary

---

## 🚀 How to Run Locally

### 1️⃣ Start Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend runs at: `http://127.0.0.1:5000`

### 2️⃣ Start Redis

```bash
redis-server
```

### 3️⃣ Start Streamlit

```bash
cd frontend
streamlit run streamlit_app.py
```

Frontend opens at: `http://localhost:8501`

---

## 📄 API Docs

Once backend is running, access Swagger at:

```
http://127.0.0.1:5000/swagger
```

---

## 🔐 Authentication

* Users log in with email & password
* JWT token is used for secure access
* Role-based access control: **AGENT / ADMIN / TEAM_LEAD**

---

## 📂 High-Level Structure

```
Smart-Support-Desk/
├── backend/
│   ├── app.py
│   ├── routes/
│   ├── models/
│   ├── db.py
│   └── redis_client.py
│
├── frontend/
│   ├── streamlit_app.py
│   └── pages/
│       ├── dashboard.py
│       ├── customers.py
│       └── tickets.py
│
└── README.md
```

---

## 🚀 Future Improvements

* Pagination for tickets/customers
* Email notifications for new tickets
* Activity logs for auditing
