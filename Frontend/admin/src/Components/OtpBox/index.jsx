import React, { useState } from "react";

const OtpBox = ({ length, onChange }) => {
    const [otp, setOtp] = useState(new Array(length).fill(""))

    const handleChange = (element, index) => {
        const value = element.value;
        if (isNaN(value)) return;

        const newOtp = [...otp];
        newOtp[index] = value;
        setOtp(newOtp);

        onChange && onChange(newOtp.join(""));

        if (value && index < length - 1) {
            document.getElementById(`otp-input-${index + 1}`).focus();
        }
    }

    const handleKeyDown = (event, index) => {
        if (event.key === "Backspace") {
            if (otp[index]) {
                const newOtp = [...otp];
                newOtp[index] = "";
                setOtp(newOtp);
                onChange && onChange(newOtp.join(""));
            } else if (index > 0) {
                document.getElementById(`otp-input-${index - 1}`).focus();
            }
        }
    };

    const handlePaste = (e) => {
        const pasteData = e.clipboardData.getData("Text").slice(0, length);
        if (!/^\d+$/.test(pasteData)) return;

        const newOtp = pasteData.split("");
        while (newOtp.length < length) newOtp.push("");
        setOtp(newOtp);
        onChange && onChange(newOtp.join(""));
    };

    return (
        <div style={{ display: "flex", gap: "5px", justifyContent: "center" }} className="otpBox">
            {otp.map((data, index) => (
                <input
                    key={index}
                    id={`otp-input-${index}`}
                    type="text"
                    maxLength="1"
                    value={otp[index]}
                    onChange={(e) => handleChange(e.target, index)}
                    onKeyDown={(e) => handleKeyDown(e, index)}
                    onPaste={handlePaste}
                    style={{
                        width: "45px",
                        height: "45px",
                        textAlign: "center",
                        fontSize: "17px",
                    }}
                />
            ))}
        </div>
    )
}

export default OtpBox