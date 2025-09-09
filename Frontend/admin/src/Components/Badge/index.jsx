import React from "react";

const Badge = (props) => {
    const getStatusStyle = (status) => {
        switch (status) {
            case "pending": return 'bg-red-500 text-white';
            case "confirmed": return 'bg-yellow-500 text-white';
            case "shipping": return 'bg-purple-500 text-white';
            case "delivered": return 'bg-green-700 text-white';
            case "cancelled": return 'bg-gray-500 text-white';
            default: return 'bg-gray-400 text-white';
        }
    };

    return (
        <span className={`inline-block py-1 px-3 rounded-full text-xs font-medium capitalize ${getStatusStyle(props.status)}`}>
            {props.status}
        </span>
    );
};

export default Badge