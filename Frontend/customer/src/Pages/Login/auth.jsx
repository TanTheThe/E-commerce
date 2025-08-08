import { useEffect, useState } from "react";
import { fetchWithAutoRefresh } from "../../utils/api";

const useAuth = () => {
    const [isLogin, setIsLogin] = useState(false);
    const [userData, setUserData] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    const checkLogin = async () => {
        setIsLoading(true);
        const token = localStorage.getItem("accesstoken");

        if (token) {
            const response = await fetchWithAutoRefresh("/customer/user", "GET");
            console.log(response);

            if (response?.success) {
                setIsLogin(true);
                setUserData(response.data);
            } else {
                setIsLogin(false);
                setUserData(null);
                localStorage.removeItem("accesstoken");
                localStorage.removeItem("refreshtoken");
            }
        } else {
            setIsLogin(false);
            setUserData(null);
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
        isLoading,
        checkLogin
    };
};

export default useAuth