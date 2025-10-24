import { FiX } from 'react-icons/fi';
import { MyContext } from "../../App";
import { useContext, useEffect } from 'react';
import { FaCloudUploadAlt } from 'react-icons/fa';
import { LazyLoadImage } from 'react-lazy-load-image-component';
import { IoMdClose } from 'react-icons/io';

const AdditionalEvaluateModal = ({ isOpen, onClose, selectedVariant, onSubmit, additionalForm, setAdditionalForm }) => {
    const context = useContext(MyContext);

    if (!isOpen) return null;

    const convertToBase64 = (file) => {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => resolve(reader.result);
            reader.onerror = error => reject(error);
        });
    };

    const handleImageUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const previewUrl = URL.createObjectURL(file);

            const base64 = await convertToBase64(file);

            const imageData = {
                file: file,
                url: previewUrl,
                name: file.name,
                base64
            };

            setAdditionalForm(prev => ({ ...prev, additional_image: imageData }));
        } catch (error) {
            console.error("Error uploading image:", error);
            if (context?.openAlertBox) {
                context.openAlertBox("error", "Có lỗi xảy ra trong quá trình upload ảnh");
            }
        }
    };

    const removeImage = () => {
        if (additionalForm.additional_image?.url) {
            URL.revokeObjectURL(additionalForm.additional_image.url);
        }
        setAdditionalForm(prev => ({ ...prev, additional_image: null }));
    };

    const handleSubmit = () => {
        if (!additionalForm.additional_comment?.trim()) {
            if (context?.openAlertBox) {
                context.openAlertBox("error", "Vui lòng nhập nhận xét bổ sung!");
            }
            return;
        }

        onSubmit();
    };

    const handleClose = () => {
        if (additionalForm.additional_image?.url) {
            URL.revokeObjectURL(additionalForm.additional_image.url);
        }
        onClose();
    };

    useEffect(() => {
        return () => {
            if (additionalForm.additional_image?.url) {
                URL.revokeObjectURL(additionalForm.additional_image.url);
            }
        };
    }, [additionalForm.additional_image]);

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.4)' }}>
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Bổ sung đánh giá</h3>
                    <button onClick={handleClose} className="text-gray-500 hover:text-gray-700 cursor-pointer">
                        <FiX className="text-xl" />
                    </button>
                </div>

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nhận xét bổ sung</label>
                        <textarea
                            value={additionalForm.additional_comment}
                            onChange={(e) => setAdditionalForm(prev => ({ ...prev, additional_comment: e.target.value }))}
                            className="w-full p-3 border border-gray-300 rounded-lg resize-none"
                            rows="4"
                            placeholder="Thêm nhận xét bổ sung về sản phẩm..."
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Hình ảnh bổ sung (tùy chọn)
                        </label>

                        {!additionalForm.additional_image ? (
                            <div className="border-dashed border-2 border-gray-300 h-[150px] flex items-center justify-center bg-gray-100 rounded relative hover:border-blue-400 hover:bg-blue-50 transition-colors">
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    className="absolute inset-0 opacity-0 z-10 cursor-pointer"
                                    id="additional-image-upload"
                                />
                                <label htmlFor="additional-image-upload" className="text-center text-gray-500 cursor-pointer">
                                    <FaCloudUploadAlt className="mx-auto mb-2 text-2xl" />
                                    <p className="text-sm font-medium">Nhấp để chọn ảnh</p>
                                    <p className="text-xs">Hỗ trợ định dạng JPG, PNG</p>
                                </label>
                            </div>
                        ) : (
                            <div className="relative w-full h-[150px] border rounded overflow-hidden">
                                <LazyLoadImage
                                    src={additionalForm.additional_image.url}
                                    alt={additionalForm.additional_image.name}
                                    className="object-cover w-full h-full"
                                    effect="blur"
                                />
                                <span
                                    onClick={removeImage}
                                    className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center cursor-pointer hover:bg-red-700 transition-colors"
                                >
                                    <IoMdClose />
                                </span>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <button
                        onClick={onClose}
                        className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                    >
                        Hủy
                    </button>
                    <button
                        onClick={handleSubmit}
                        className="flex-1 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors cursor-pointer"
                    >
                        Gửi bổ sung
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdditionalEvaluateModal;