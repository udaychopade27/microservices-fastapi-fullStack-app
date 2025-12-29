import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './auth/AuthContext';
import ProtectedRoute from './auth/ProtectedRoute';

import DashboardLayout from './components/layout/DashboardLayout';

import Login from './features/auth/Login';
import Signup from './features/auth/Signup';

import ProductCatalog from './features/products/ProductCatalog';
import Cart from './features/cart/Cart';
import Checkout from './features/orders/Checkout';
import MyOrders from './features/orders/MyOrders';
import Receipt from './features/orders/Receipt';

import Inventory from './features/owner/Inventory';
import AllOrders from './features/owner/AllOrders';

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        {/* PUBLIC */}
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />

        {/* ROOT */}
        <Route path="/" element={<Navigate to="/products" replace />} />

        {/* CLIENT */}
        <Route
          path="/products"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <ProductCatalog />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/cart"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <Cart />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/checkout"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <Checkout />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/orders"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <MyOrders />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/receipt/:id"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <Receipt />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        {/* OWNER */}
        <Route
          path="/inventory"
          element={
            <ProtectedRoute role="OWNER">
              <DashboardLayout>
                <Inventory />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/all-orders"
          element={
            <ProtectedRoute role="OWNER">
              <DashboardLayout>
                <AllOrders />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        {/* FALLBACK */}
        <Route path="*" element={<Navigate to="/products" replace />} />
      </Routes>
    </AuthProvider>
  );
}
