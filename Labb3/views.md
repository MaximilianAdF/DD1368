# Views in Databases: Benefits and Differences

### 1. When Would a View Be Beneficial Compared to Regular Queries?  
Views are beneficial when:  
- **Simplifying Complex Queries:** They encapsulate complex SQL logic, allowing users to retrieve data without re-writing complex queries.  
- **Reusability:** They provide a reusable abstraction for frequently used queries.  
- **Security:** Views can restrict access to specific columns or rows, providing a controlled way to expose data.  
- **Maintenance:** They reduce the risk of introducing errors by centralizing query logic.  

---

### 2. What is Stored in the Database for Non-Materialized and Materialized Views?  
- **Non-Materialized Views:**  
  - Only the **SQL query definition** is stored. The result set is dynamically generated every time the view is queried.  

- **Materialized Views:**  
  - Both the **query definition** and the **result set** are stored in the database. The result set is updated periodically or manually.  

---

### 3. Benefit of Using Materialized Views Over Non-Materialized Views  
- **Performance:** Materialized views provide faster query responses since the data is precomputed and stored, reducing computation time during queries.  

---

### 4. Benefit of Using Non-Materialized Views Over Materialized Views  
- **Freshness of Data:** Non-materialized views always reflect the latest data from the base tables, eliminating the need for manual or scheduled updates.  
