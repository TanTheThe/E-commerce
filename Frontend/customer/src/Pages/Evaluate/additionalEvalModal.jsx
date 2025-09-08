import { FiX } from 'react-icons/fi';

const AdditionalEvaluateModal = ({ isOpen, onClose, selectedVariant, onSubmit, additionalForm, setAdditionalForm }) => {
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

        const base64 = await convertToBase64(file);
        const imageData = {
            file: file,
            url: URL.createObjectURL(file),
            name: file.name,
            base64
        };

        setAdditionalForm(prev => ({ ...prev, additional_image: imageData }));
    };

    const removeImage = () => {
        if (additionalForm.additional_image && additionalForm.additional_image.url) {
            URL.revokeObjectURL(additionalForm.additional_image.url);
        }
        setAdditionalForm(prev => ({ ...prev, additional_image: null }));
    };

    const handleSubmit = () => {
        onSubmit();
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            style={{ backdropFilter: 'blur(2px)', backgroundColor: 'rgba(0, 0, 0, 0.4)' }}>
            <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-gray-800">Bổ sung đánh giá</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
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
                            <>
                                <input
                                    type="file"
                                    accept="image/*"
                                    onChange={handleImageUpload}
                                    className="hidden"
                                    id="additional-image-upload"
                                />
                                <label
                                    htmlFor="additional-image-upload"
                                    className="w-full px-4 py-6 border-2 border-dashed border-gray-300 rounded-lg text-center cursor-pointer hover:border-blue-400 hover:bg-blue-50 transition-colors block"
                                >
                                    <div className="flex flex-col items-center">
                                        <FaCloudUploadAlt className="text-2xl text-gray-400 mb-2" />
                                        <p className="text-sm font-medium text-gray-700">Nhấp để chọn ảnh</p>
                                        <p className="text-xs text-gray-500">Hỗ trợ định dạng JPG, PNG</p>
                                    </div>
                                </label>
                            </>
                        ) : (
                            <div className="relative group">
                                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden max-w-32">
                                    <img
                                        src={additionalForm.additional_image.url}
                                        alt={additionalForm.additional_image.name}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <button
                                    type="button"
                                    onClick={removeImage}
                                    className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs opacity-0 group-hover:opacity-100 transition-opacity"
                                >
                                    <IoMdClose />
                                </button>
                                <p className="text-xs text-gray-500 mt-1 truncate">{additionalForm.additional_image.name}</p>
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex gap-3 mt-6">
                    <button
                        onClick={onClose}
                        className="flex-1 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                        Hủy
                    </button>
                    <button
                        onClick={handleSubmit}
                        className="flex-1 py-2 bg-[#ff5252] text-white rounded-lg hover:bg-[#e53e3e] transition-colors"
                    >
                        Gửi bổ sung
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AdditionalEvaluateModal;