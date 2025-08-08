import React from "react";

const Badge = (props) => {
    const getStatusStyle = (status) => {
        switch (status) {
            case "Pending": return 'bg-red-500 text-white';
            case "Confirm": return 'bg-yellow-500 text-white';
            case "Processing": return 'bg-blue-500 text-white';
            case "Shipped": return 'bg-purple-500 text-white';
            case "Delivered": return 'bg-green-700 text-white';
            case "Cancelled": return 'bg-gray-500 text-white';
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