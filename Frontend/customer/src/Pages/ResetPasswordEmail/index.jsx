// src/pages/ResetPasswordEmail.tsx
import React, { useContext, useState } from "react";
import { postDataApi } from "../../utils/api";
import { MyContext } from "../../App";
import { CircularProgress } from "@mui/material";

const ResetPasswordEmail = () => {
    const [email, setEmail] = useState("");
    const context = useContext(MyContext)
    const [isLoading, setIsLoading] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!email) {
            context.openAlertBox("error", "Please enter email");
            return;
        }

        setIsLoading(true)

        const response = await postDataApi("/customer/auth/forgot-password", {
            email,
            check: "email"
        });

        if (response?.success === true) {
            context.openAlertBox(
                "success", "Please visit your email to receive the link"
            )
        } else {
            context.openAlertBox("error", response?.data?.detail?.message)
        }

        setIsLoading(false);
    };

    return (
        <div className="min-h-120 bg-gray-100 flex flex-col items-center justify-center px-4">
            <h1 className="text-3xl font-bold mb-4">Reset Your Password</h1>
            <p className="text-gray-700 mb-6 text-center max-w-md">
                Lost your password? Please enter your email address. You will receive a link to create a new password via email.
            </p>
            <form onSubmit={handleSubmit} className="w-full max-w-md">
                <label htmlFor="email" className="block mb-2 font-medium text-sm">
                    Email *
                </label>
                <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full p-2 border border-gray-300 rounded mb-4 bg-white"
                />
                <button
                    type="submit"
                    disabled={!email || isLoading}
                    className={`w-full flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded transition hover:bg-blue-700 ${(!email || isLoading) ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
                >
                    {isLoading ? <CircularProgress size={24} color="inherit" /> : "RESET PASSWORD"}
                </button>
            </form>
        </div>
    );
};

export default ResetPasswordEmail;
