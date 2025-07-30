# Welcome to the `mkdocs-mermaid-zoom` Demo!

This page demonstrates the functionality of the `mkdocs-mermaid-zoom` plugin.

Click on the diagram below to see the lightbox in action. Once the lightbox is open, you can:

- **Zoom** with your mouse wheel.
- **Pan** by clicking and dragging the diagram.

---

## Simple Flowchart

```mermaid
graph TD
    A[Start] --> B{Is it working?};
    B -- Yes --> C[Great!];
    B -- No --> D[Check the console];
    C --> E[End];
    D --> E[End];
``` 

---

## E-Commerce System Class Diagram

```mermaid
classDiagram
    class User {
        +login()
        +logout()
        +updateProfile()
        +getOrderHistory()
    }
    
    class Customer {
        +addPaymentMethod()
        +removePaymentMethod()
        +placeOrder()
    }
    
    class Admin {
        +manageProducts()
        +viewAllOrders()
        +manageUsers()
        +generateReports()
    }
    
    class Product {
        +updateStock()
        +updatePrice()
        +setDiscount()
    }
    
    class Order {
        +calculateTotal()
        +updateStatus()
        +cancelOrder()
        +getOrderDetails()
    }
    
    class OrderItem {
        +calculateSubtotal()
        +updateQuantity()
    }
    
    class ShoppingCart {
        +addItem()
        +removeItem()
        +clearCart()
        +calculateTotal()
    }
    
    class Payment {
        +processPayment()
        +refund()
        +getPaymentDetails()
    }

    User <|-- Customer
    User <|-- Admin
    Customer --> Order
    Order --> OrderItem
    Product --> OrderItem
    Customer --> ShoppingCart
    ShoppingCart --> OrderItem
    Order --> Payment
``` 

---

## User Authentication Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant A as Auth Service
    participant D as Database
    participant C as Cache

    U->>F: Enter credentials
    F->>A: POST /login
    A->>D: Validate user
    D-->>A: User data
    A->>C: Store session
    C-->>A: Session ID
    A-->>F: JWT Token + Session ID
    F->>F: Store token in localStorage
    F-->>U: Redirect to dashboard
    
    Note over U,C: User is now authenticated
    
    U->>F: Access protected resource
    F->>A: GET /api/data (with JWT)
    A->>C: Validate session
    C-->>A: Session valid
    A->>D: Fetch user data
    D-->>A: Data
    A-->>F: Protected data
    F-->>U: Display content
``` 