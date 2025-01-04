import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "payment_value": "sum"
    })
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count"
    }, inplace=True)
    return daily_orders_df

#demografi customer
def create_custate_df(df):
    custate_df = df.groupby(by="customer_state").customer_id.nunique().reset_index()
    custate_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    custate_df=custate_df.sort_values(by="customer_count", ascending=False)
    return custate_df

#demografi seller
def create_sellstate_df(df):
    sellstate_df = df.groupby(by="seller_state").seller_id.nunique().reset_index()
    sellstate_df.rename(columns={
        "seller_id": "seller_count"
    }, inplace=True)
    sellstate_df=sellstate_df.sort_values(by="seller_count", ascending=False)
    return sellstate_df

#payment method
def create_paymethod_df(df):
    paymethod_df = df.groupby(by="payment_type").order_id.count().reset_index()
    paymethod_df.rename(columns={"order_id":"order_count"}, inplace=True)
    return paymethod_df

#payment value
def create_payvalue_df(df):
    payvalue_df = df.groupby(by="payment_type").payment_value.sum().reset_index()
    return payvalue_df

#cancellation
def create_cancellation_df(df):
    canceled_df = df[df['order_status'] == 'canceled']
    daily_cancel_df = canceled_df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique"
    }, inplace=True)
    daily_cancel_df = daily_cancel_df.reset_index()
    daily_cancel_df.rename(columns={
        "order_id": "cancel_count"
    }, inplace=True)
    return daily_cancel_df

#load data
all_df = pd.read_csv("dashboard/all_data.csv")
paydate_df = pd.read_csv("dashboard/paym_date.csv")
seller_df = pd.read_csv("dashboard/seller_database.csv")

#all_df datetime
datetime_alldf = ["order_purchase_timestamp"]
all_df.sort_values(by="order_purchase_timestamp", inplace=True)
all_df.reset_index(inplace=True)
for column in datetime_alldf:
    all_df[column]=pd.to_datetime(all_df[column])

#paydate_df datetime
datetime_paydatedf = ["order_purchase_timestamp"]
paydate_df.sort_values(by="order_purchase_timestamp", inplace=True)
paydate_df.reset_index(inplace=True)
for column in datetime_paydatedf:
    paydate_df[column]=pd.to_datetime(paydate_df[column])

#header dashboard
st.header('Brazilian E-Commerce Dashboard \U0001F6D2')

#Membuat komponen filter
min_date = min(all_df["order_purchase_timestamp"].min(), paydate_df["order_purchase_timestamp"].min())
max_date = max(all_df["order_purchase_timestamp"].max(), paydate_df["order_purchase_timestamp"].max())

# Mengambil start_date & end_date dari date_input
start_date, end_date = st.date_input(
    label='Rentang Waktu',
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

#Filter data
filter_all = all_df[
    (all_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (all_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]
filter_paym = paydate_df[
    (paydate_df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (paydate_df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
]

daily_orders_df = create_daily_orders_df(filter_all)
custate_df = create_custate_df(filter_all)
sellstate_df = create_sellstate_df(seller_df)
paymethod_df = create_paymethod_df(filter_paym)
payvalue_df = create_payvalue_df(filter_paym)
daily_cancel_df = create_cancellation_df(filter_all)

st.subheader('E-commerce Performance Overview')
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col2:
    total_revenue = format_currency(daily_orders_df.payment_value.sum(), "BRL", locale='pt_BR')
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16,8))
ax.plot(
    daily_orders_df["order_purchase_timestamp"],
    daily_orders_df["order_count"],
    marker='o',
    linewidth=2,
    color="#1f1f8c"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)

st.subheader("Demographics Overview")
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 15))
colors = ["#1f1f8c","#3b4ab7","#5572e0","#7a96ff","#a1c1ff"]
sns.barplot(x="customer_count", y="customer_state", data=custate_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Customer", fontsize=30)
ax[0].set_title("Customer State", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)
#st.pyplot(fig)

sns.barplot(x="seller_count", y="seller_state", data=sellstate_df.head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Seller", fontsize=30)
ax[1].set_title("Seller State", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=30)
st.pyplot(fig)

st.subheader("Payment Insight")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#1f1f8c","#3b4ab7","#5572e0","#7a96ff","#a1c1ff"]
    sns.barplot(
        y="order_count", 
        x="payment_type",
        data=paymethod_df.sort_values(by="order_count", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Total Order by Payment Type", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)
 
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    colors = ["#1f1f8c","#3b4ab7","#5572e0","#7a96ff","#a1c1ff"]
    sns.barplot(
        y="payment_value", 
        x="payment_type",
        data=payvalue_df.sort_values(by="payment_value", ascending=False),
        palette=colors,
        ax=ax
    )
    ax.set_title("Revenue Each Payment Type", loc="center", fontsize=50)
    ax.set_ylabel(None)
    ax.set_xlabel(None)
    ax.tick_params(axis='x', labelsize=35)
    ax.tick_params(axis='y', labelsize=30)
    st.pyplot(fig)

st.subheader("Cancellation Trends")
fig, ax = plt.subplots(figsize=(16,8))
ax.plot(
    daily_cancel_df["order_purchase_timestamp"],
    daily_cancel_df["cancel_count"],
    marker='o',
    linewidth=2,
    color="#B71A1A"
)
ax.set_title("Cancellation Trends Over Time", loc="center", fontsize=30)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)
