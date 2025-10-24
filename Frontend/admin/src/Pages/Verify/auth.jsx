import { useEffect, useState } from "react";
import { fetchWithAutoRefresh } from "../../utils/api";

const useAuth = () => {
    const [isLogin, setIsLogin] = useState(false);
    const [userData, setUserData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [userRole, setUserRole] = useState(null);

    const checkLogin = async () => {
        setIsLoading(true);
        const token = localStorage.getItem("accesstoken");

        if (token) {
            const response = await fetchWithAutoRefresh("/admin/user", "GET");

            if (response?.success) {
                setIsLogin(true);
                setUserData(response.data);
                setUserRole(response.data.role);
            } else {
                setIsLogin(false);
                setUserData(null);
                setUserRole(null);
                localStorage.removeItem("accesstoken");
                localStorage.removeItem("refreshtoken");
            }
        } else {
            setIsLogin(false);
            setUserData(null);
            setUserRole(null);
        }
        setIsLoading(false);
    };

    useEffect(() => {
        checkLogin();
    }, []);

    return {
        isLogin,
        setIsLogin,
        userData,
        setUserData,
        userRole,
        isLoading,
        checkLogin
    };
};

export default useAuth