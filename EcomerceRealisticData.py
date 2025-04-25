
# ================================= Import Libraries =================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import numpy as np

# ================================= STEP 1: Data Exploration & Cleaning =================================

# Load the dataset
file_path = "dataset.csv"  # Your uploaded file
df = pd.read_csv(file_path, encoding="ISO-8859-1")  # Encoding helps avoid character errors

# Display the first 5 rows of the dataset
print(df.head())

print()

# Get dataset information
df.info()

# Check for missing values
print(df.isnull().sum())

# Fill missing descriptions with the most common one per StockCode
df["Description"] = df.groupby("StockCode")["Description"].transform(lambda x: x.fillna(x.mode()[0]) if not x.mode().empty else "Unknown")

# Fill missing CustomerID properly
df["CustomerID"] = df["CustomerID"].fillna(999999)  # Corrected without inplace=True

# Check for missing values AGAIN
print(df.isnull().sum())

# Convert data types (Object to Datetime format)
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

df.info()  # Check if InvoiceDate is now datetime64

print("Duplicate Rows Before Removal:", df.duplicated().sum())
df.drop_duplicates(inplace=True) # Removing duplicates
print("Duplicate Rows After Removal:", df.duplicated().sum())

# ================================= STEP 2: Monthly Sales Revenue Trends =================================

# Extract Year & Month
df["YearMonth"] = df["InvoiceDate"].dt.to_period("M")  # YYYY-MM format

# Calculate Monthly Revenue
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
monthly_revenue = df.groupby("YearMonth")["Revenue"].sum().reset_index()

monthly_revenue["YearMonth"] = monthly_revenue["YearMonth"].astype(str)


# Visualize Monthly Revenue Trends
plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_revenue, x="YearMonth", y="Revenue", marker="o", linewidth=2, color="royalblue")
plt.xticks(rotation=45)
plt.title("Monthly Sales Revenue Trends", fontsize=14)
plt.xlabel("Month", fontsize=12)
plt.ylabel("Total Revenue", fontsize=12)
plt.grid(True)
plt.show()

# ================================= STEP 3: Identify Top 5 Best-Selling Products =================================

# Group Data by Description and Sum Total Quantity Sold
top_products = df.groupby("Description")["Quantity"].sum().reset_index()
top_products = top_products.sort_values(by="Quantity", ascending=False).head(5)

# Visualize Top 5 Best-Selling Products Using a Bar Chart
plt.figure(figsize=(10,5))
sns.barplot(data=top_products, x="Quantity", y="Description", hue="Description", palette="Blues_r", legend=False)
plt.xlabel("Total Quantity Sold")
plt.ylabel("Product Description")
plt.title("Top 5 Best-Selling Products")
plt.show()

# ================================= STEP 4: Customer Segmentation =================================


# Calculate Total Spending per Customer (Total Spending = Quantity × Unit Price)
df["Total_Spending"] = df["Quantity"] * df["UnitPrice"]
customer_spending = df.groupby("CustomerID")["Total_Spending"].sum().reset_index()

# Reshape the spending data for clustering
X = customer_spending["Total_Spending"].values.reshape(-1, 1)

# Apply K-Means Clustering
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
customer_spending["Cluster"] = kmeans.fit_predict(X)

# Determine spending tiers correctly
cluster_means = customer_spending.groupby("Cluster")["Total_Spending"].mean().sort_values()

# Assign labels based on spending amounts
spending_labels = {
    cluster_means.index[0]: "Low",
    cluster_means.index[1]: "Medium",
    cluster_means.index[2]: "High"
}
customer_spending["Spending_Tier"] = customer_spending["Cluster"].map(spending_labels)

# Visualize Customer Segments
plt.figure(figsize=(8, 5))
sns.countplot(data=customer_spending, x="Spending_Tier", hue="Spending_Tier", palette="coolwarm", legend=False)

plt.title("Customer Segmentation Based on Spending Habits")
plt.xlabel("Spending Tier")
plt.ylabel("Number of Customers")
plt.show()

# Display the count of each segment
print(customer_spending["Spending_Tier"].value_counts())


# ================================= STEP 5: Actionable Insights & Recommendations =================================

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Ensure date column is in proper datetime format
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

df["YearMonth"] = df["InvoiceDate"].dt.strftime("%Y-%m")  # Convert to 'YYYY-MM' string format

# Identify Seasonal Trends in Sales
monthly_sales = df.groupby("YearMonth")["Total_Spending"].sum().reset_index()

plt.figure(figsize=(12, 6))
sns.lineplot(data=monthly_sales, x="YearMonth", y="Total_Spending", marker="o", color="b")
plt.xticks(rotation=45)
plt.title("Monthly Sales Trend")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.grid(True)
plt.show()

# Identify Underperforming Products
product_sales = df.groupby("Description")["Total_Spending"].sum().reset_index()
low_performing_products = product_sales.nsmallest(10, "Total_Spending")  # Bottom 10 products

plt.figure(figsize=(10, 6))
sns.barplot(
    data=low_performing_products, x="Total_Spending", y="Description", hue="Description",  palette="Reds_r", legend=False)

plt.title("Bottom 10 Underperforming Products")
plt.xlabel("Total Revenue")
plt.ylabel("Product")
plt.show()