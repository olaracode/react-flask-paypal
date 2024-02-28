import React, { useContext } from "react";
import { Context } from "../store/appContext";
import rigoImageUrl from "../../img/rigo-baby.jpg";
import "../../styles/home.css";
import { PayPalScriptProvider, PayPalButtons } from "@paypal/react-paypal-js";
export const Home = () => {
  const { store, actions } = useContext(Context);
  console.log(process.env.PAYPAL_CLIENT);
  const createOrder = async () => {
    const response = await fetch(store.apiUrl + "/api/create_order", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        items: [
          {
            name: "Acrilyc mani",
            price: 25,
            quantity: 1,
          },
          {
            name: "Pedicure",
            price: 50,
            quantity: 1,
          },
        ],
      }),
    });
    if (response.ok) {
      const data = await response.json();
      return data.order_id;
    }
  };
  return (
    <div className="text-center mt-5">
      <h1>PAYPAL Integration</h1>
      <p>
        <img src={rigoImageUrl} />
      </p>
      <div className="alert alert-info">
        {store.message ||
          "Loading message from the backend (make sure your python backend is running)..."}
      </div>
      <PayPalScriptProvider options={{ clientId: process.env.PAYPAL_CLIENT }}>
        <PayPalButtons createOrder={createOrder} />
      </PayPalScriptProvider>
    </div>
  );
};
